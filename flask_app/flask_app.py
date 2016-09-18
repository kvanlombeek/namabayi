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
from sklearn.ensemble import RandomForestClassifier
import re
from sqlalchemy import create_engine
import psycopg2
from copy import deepcopy

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

	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	query = '''SELECT name
				FROM feedback 
				WHERE user_id = %(user_id)s
				AND feedback = 'like' '''
	params = {'user_id':user_ID}	
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values
	# Strange formating for vue.js array
	return_dict = []
	for index, name in enumerate(liked_names):
		return_dict.append({'name':name})
	return jsonify(liked_names = return_dict)

@app.route('/delete_name', methods=['GET'])
def delete_name():
	user_ID = request.args.get('user_ID')
	name = request.args.get('name').strip().title()
	# Update the table, change the feedback of the particular name to no_like
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	sql_cursor = sql_conn.cursor()
	query = '''UPDATE feedback 
					SET feedback = 'no_like' 
					WHERE name = %(name)s 
					AND user_id = %(user_id)s'''
	params = {'name':name, 'user_id':user_ID}
	sql_cursor.execute(query, params)
	sql_conn.commit()
	# Send back the liked names, a bit the same as request_liked_names
	query = '''SELECT name
				FROM feedback 
				WHERE user_id = %(user_id)s
				AND feedback = 'like'  '''
	params = {'user_id':user_ID}
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values
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
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	# First check if the name is not in there
	query = '''SELECT * FROM feedback WHERE name = %(name)s AND user_id = %(user_id)s'''
	params = {'name':name, 'user_id': user_ID}
	test = pd.read_sql(sql = query, con = sql_conn, params = params)
	# Hier zt een mini bug in, als de user eerst op niet like heeft geduwd, kan hij de naam niet meer toevoegen
	if(len(test>0)):
		print('name already added')
	else:
		query = '''INSERT INTO feedback 
				VALUES (%(feedback)s,%(name)s,%(session_id)s,%(time)s,%(user_id)s,%(sex)s)'''
		params={'feedback':'like',
					'name':name,
					'session_id':session_ID,
					'sex':sex,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'user_id':user_ID}
		sql_conn.execute(query, params)
		print('Naam is toegevoegd')
	# Send back the liked names, a bit the same as request_liked_names
	query = '''SELECT name
				FROM feedback 
				WHERE user_ID = %(user_id)s
				AND feedback = 'like' '''
	params = {'user_id':user_ID}
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).loc[:,'name'].values.tolist()
	liked_names.remove(name)
	liked_names.append([name])
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
	# Geocode IP adre
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
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	to_write_away = pd.DataFrame.from_dict([info_dict])
	to_write_away.to_sql(name=table_name,con = sql_conn, if_exists='append',index=False)
	return None	

@app.route('/return_vote', methods=['GET'])
def return_vote():
	print('in NEW return vote function')
	# Request parameters
	feedback = {'session_id':request.args.get('session_ID'),
				'user_id':request.args.get('user_ID'),
				'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
				'feedback':request.args.get('feedback'),
				'name':request.args.get('name'),
				'sex':request.args.get('sex')}
	print(feedback)
	write_dict_to_sql_usage(feedback, 'feedback')
	return jsonify(whatever = '')

@app.route('/get_stringer_suggestion', methods=['GET'])
def get_stringer_suggestion():
	# Request parameters
	how_many = int(request.args.get('how_many'))
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')
	requested_sex = request.args.get('requested_sex')
	# Check how many postive feedbacks the user already gave.
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	query = '''SELECT *
					FROM feedback
					WHERE user_id = %(user_id)s
					AND sex = %(sex)s '''
	params = {'user_id':user_ID, 'sex':requested_sex}
	names_feedback = pd.read_sql_query(sql = query, con = sql_conn, params=params)
	
	n_liked_names = len(names_feedback.loc[names_feedback['feedback'] == 'like',:])
	n_disliked_names = len(names_feedback.loc[names_feedback['feedback'] != 'like',:])
	print('User liked already %i names and disliked %i' %(n_liked_names, n_disliked_names))
	
	# Normal random suggestion
	if((n_liked_names < 5) | (n_disliked_names < 5) ):
		query = '''SELECT *
						FROM voornamen_pivot 
						WHERE sex = %(sex)s
						AND region = 'Belgie'
						AND name NOT IN (
							SELECT name 
							FROM feedback
							WHERE user_id = %(user_id)s)
						ORDER BY RANDOM() LIMIT 10'''
		params = {'sex':requested_sex,'user_id':user_ID}
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'name'].values[:how_many].tolist()
		print('Queried suggestion : %s and sex %s ' %(suggestion,requested_sex))
		return jsonify(names = suggestion, sex = requested_sex)

	# User liked already more than 10 names, train a model and get a scored suggestion
	if(n_liked_names >= 5):
		params = {'user_id':user_ID}
		all_names = pd.read_sql_query('''SELECT * FROM voornamen_pivot
											WHERE name IN (
												SELECT name 
												FROM feedback
												WHERE user_id = %(user_id)s
											)''', con = sql_conn, params=params)
		all_names = all_names.loc[all_names['sex'] == requested_sex,:]
		all_names = all_names.loc[all_names['region'] == 'Belgie',:]
		all_names = all_names.drop(['sex', 'region'], axis = 1)
		# Get previous user feedback 
		query = '''SELECT * FROM feedback WHERE user_id = %(user_id)s '''
		params = {'user_id':user_ID}
		user_feedback = pd.read_sql_query(sql = query, con = sql_conn, params=params)
		# Merge with features to make learning matrix
		learning_matrix = pd.merge(user_feedback, all_names, how = 'left', left_on = 'name', right_on = 'name')
		# Column selecton
		feature_names = ['score_original','score_vintage','score_classic','score_trend','score_popular','length']
		feature_names.extend([feature for feature in all_names.columns if (re.search('origin_', feature))])
		#The original undummified column was Origin feature, so drop it
		feature_names = [feature for feature in feature_names if feature != 'origin_feature']
		columns_needed = deepcopy(feature_names)
		columns_needed.extend(['feedback'])
		learning_matrix = learning_matrix[columns_needed]
		learning_matrix = learning_matrix.dropna()
		# Convert like into boolean
		learning_matrix['feedback'] = learning_matrix['feedback']=='like'
		learning_matrix['feedback'] = learning_matrix['feedback'].astype(float)
		target_name = 'feedback' 

		# Train model
		model = RandomForestClassifier(n_estimators=50, max_depth=5)
		model.fit(X = learning_matrix[feature_names], y = learning_matrix[target_name])
		importances = pd.Series(data = model.feature_importances_, index = feature_names)
		print(importances.sort_values(ascending=False))
		# Make a suggestion
		test_sample = pd.read_sql_query('''SELECT * FROM voornamen_pivot
											WHERE name NOT IN (
												SELECT name 
												FROM feedback
												WHERE user_id = %(user_id)s
											) ORDER BY RANDOM() LIMIT 500''', con = sql_conn, params=params)
		test_sample = test_sample.loc[test_sample['sex'] == requested_sex,:]
		test_sample = test_sample.loc[test_sample['region'] == 'Belgie',:]
		test_sample = test_sample.drop(['sex', 'region'], axis = 1)
		print('Shape test sample: %s' %str(test_sample.shape))
		test_sample = test_sample.loc[~test_sample['name'].isin(user_feedback['name'].values),:]
		print('Shape test sample: %s' %str(test_sample.shape))
		test_sample['prediction'] = model.predict(X = test_sample[feature_names])
		test_sample['prediction_proba'] = model.predict_proba(X = test_sample[feature_names])[:,1]
		test_sample = test_sample.sort_values(by = 'prediction_proba', axis=0, ascending=False)
		suggestion = test_sample['name'].values[:how_many].tolist()
		print('Queried suggestion : %s and sex %s ' %(suggestion,requested_sex))		
		return jsonify(names = suggestion, sex = requested_sex)

@app.route('/get_stats', methods=['GET'])
def get_stats():

	print('in get_stats function')
	
	# Request name info
	name_1 = request.args.get('name_1').strip().title()
	name_2 = request.args.get('name_2').strip().title()
	sex_name_1 = request.args.get('sex_name_1')
	sex_name_2 = request.args.get('sex_name_2')
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
					'sex_name_1':sex_name_1,
					'sex_name_2':sex_name_2}
	write_dict_to_sql_usage(lookup_info, 'name_lookups')

	# Connection to database
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	
	# Query name 1
	query = '''SELECT *
				FROM voornamen_pivot 
				WHERE name = %(name)s
				AND sex = %(sex)s
				AND region = %(region)s
				LIMIT 1'''
	params = {'name':name_1, 'sex':sex_name_1, 'region':region}
	try: 
		name_1_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[0,:]
		name_1_ts = name_1_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values
		name_1_meaning = name_1_kpis['meaning']
	except:
		name_1_kpis = pd.Series({'score_original':5.0,'score_vintage':0.0,'score_classic':0.0,'score_trend':0.0,'score_popular':0.0})
		name_1_ts = np.repeat(0, 20)
		name_1_meaning = 'Unknown'
	
	# Query name 2
	params = {'name':name_2, 'sex':sex_name_2, 'region':region}
	try: 
		name_2_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[0,:]
		name_2_ts = name_2_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values
		name_2_meaning = name_2_kpis['meaning']
	except:
		name_2_kpis = pd.Series({'score_original':5.0,'score_vintage':0.0,'score_classic':0.0,'score_trend':0.0,'score_popular':0.0})
		name_2_ts = np.repeat(0, 20)
		name_2_meaning = 'Unknown'

	return jsonify(score_original = {'name_1': np.round(name_1_kpis['score_original'],1),
									 'name_2': np.round(name_2_kpis['score_original'],1)},
					score_vintage = {'name_1': np.round(name_1_kpis['score_vintage'],1),
									 'name_2': np.round(name_2_kpis['score_vintage'],1)},
					score_classic = {'name_1': np.round(name_1_kpis['score_classic'],1),
									 'name_2': np.round(name_2_kpis['score_classic'],1)},
					score_trend   = {'name_1': np.round(name_1_kpis['score_trend'],1),
									 'name_2': np.round(name_2_kpis['score_trend'],1)},
					score_popular = {'name_1': np.round(name_1_kpis['score_popular'],1),
									 'name_2': np.round(name_2_kpis['score_popular'],1)},
					ts = {'name_1': name_1_ts.tolist(),
						  'name_2': name_2_ts.tolist()},
					meanings = {'name_1':name_1_meaning,
								'name_2':name_2_meaning})

@app.route('/')
def index():
	return redirect(url_for('static', filename='index.html'))

@app.route('/<path:javascript_file>')
def javascript():
	return redirect(url_for('static', filename=javascript_file))
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)




