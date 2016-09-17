# coding=utf-8

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
import pandas as pd
import numpy as np
import sqlite3
import datetime
import time
import math
import json
import sys
from base64 import b64encode
from sklearn.grid_search import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
import re
from sqlalchemy import create_engine
import psycopg2

sys.path.append('../')

app = Flask(__name__, static_url_path='')

@app.route('/request_user_ID', methods=['GET'])
def request_user_ID():
	user_ID = b64encode(os.urandom(24)).decode('utf-8')
	session_ID = b64encode(os.urandom(24)).decode('utf-8')
	# Create session info dict and store it
	session_info = {'session_ID':session_ID,
					'user_ID':user_ID,
					'ip_address' : request.remote_addr,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'user_agent':request.headers.get('User-Agent')}
	write_dict_to_sql_usage(session_info, 'sessions')
	return jsonify(user_ID = user_ID, session_ID = session_ID)

@app.route('/request_liked_names', methods=['GET'])
def request_liked_names():
	user_ID = request.args.get('user_ID')

	sql_conn = sqlite3.connect('data/analysed_data.sql')
	query = '''SELECT name
				FROM feedback 
				WHERE User_ID = ?
				AND feedback = "like" '''
	params = [user_ID]	
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values
	sql_conn.close()
	# Strange formating for vue.js array
	return_dict = []
	for index, name in enumerate(liked_names):
		return_dict.append({'name':name})
	return jsonify(liked_names = return_dict)

@app.route('/delete_name', methods=['GET'])
def delete_name():
	user_ID = request.args.get('user_ID')
	name = request.args.get('name')
	# Update the table, change the feedback of the particular name to no_like
	sql_conn = sqlite3.connect('data/analysed_data.sql')
	sql_cursor = sql_conn.cursor()
	query = '''UPDATE feedback 
					SET feedback = 'no_like' 
					WHERE name = ? 
					AND user_ID = ?'''
	params = [name.strip(), user_ID]	
	sql_cursor.execute(query, params)
	sql_conn.commit()
	# Send back the liked names, a bit the same as request_liked_names
	query = '''SELECT name
				FROM feedback 
				WHERE User_ID = ?
				AND feedback = "like"  '''
	params = [user_ID]	
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values
	sql_conn.close()
	# Strange formating for vue.js array
	return_dict = []
	for index, name in enumerate(liked_names):
		return_dict.append({'name':name})
	return jsonify(liked_names = return_dict)

@app.route('/add_name', methods=['GET'])
def add_name():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	name = request.args.get('name').title()
	sex = request.args.get('sex')
	print('User %s wants to add name : %s of sex %s' %(user_ID,name,sex) )
	# Update the table, change the feedback of the particular name to no_like
	sql_conn = sqlite3.connect('data/analysed_data.sql')
	sql_cursor = sql_conn.cursor()
	# First check if the name is not in there
	params = [name, user_ID]
	query = '''SELECT * FROM feedback WHERE name = ? AND user_ID = ?'''
	test = pd.read_sql(sql = query, con = sql_conn, params = params)
	# Hier zt een mini bug in, als de user eerst op niet like heeft geduwd, kan hij de naam niet meer toevoegen
	if(len(test>0)):
		print('name already added')
	else:
		query = '''INSERT INTO feedback 
				VALUES (?,?,?,?,?,?)'''
		params=['like',
					name,
					session_ID,
					datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					user_ID,
					sex]
		sql_cursor.execute(query, params)
		sql_conn.commit()
		print('Naam is toegevoegd')
	# Send back the liked names, a bit the same as request_liked_names
	query = '''SELECT name
				FROM feedback 
				WHERE User_ID = ?
				AND feedback = "like" '''
	params = [user_ID]	
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values.tolist()
	liked_names.remove(name)
	liked_names.append([name])
	sql_conn.close()
	# Strange formating for vue.js array
	return_dict = []
	for index, name in enumerate(liked_names):
		return_dict.append({'name':name})
	return jsonify(liked_names = return_dict)


@app.route('/create_session_ID', methods=['GET'])
def create_session_ID():
	user_ID = request.args.get('user_ID')
	window_width = request.args.get('window_width')
	window_height = request.args.get('window_height')
	session_ID = b64encode(os.urandom(24)).decode('utf-8')
	# Geocode IP adres
	#geolocator = GoogleV3()
	#try:
	#	location = geolocator.geocode(request.remote_addr)
	#except Exception as e:
	#	print(e)
	#	location = e
	#print(location)
	# Create session info dict and store it
	session_info = {'session_ID':session_ID,
					'user_ID':user_ID,
					'ip_address' : request.remote_addr,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'user_agent':request.headers.get('User-Agent'),
					'window_width':window_width,
					'window_height': window_height}
	write_dict_to_sql_usage(session_info, 'sessions')
	# Return session ID
	return jsonify(session_ID = session_ID)

def write_dict_to_sql_usage(info_dict, table_name):
	# Write in SQL table lookups
	sql_conn = sqlite3.connect('data/analysed_data.sql')
	to_write_away = pd.DataFrame.from_dict([info_dict])
	to_write_away.to_sql(name=table_name,con = sql_conn, if_exists='append',index=False)
	sql_conn.close()
	return None	

@app.route('/get_suggestion', methods=['GET'])
def get_suggestion():
	print('in get_suggestion function')
	# Request parameters
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')
	scores = json.loads(request.args.get('suggestion_scores'))
	requested_sex = request.args.get('requested_sex')
	feedback = request.args.get('feedback')
	feedback_name = request.args.get('previous_suggestion')
	feedback_sex = request.args.get('previous_suggestion_sex')
	print('Feedback: %s about name %s of sex %s' %(feedback, feedback_name, feedback_sex))
	# Is it the first suggestion? If so, the user did not set any parameters
	if(feedback=='suggestion_initialisation'):
		sql_conn = sqlite3.connect('data/analysed_data.sql')
		query = '''SELECT *
					FROM voornamen_pivot 
					WHERE Sex = "F"
					AND Region = "Belgie"
					AND Score_trend = 4
					ORDER BY RANDOM() LIMIT 1'''
		params = []	
		requested_sex = 'F'
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'Name'].values[0]
		print('Queried suggestion : %s and sex %s ' %(suggestion,requested_sex))
		sql_conn.close()
		return jsonify(name = suggestion, sex = requested_sex)
	# The user returned feedback, first store it
	sql_conn = sqlite3.connect('data/analysed_data.sql')
	feedback = {'session_ID':session_ID,
				'user_ID':user_ID,
				'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
				'feedback':feedback,
				'name':feedback_name,
				'sex':feedback_sex}
	write_dict_to_sql_usage(feedback, 'feedback')
	# Check how many postive feedbacks the user already gave.
	query = '''SELECT *
					FROM feedback
					WHERE user_ID = ?
					AND feedback = "like" '''
	params = [user_ID]
	n_liked_names = len(pd.read_sql_query(sql = query, con = sql_conn, params=params))
	print('User liked already %i names' %n_liked_names)
	#If the user has already ten liked names, do a RF suggestion, if not, random suggestion
	if(n_liked_names < 10):
		# Normal random suggestion
		query = '''SELECT *
					FROM voornamen_pivot 
					WHERE Sex = ?
					AND Score_original BETWEEN ? AND ?
					AND Score_classic BETWEEN ? AND ?
					AND Score_vintage BETWEEN ? AND ?
					AND Score_popular BETWEEN ? AND ?
					AND Score_trend BETWEEN ? AND ?
					AND Region = "Belgie" 
					AND Name NOT IN (
						SELECT name 
						FROM feedback
						WHERE user_ID = ?)
					ORDER BY RANDOM() LIMIT 1'''
		params = [requested_sex,scores['original']['min'],scores['original']['max'],
						1,scores['populair']['max'],
						scores['classic']['min'],scores['classic']['max'],
						scores['vintage']['min'],scores['vintage']['max'],
						scores['trending']['min'],scores['trending']['max'], user_ID]
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'Name'].values[0]
		print('Queried suggestion : %s and sex %s ' %(suggestion,requested_sex))
		sql_conn.close()
		return jsonify(name = suggestion, sex = requested_sex)
	# User liked already more than 10 names, train a model and get a scored suggestion
	if(n_liked_names >= 10):
		# First feature creation, this should really be in the app preparation
		all_names = pd.read_sql_query('''SELECT * FROM voornamen_pivot''', con = sql_conn)
		all_names = all_names[['Name', 'Score_original','Score_vintage', 'Score_classic','Score_trend', 'Score_popular', 'Sex', 'Region']]
		all_names = all_names.loc[all_names['Sex'] == requested_sex,:]
		all_names = all_names.loc[all_names['Region'] == 'Belgie',:]
		all_names = all_names.drop(['Sex', 'Region'], axis = 1)
		# # Last 3 letters dummified
		# all_names['last_3_letters'] = all_names['Name'].str[-3:]
		# common_last_three_letters = all_names['Name'].str[-3:].value_counts()[:20].index
		# all_names.loc[~all_names['last_3_letters'].isin(common_last_three_letters),'last_3_letters'] = 'not_common'
		# all_names = pd.concat([all_names, pd.get_dummies(all_names['last_3_letters'])], axis=1)
		# all_names = all_names.drop(['last_3_letters', 'not_common'], axis=1)
		# # Last 2 letters dummified
		# all_names['last_2_letters'] = all_names['Name'].str[-2:]
		# common_last_two_letters = all_names['Name'].str[-2:].value_counts()[:50].index
		# all_names.loc[~all_names['last_2_letters'].isin(common_last_two_letters),'last_2_letters'] = 'not_common'
		# all_names = pd.concat([all_names, pd.get_dummies(all_names['last_2_letters'])], axis=1)
		# all_names = all_names.drop(['last_2_letters', 'not_common'], axis=1)
		# # Special characters, like dash or accents
		# all_names['dash'] = all_names['Name'].str.contains('-')
		# all_names['é'] = all_names['Name'].str.contains('é')
		# all_names['è'] = all_names['Name'].str.contains('è')
		# all_names['ä'] = all_names['Name'].str.contains('ä')
		# all_names['ë'] = all_names['Name'].str.contains('ë')
		# all_names['ï'] = all_names['Name'].str.contains('ï')
		# all_names['ü'] = all_names['Name'].str.contains('ï')
		# all_names['ç'] = all_names['Name'].str.contains('ç')
		# Lengte
		all_names['length'] = all_names['Name'].str.len()
		# Get previous user feedback 
		query = '''SELECT * FROM feedback WHERE user_ID = ? '''
		params = [user_ID]
		user_feedback = pd.read_sql_query(sql = query, con = sql_conn, params=params)
		# Merge with features to make learning matrix
		learning_matrix = pd.merge(user_feedback, all_names, how = 'left', left_on = 'name', right_on = 'Name')
		learning_matrix = learning_matrix.dropna()
		learning_matrix['feedback'] = learning_matrix['feedback']=='like'
		learning_matrix['feedback'] = learning_matrix['feedback'].astype(float)
		# Define feature names and target variable for learning
		feature_names = ['Score_original','Score_vintage','Score_classic','Score_trend','Score_popular','length']
		# , 'dash','é','è','ä','ë','ï','ü','ç',
		#feature_names.extend(common_last_three_letters)
		#feature_names.extend(common_last_two_letters)
		target_name = 'feedback' 
		# Train model
		n_estimators = [50]
		max_depth = [2,4,6]
		model = RandomForestClassifier()
		clf = GridSearchCV(cv = 3, estimator=model, param_grid=dict(n_estimators=n_estimators,max_depth=max_depth), scoring='recall')
		clf.fit(learning_matrix[feature_names], learning_matrix[target_name])
		model = RandomForestClassifier(n_estimators=clf.best_estimator_.n_estimators, max_depth=clf.best_estimator_.max_depth)
		model.fit(X = learning_matrix[feature_names], y = learning_matrix[target_name])
		print('Best score = %f Max depth = %i , n estimators = %i' %(clf.best_score_, clf.best_estimator_.max_depth,clf.best_estimator_.n_estimators ))
		# Make a suggestion
		test_sample = all_names.sample(100).copy()
		print('Shape test sample: %s' %str(test_sample.shape))
		test_sample = test_sample.loc[~test_sample['Name'].isin(user_feedback['name'].values),:]
		print('Shape test sample: %s' %str(test_sample.shape))
		test_sample['prediction'] = clf.predict(X = test_sample[feature_names])
		test_sample['prediction_proba'] = clf.predict_proba(X = test_sample[feature_names])[:,1]
		test_sample = test_sample.sort_values(by = 'prediction_proba', axis=0, ascending=False)
		suggestion = test_sample['Name'].values[0]
		print('Queried suggestion : %s and sex %s ' %(suggestion,requested_sex))		
		return jsonify(name = suggestion, sex = requested_sex)

@app.route('/get_stats', methods=['GET'])
def get_stats():

	print('in get_stats function')
	
	# Request name info
	name_1 = request.args.get('name_1').strip().title()
	name_2 = request.args.get('name_2').strip().title()
	sex = request.args.get('sex')
	region = request.args.get('region')
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')

	# Store away Lookup info
	lookup_info = {'session_ID':session_ID,
					'user_ID':user_ID,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'name_1': name_1,
					'name_2': name_2,
					'region':region,
					'sex':sex}
	write_dict_to_sql_usage(lookup_info, 'name_lookups')

	# Connection to database
	sql_conn = sqlite3.connect('data/analysed_data.sql')
	
	# Query name 1
	query = '''SELECT *
				FROM voornamen_pivot 
				WHERE Name = ? 
				AND Sex = ?
				AND Region = ?
				LIMIT 1'''
	params = [name_1, sex, region]
	try: 
		name_1_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[0,:]
		name_1_ts = name_1_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values

	except:
		name_1_kpis = pd.Series({'Score_original':5.0,'Score_vintage':0.0,'Score_classic':0.0,'Score_trend':0.0,'Score_popular':0.0})
		name_1_ts = np.repeat(0, 20)
	# Query name 2
	query = '''SELECT *
				FROM voornamen_pivot 
				WHERE Name = ? 
				AND Sex = ?
				AND Region = ?
				LIMIT 1'''
	params = [name_2, sex, region]
	try: 
		name_2_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[0,:]
		name_2_ts = name_2_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values
	except:
		name_2_kpis = pd.Series({'Score_original':5.0,'Score_vintage':0.0,'Score_classic':0.0,'Score_trend':0.0,'Score_popular':0.0})
		name_2_ts = np.repeat(0, 20)
	# Close connection
	sql_conn.close()

	return jsonify(score_original = {'name_1': np.round(name_1_kpis['Score_original'],1),
									 'name_2': np.round(name_2_kpis['Score_original'],1)},
					score_vintage = {'name_1': np.round(name_1_kpis['Score_vintage'],1),
									 'name_2': np.round(name_2_kpis['Score_vintage'],1)},
					score_classic = {'name_1': np.round(name_1_kpis['Score_classic'],1),
									 'name_2': np.round(name_2_kpis['Score_classic'],1)},
					score_trend   = {'name_1': np.round(name_1_kpis['Score_trend'],1),
									 'name_2': np.round(name_2_kpis['Score_trend'],1)},
					score_popular = {'name_1': np.round(name_1_kpis['Score_popular'],1),
									 'name_2': np.round(name_2_kpis['Score_popular'],1)},
					ts = {'name_1': name_1_ts.tolist(),
						  'name_2': name_2_ts.tolist()})

@app.route('/')
def index():
	return redirect(url_for('static', filename='index.html'))

@app.route('/<path:javascript_file>')
def javascript():
	return redirect(url_for('static', filename=javascript_file))
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)




