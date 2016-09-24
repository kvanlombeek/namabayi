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
import re
from sqlalchemy import create_engine
import psycopg2
from copy import deepcopy
from naive_bayes_lib import drop_unwanted_columns, drop_columns_with_no_variation, \
                                drop_equal_columns, keep_only_interesting_origins, Naive_bayes_model


sys.path.append('../')

application = Flask(__name__, static_url_path='')

@application.route('/request_user_ID', methods=['GET'])
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

@application.route('/request_liked_names', methods=['GET'])
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

@application.route('/delete_name', methods=['GET'])
def delete_name():
	user_ID = request.args.get('user_ID')
	name = request.args.get('name').strip().title()
	# Update the table, change the feedback of the particular name to no_like
	sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('kasper', 'VosseM08'))
	query = '''UPDATE feedback 
					SET feedback = 'no_like' 
					WHERE name = %(name)s 
					AND user_id = %(user_id)s'''
	params = {'name':name, 'user_id':user_ID}
	sql_conn.execute(query, params)
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

@application.route('/add_name', methods=['GET'])
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


@application.route('/create_session_ID', methods=['GET'])
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

@application.route('/return_vote', methods=['GET'])
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

@application.route('/get_stringer_suggestion', methods=['GET'])
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
	#if((n_liked_names < 5) | (n_disliked_names < 5) ):
	if(n_liked_names <10 ):
		query = '''SELECT *
						FROM voornamen_pivot 
						WHERE sex = %(sex)s
						AND region = 'Belgie'
						AND score_popular > 2
						AND name NOT IN (
							SELECT name 
							FROM feedback
							WHERE user_id = %(user_id)s)
						ORDER BY RANDOM() LIMIT 10'''
		params = {'sex':requested_sex,'user_id':user_ID}
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'name'].values[:how_many].tolist()
		return jsonify(names = suggestion, sex = requested_sex)

	# User liked already more than 10 names, train a model and get a scored suggestion
	if(n_liked_names >= 10):
		params = {'user_id':user_ID, 'requested_sex':requested_sex}
		learning_matrix = pd.read_sql_query('''SELECT voornamen_pivot.*, feedback.feedback
                							FROM voornamen_pivot, feedback
							                	WHERE voornamen_pivot.name = feedback.name
							                	AND voornamen_pivot.region = 'Vlaanderen'
							                	AND voornamen_pivot.sex = feedback.sex
							                	AND feedback.user_id = %(user_id)s
							                	AND feedback.sex = %(requested_sex)s;''', con = sql_conn, params=params)
		learning_matrix['feedback'] = learning_matrix['feedback'] == 'like'
		learning_matrix['score_original'] = learning_matrix['score_original'].apply(lambda x: x if x != 0.5 else 0)
		learning_matrix = drop_unwanted_columns(learning_matrix)
		learning_matrix = drop_columns_with_no_variation(learning_matrix)
		learning_matrix = keep_only_interesting_origins(learning_matrix,5)
		learning_matrix = drop_equal_columns(learning_matrix)
		# Train
		features_and_types = {}
		for feature in learning_matrix.columns:
		    if(re.search('score_', feature)): features_and_types[feature]='int_bigger_than_zero'
		    if(re.search('origin_', feature)): features_and_types[feature]='bool'
		    if(feature == 'length'): features_and_types[feature]='normal'
		learning_matrix['feedback'] = learning_matrix['feedback'].apply(lambda x: 'like' if x else 'no_like')
		model = Naive_bayes_model()
		model.train(learning_matrix, features_and_types, 'feedback')
		learning_matrix['odds_ratio'] = model.predict(learning_matrix)

		# Original package or own model:
		model = Naive_bayes_model()
		model.train(learning_matrix, features_and_types, 'feedback')

		# Make a suggestion
		params = {'user_id':user_ID, 'requested_sex':requested_sex}
		test_sample = pd.read_sql_query('''SELECT * FROM voornamen_pivot
											WHERE sex = %(requested_sex)s
											AND region = 'Vlaanderen'
											AND name NOT IN (
												SELECT name 
												FROM feedback
												WHERE user_id = %(user_id)s
											) ORDER BY RANDOM() LIMIT 500''', con = sql_conn, params=params)
		test_sample = test_sample.drop(['sex', 'region'], axis = 1)
		test_sample['score_original'] = test_sample['score_original'].apply(lambda x: x if x != 0.5 else 0)
		test_sample['odds_ratio'] = model.predict(test_sample)
		test_sample = test_sample.sort_values(by = 'odds_ratio', axis=0, ascending=False)
		print('high scores names:')
		print(test_sample['name'].values[:10])
		print('low scores names:')
		print(test_sample['name'].values[-10:])		
		suggestion = test_sample['name'].values[:how_many].tolist()
		return jsonify(names = suggestion, sex = requested_sex)

@application.route('/get_stats', methods=['GET'])
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

@application.route('/')
def index():
	return redirect(url_for('static', filename='index.html'))

@application.route('/<path:javascript_file>')
def javascript():
	return redirect(url_for('static', filename=javascript_file))
	
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=True)




