# coding=utf-8
from __future__ import unicode_literals
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_predict, GridSearchCV, KFold
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
#from naive_bayes_lib import drop_unwanted_columns, drop_columns_with_no_variation, \
#                                drop_equal_columns, keep_only_interesting_origins, Naive_bayes_model


sys.path.append('../')

application = Flask(__name__, static_url_path='')

sql_conn = create_engine('postgresql://%s:%s@forespellpostgis.cusejoju89w7.eu-west-1.rds.amazonaws.com:5432/grb_2016_03' %('namabayi_dev', 'namabayi_dev_40'))

@application.route('/forespell')
def forespell():
	return redirect("https://www.forespell.com")

@application.route('/forespell_kasper')
def forespell_kasper():
	return redirect("https://www.forespell.com/resume/kasper/")

@application.route('/create_login', methods=['GET'])
def create_login():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	email = request.args.get('email').lower()
	password = generate_password_hash(request.args.get('password'))
	repeat_password = generate_password_hash(request.args.get('repeat_password'))
	
	# Check if user doesn't exist!
	params =  {'email':email}
	user_test = pd.read_sql(''' SELECT * FROM registered_users
										WHERE email = %(email)s''', sql_conn, params = params)
	if(len(user_test)>0):
		print('user already existed')
		return jsonify(logged_in = False, error = 'user already existed')
	user_information = {
		'user_id' : user_ID,
		'session_id' : session_ID,
		'email' : email,
		'password': password,
		'repeat_password' : repeat_password,
		'registration_time' : datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
	}
	write_dict_to_sql_usage(user_information, 'registered_users')
	return jsonify(logged_in = True, error = 'no_error')

@application.route('/login', methods=['GET'])
def login():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	email = request.args.get('email').lower()
	password = request.args.get('password')
	params = {'email':email, 'password':password}
	user_record = pd.read_sql(''' SELECT password, user_id FROM registered_users
										WHERE email = %(email)s''', sql_conn, params = params)
	if(len(user_record) == 0):
		error = 'Unknown user'
		logged_in = False
		return jsonify(logged_in = logged_in, user_ID = user_ID, error=error)
	password_test = check_password_hash(password = password, pwhash=user_record['password'][0])

	if(password_test):
		user_ID = user_record['user_id'][0]
		logged_in = True
		error = 'no_error'
	else: 
		error = 'Wrong password'
		logged_in = False
	return jsonify(logged_in = logged_in, user_ID = user_ID, error=error)

def write_dict_to_sql_usage(info_dict, table_name):
	# Write in SQL table lookups
	to_write_away = pd.DataFrame.from_dict([info_dict])
	to_write_away.to_sql(name=table_name,con = sql_conn, if_exists='append',index=False)
	return None	

@application.route('/request_user_ID', methods=['GET'])
def request_user_ID():
	user_ID = b64encode(os.urandom(24)).decode('utf-8')
	session_ID = b64encode(os.urandom(24)).decode('utf-8')
	window_width = request.args.get('window_width')
	window_height = request.args.get('window_height')
	# Create session info dict and store it
	session_info = {'session_ID':session_ID,
					'user_ID':user_ID,
					'ip_address' : request.remote_addr,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'user_agent':request.headers.get('User-Agent'),
					'window_width': window_width,
					'window_height': window_height}
	write_dict_to_sql_usage(session_info, 'sessions')
	return jsonify(user_ID = user_ID, session_ID = session_ID)

def query_liked_names(user_ID, session_ID, logged_in):
	if(logged_in):
		query = '''SELECT name, sex, rank
					FROM feedback 
					WHERE user_id = %(user_id)s
					AND feedback = 'like' 
					'''
		params = {'user_id':user_ID}
	else:
		query = '''SELECT name, sex, rank
					FROM feedback 
					WHERE user_id = %(user_id)s
					AND session_id = %(session_id)s
					AND feedback = 'like' 
					'''
		params = {'user_id':user_ID, 'session_id':session_ID}	
	liked_names = pd.read_sql(sql=query, con=sql_conn, params=params).fillna(0).to_dict(orient='records')
	return liked_names

@application.route('/request_liked_names', methods=['GET'])
def request_liked_names():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	logged_in = request.args.get('logged_in') == 'true'
	print('Requesting liked names, logged_in = {}'.format(logged_in))
	liked_names = query_liked_names(user_ID, session_ID, logged_in)
	return jsonify(liked_names = liked_names)

@application.route('/swap_ranks', methods=['GET'])
def swap_ranks():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	logged_in = request.args.get('logged_in') == 'true'
	sex = request.args.get('sex')
	name_one = request.args.get('name_one').strip().title()
	name_two = request.args.get('name_two').strip().title()
	new_rank_name_one = int(request.args.get('new_rank_name_one'))
	new_rank_name_two = int(request.args.get('new_rank_name_two'))

	# Check if logged in
	# Hier nog potentiele bug: als een user al een lijstje heeft, pas na een tijd inlogt, kunnen de namen er dubbel instaan!
	if(logged_in):
		params = {'name_one':name_one, 'user_id':user_ID,'sex':sex, 'new_rank_name_one':new_rank_name_one}
		query = '''UPDATE feedback 
						SET rank = %(new_rank_name_one)s
						WHERE name = %(name_one)s 
						AND user_id = %(user_id)s 
						AND sex  = %(sex)s'''
		sql_conn.execute(query, params)
		# Update name two
		params = {'name_two':name_two, 'user_id':user_ID,'sex':sex, 'new_rank_name_two':new_rank_name_two}
		query = '''UPDATE feedback 
						SET rank = %(new_rank_name_two)s
						WHERE name = %(name_two)s 
						AND user_id = %(user_id)s 
						AND sex  = %(sex)s'''
		sql_conn.execute(query, params)
	else:	
		params = {'name_one':name_one, 'user_id':user_ID,'session_id':session_ID, 'sex':sex, 'new_rank_name_one':new_rank_name_one}
		query = '''UPDATE feedback 
						SET rank = %(new_rank_name_one)s
						WHERE name = %(name_one)s 
						AND user_id = %(user_id)s 
						AND session_ID = %(session_id)s 
						AND sex  = %(sex)s'''
		sql_conn.execute(query, params)
		# Update name two
		params = {'name_two':name_two, 'user_id':user_ID, 'session_id':session_ID,'sex':sex, 'new_rank_name_two':new_rank_name_two}
		query = '''UPDATE feedback 
						SET rank = %(new_rank_name_two)s
						WHERE name = %(name_two)s 
						AND user_id = %(user_id)s 
						AND session_ID = %(session_id)s 
						AND sex  = %(sex)s'''
		sql_conn.execute(query, params)
	# Send back the liked names, a bit the same as request_liked_names
	liked_names = query_liked_names(user_ID, session_ID, logged_in)
	return jsonify(liked_names = liked_names)	

@application.route('/delete_name', methods=['GET'])
def delete_name():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	logged_in = request.args.get('logged_in') == 'true'
	sex = request.args.get('sex')
	name = request.args.get('name').strip().title()
	rank_deleted_name = request.args.get('rank')
	# TO DO: reset all the ranks!
	if(logged_in):
		query = '''DELETE FROM feedback 
						WHERE name = %(name)s 
						AND user_id = %(user_id)s 
						AND sex  = %(sex)s'''
		params = {'name':name, 'user_id':user_ID, 'sex':sex, 'rank':None}
		sql_conn.execute(query, params)
		# Update the ranks
		query = '''UPDATE feedback 
						SET rank = rank - 1
						WHERE user_id = %(user_id)s 
						AND sex  = %(sex)s
						AND rank > %(rank)s'''
		params = {'name':name, 'user_id':user_ID, 'sex':sex, 'rank':rank_deleted_name}
		sql_conn.execute(query, params)	
	else:
		query = '''DELETE FROM feedback 
						WHERE name = %(name)s 
						AND user_id = %(user_id)s 
						AND session_id = %(session_id)s 
						AND sex  = %(sex)s'''
		params = {'name':name, 'user_id':user_ID,'session_id':session_ID, 'sex':sex, 'rank':None}
		sql_conn.execute(query, params)
		# Update the ranks
		query = '''UPDATE feedback 
						SET rank = rank - 1
						WHERE user_id = %(user_id)s 
						AND session_id = %(session_id)s 
						AND sex  = %(sex)s
						AND rank > %(rank)s'''
		params = {'name':name, 'user_id':user_ID,'session_id':session_ID, 'sex':sex, 'rank':rank_deleted_name}
		sql_conn.execute(query, params)
	# Query liked names
	liked_names = query_liked_names(user_ID, session_ID, logged_in)
	return jsonify(liked_names = liked_names)

@application.route('/add_name', methods=['GET'])
def add_name():
	user_ID = request.args.get('user_ID')
	session_ID = request.args.get('session_ID')
	logged_in = request.args.get('logged_in') == 'true'
	name = request.args.get('name').title()
	sex = request.args.get('sex')
	rank = determine_rank_for_new_like(user_ID, session_ID, sex)
	# Update the table, change the feedback of the particular name to no_like
	# First check if the name is not in there
	if(logged_in):
		query = '''SELECT * FROM feedback 
					WHERE name = %(name)s 
					AND user_id = %(user_id)s 
					AND sex = %(sex)s'''
		params = {'name':name, 'user_id': user_ID, 'sex':sex}
		test = pd.read_sql(sql = query, con = sql_conn, params = params)
	else:
		query = '''SELECT * FROM feedback 
					WHERE name = %(name)s 
					AND user_id = %(user_id)s 
					AND sex = %(sex)s
					AND session_id = %(session_id)s'''
		params = {'name':name, 'user_id': user_ID,'session_id':session_ID, 'sex':sex}
		test = pd.read_sql(sql = query, con = sql_conn, params = params)
	
	# Hier zit een bug in, als de naam al in het systeem zit
	if(len(test>0)):
		params={'name':name,
					'sex':sex,
					'user_id':user_ID,
					'rank':rank}
		query = '''UPDATE feedback 
					SET feedback = 'like' , rank = %(rank)s
					WHERE name = %(name)s 
					AND user_id = %(user_id)s 
					AND sex  = %(sex)s'''
		sql_conn.execute(query, params)
	else:

		query = '''INSERT INTO feedback 
				VALUES (%(feedback)s,%(name)s,%(session_id)s,%(time)s,%(user_id)s,%(sex)s, %(rank)s)'''
		params={'feedback':'like',
					'name':name,
					'session_id':session_ID,
					'sex':sex,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'user_id':user_ID,
					'rank':rank}
		sql_conn.execute(query, params)
	# Send back the liked names, a bit the same as request_liked_names
	liked_names = query_liked_names(user_ID, session_ID, logged_in)
	return jsonify(liked_names = liked_names)

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
	to_write_away = pd.DataFrame.from_dict([info_dict])
	to_write_away.to_sql(name=table_name,con = sql_conn, if_exists='append',index=False)
	return None	

def determine_rank_for_new_like(user_id, session_id, sex):
	query = '''SELECT *
					FROM feedback
					WHERE user_id = %(user_id)s
					AND sex = %(sex)s 
					AND feedback = 'like' '''
	params = {'user_id':user_id,'session_id':session_id, 'sex':sex}
	feedback_already_stored = pd.read_sql(sql=query, con=sql_conn, params = params)
	if(len(feedback_already_stored) > 0 ): rank = np.max(feedback_already_stored['rank'])+1
	else: rank = 1	
	return rank

@application.route('/return_vote', methods=['GET'])
def return_vote():
	# First determine new rank for a like
	if(request.args.get('feedback') == 'like'):
		rank = determine_rank_for_new_like(request.args.get('user_ID'),request.args.get('session_ID'), request.args.get('sex'))
	else:
		rank = None	

	# Prepare in dict to easy store
	feedback = {'session_id':request.args.get('session_ID'),
				'user_id':request.args.get('user_ID'),
				'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
				'feedback':request.args.get('feedback'),
				'name':request.args.get('name'),
				'sex':request.args.get('sex'),
				'rank':rank}
	write_dict_to_sql_usage(feedback, 'feedback')
	return jsonify(whatever = '')

def store_names_awaiting_feedback(names, sex, user_id, session_id):
	to_store = pd.DataFrame({'name':names, 
							'user_id':np.repeat(user_id, len(names)), 
							'session_id':np.repeat(session_id, len(names)),
							'requested_sex':np.repeat(sex, len(names))})
	to_store.to_sql(name='awaiting_feedback', index=False, if_exists = 'append', con = sql_conn)
	print('{} suggestions stored away in awaiting feedback'.format(len(names)))
	return None

@application.route('/get_stringer_suggestion', methods=['GET'])
def get_stringer_suggestion():
	# Request parameters
	how_many = int(request.args.get('how_many'))
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')
	requested_sex = request.args.get('requested_sex')
	suggestion_type = request.args.get('type')

	print('User {} wants {} how many suggestions of type {}'.format(user_ID.encode('ascii', 'replace'),how_many,suggestion_type ))
	
	# Random suggestions
	# ------------------
	if(suggestion_type=='random'):
		print('Querying random names')
		query = '''SELECT *
						FROM voornamen_pivot_2 
						WHERE sex = %(sex)s
						AND region = 'Belgie'
						AND name NOT IN (
							SELECT name 
							FROM feedback
							WHERE user_id = %(user_id)s)
						AND name NOT IN(
							SELECT name
							FROM awaiting_feedback
							WHERE user_id = %(user_id)s
							AND requested_sex = %(sex)s
							AND session_id = %(session_id)s
						)
						ORDER BY RANDOM() LIMIT 10'''
		params = {'sex':requested_sex,'user_id':user_ID, 'session_id':session_ID}
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'name'].values[:how_many].tolist()
		store_names_awaiting_feedback(suggestion, requested_sex, user_ID, session_ID)
		return jsonify(names = suggestion, sex = requested_sex)

	# Check how many postive feedbacks the user already gave.
	query = '''SELECT * FROM feedback WHERE user_id = %(user_id)s AND sex = %(sex)s '''
	params = {'user_id':user_ID, 'sex':requested_sex}
	names_feedback = pd.read_sql_query(sql = query, con = sql_conn, params=params)
	n_liked_names = len(names_feedback.loc[names_feedback['feedback'] == 'like',:])
	n_disliked_names = len(names_feedback.loc[names_feedback['feedback'] != 'like',:])
	
	# How many names did he already lookup?
	query = '''SELECT * FROM name_lookups WHERE user_id = %(user_id)s'''
	lookup_names = pd.read_sql(sql=query, con=sql_conn, params=params)
	lookup_names_1 = lookup_names.loc[lookup_names['sex_name_1']==requested_sex,:]
	lookup_names_1 = np.unique(lookup_names_1['name_1'].values).tolist()
	lookup_names_2 = lookup_names.loc[lookup_names['sex_name_2']==requested_sex,:]
	lookup_names_2 = np.unique(lookup_names_2['name_2'].values).tolist()
	lookup_names = lookup_names_1
	lookup_names.extend(lookup_names_2)
	lookup_names = [lookup_name for lookup_name in lookup_names if lookup_name != '']
	n_lookup_names = len(lookup_names)

	# If the learning matrix is too small, just query popular names
	# ------------------------------------------------------------
	if(((n_liked_names+n_lookup_names)<4) | (n_disliked_names<4)):
		print('Just query popular names')
		query = '''SELECT *
						FROM voornamen_pivot_2
						WHERE sex = %(sex)s
						AND region = 'Vlaanderen'
						AND score_popular > 3
						AND name NOT IN (
							SELECT name 
							FROM feedback
							WHERE user_id = %(user_id)s)
						AND name NOT IN(
							SELECT name
							FROM awaiting_feedback
							WHERE user_id = %(user_id)s
							AND requested_sex = %(sex)s
							AND session_id = %(session_id)s
						)
						ORDER BY RANDOM() LIMIT 10'''
		params = {'sex':requested_sex,'user_id':user_ID, 'session_id':session_ID}
		suggestion = pd.read_sql_query(sql = query, con = sql_conn, params=params).loc[:,'name'].values[:how_many].tolist()
		store_names_awaiting_feedback(suggestion, requested_sex, user_ID, session_ID)
		return jsonify(names = suggestion, sex = requested_sex)

	# Random forest
	# --------------
	params = {'user_id':user_ID, 'requested_sex':requested_sex}
	query = '''SELECT voornamen_pivot.*, feedback.feedback
			FROM voornamen_pivot_2 voornamen_pivot, feedback
			WHERE voornamen_pivot.name = feedback.name
			AND voornamen_pivot.region = 'Vlaanderen'
			AND voornamen_pivot.sex = feedback.sex
			AND feedback.user_id = %(user_id)s;'''
	learning_matrix = pd.read_sql_query(sql = query, con = sql_conn, params=params)
	
	# Apend learning matrix with lookup names
	if(len(lookup_names)>0):
		params = {'user_id':user_ID, 'requested_sex':requested_sex, 'lookup_names':lookup_names}
		lookup_names = pd.read_sql_query('''SELECT voornamen_pivot.*
											FROM voornamen_pivot_2 as voornamen_pivot
												WHERE voornamen_pivot.name = ANY(%(lookup_names)s)
												AND voornamen_pivot.region = 'Vlaanderen'
												AND voornamen_pivot.sex = %(requested_sex)s;''', 
												con = sql_conn, params=params)
		lookup_names['feedback'] = 'like'
		learning_matrix = pd.concat([learning_matrix, lookup_names], axis=0)
		learning_matrix = learning_matrix.drop_duplicates('name' )

	# Change the outcome variable from string 'like' to 1
	learning_matrix['feedback'] = learning_matrix['feedback'] == 'like'
	
	# Drop columns with no variation and columns with strings and columns with the number of names per year
	learning_matrix = learning_matrix.drop(['origin','meaning','closest_match','closest_match_origin', 'origin_feature'], axis=1)
	for column in learning_matrix.columns:
		if(column in ['name','feedback', 'sex', 'region']): continue
		if(len(np.unique(learning_matrix[column]))==1):
			learning_matrix = learning_matrix.drop(column, axis=1)
	learning_matrix = learning_matrix.drop([feature for feature in learning_matrix.columns if re.search('[0-9]{4}', feature)], axis=1)

	# Drop equal columns
	columns_to_drop = []
	for index, column_1 in enumerate(learning_matrix.columns):
		if(column_1 in ['name','feedback', 'sex', 'region']): continue
		for index_column_2 in np.arange(index+1, len(learning_matrix.columns)):
			column_2 = learning_matrix.columns[index_column_2]
			if(column_2 in ['name','feedback', 'sex', 'region']): continue
			if(sum(learning_matrix[column_1] == learning_matrix[column_2]) == len(learning_matrix)):
				columns_to_drop.extend([column_2])
	columns_to_drop = np.unique(columns_to_drop)
	learning_matrix = learning_matrix.drop(columns_to_drop, axis=1)

	# Features
	features = list(learning_matrix.columns)
	to_remove = ['name', 'sex', 'region','feedback', 'all_ages', 'between18and64', 'minus18', 'plus64']
	features = [feature for feature in features if feature not in to_remove]
	features = [feature for feature in features if re.search('[0-9]{4}', feature) is None]
	X = learning_matrix[features].fillna(0).copy()
	y = learning_matrix['feedback']
	
	# Train the model
	rf = RandomForestClassifier(n_estimators = 10, max_features = int(np.ceil(len(features)/2)))
	grid = {'max_depth':[2,4,6,8,10],'min_samples_leaf':[1,2,4]}
	grid_search = GridSearchCV(estimator = rf, param_grid = grid, scoring='recall')
	grid_search.fit(X = X, y = y)
	trained_rf = grid_search.best_estimator_
	feature_importances = pd.DataFrame({'importances': trained_rf.feature_importances_, 'features':features})
	feature_importances = feature_importances.sort_values('importances', ascending=False)
	
	# Train a decission tree with only one cut based on the most important feature of RF to query a small test sample
	best_feature = feature_importances.iloc[0]['features']
	clf = DecisionTreeClassifier(max_depth=1, class_weight='balanced')
	clf.fit(X = X[[best_feature]], y = y)
	temp_treshold =  clf.tree_.threshold[0]

	# Write the best feature away
	dict_to_store = {'best_feature':best_feature, 'user_id': user_ID, 'requested_sex':requested_sex, 
						'value_left_child': clf.tree_.value[1][0][0], 'value_right_child': clf.tree_.value[1][0][1],
						'treshold' :  clf.tree_.threshold[0], 'len_training_data':len(learning_matrix)}
	write_dict_to_sql_usage(dict_to_store, 'decision_trees')

	# Query the testsample, by using the treshold of the classifiction tree
	if(clf.tree_.value[1][0][0] <  clf.tree_.value[1][0][1]):
		if(type(X[[best_feature]].iloc[0,0]) == np.bool_): temp_treshold = True
		# If numeric, apply safety margin for query. As the number of samples in the training dataset is very small,
		# it might be that the boundary for the query doesn't get samples out of the database
		print(type(X[[best_feature]].iloc[0,0]))
		if(type(X[[best_feature]].iloc[0,0]) == np.float64): temp_treshold = temp_treshold*1.25
		print('%s needs to be smaller than %f' %(best_feature, temp_treshold))
		query = '''SELECT * FROM voornamen_pivot_2
										WHERE region = 'Vlaanderen'
										AND sex = %(requested_sex)s
										AND best_feature < %(treshold)s 
										AND name NOT IN (
												SELECT name FROM feedback WHERE user_id = %(user_id)s )
										AND name NOT IN(
											SELECT name FROM awaiting_feedback
											WHERE user_id = %(user_id)s
											AND requested_sex = %(requested_sex)s
											AND session_id = %(session_id)s )
										ORDER BY RANDOM() LIMIT 100 '''.replace('best_feature', best_feature)
	else:
		if(type(X[[best_feature]].iloc[0,0]) == np.bool_): temp_treshold = False
		if(type(X[[best_feature]].iloc[0,0]) == np.float64): temp_treshold = temp_treshold*0.75
		print('%s needs to be bigger than %f' %(best_feature,temp_treshold))
		query = '''SELECT * FROM voornamen_pivot_2
										WHERE region = 'Vlaanderen'
										AND sex = %(requested_sex)s
										AND best_feature > %(treshold)s
										AND name NOT IN (
												SELECT name 
												FROM feedback
												WHERE user_id = %(user_id)s )
										AND name NOT IN(
											SELECT name
											FROM awaiting_feedback
											WHERE user_id = %(user_id)s
											AND requested_sex = %(requested_sex)s
											AND session_id = %(session_id)s )
										ORDER BY RANDOM() LIMIT 100   '''.replace('best_feature', best_feature)
	params = {'user_id':user_ID,'session_id':session_ID,'requested_sex':requested_sex, 
						'best_feature':best_feature, 'treshold':temp_treshold}
	test_sample = pd.read_sql_query(sql = query, con = sql_conn, params=params)

	# Predict the test sample
	test_sample = test_sample.drop(['sex', 'region'], axis = 1)
	test_sample['predictions'] = trained_rf.predict_proba(X = test_sample[features].fillna(0))[:,1]
	print(test_sample[['predictions', 'name']].sort_values('predictions', ascending=False).head(5))
	suggestion = list(test_sample[['predictions', 'name']].sort_values('predictions', ascending=False)['name'].head(how_many).values)
	store_names_awaiting_feedback(suggestion, requested_sex, user_ID, session_ID)	
	return jsonify(names = suggestion, sex = requested_sex)

@application.route('/export', methods=['GET'])
def export():
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')
	logged_in = request.args.get('logged_in')
	if(logged_in is False):
		print('requesting csv but not logged in')
		return None

	# Get everything back from the user
	params = {'user_id':user_ID}
	query = '''SELECT voornamen_pivot.*, feedback.feedback
			FROM voornamen_pivot_2 voornamen_pivot, feedback
			WHERE voornamen_pivot.name = feedback.name
			AND voornamen_pivot.region = 'Vlaanderen'
			AND feedback.user_id = %(user_id)s;'''
	learning_matrix = pd.read_sql_query(sql = query, con = sql_conn, params=params)
	# Add all the names with letter m as a start
	query = '''SELECT * FROM voornamen_pivot_2
										WHERE region = 'Vlaanderen'
										AND lower(substring(name from 1 for 1)) = 'm' 
										AND name NOT IN (
												SELECT name 
												FROM feedback
												WHERE user_id = %(user_id)s )'''
	test_sample = pd.read_sql_query(sql = query, con = sql_conn, params=params)	
	export_csv = pd.concat([learning_matrix, test_sample], axis = 0)
	print('Shape of export csv : {} '.format(export_csv.shape))

	csv_filename =  "generated_csvs/learning_matrix_" + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
	if not os.path.exists('static/generated_csvs'):
		os.makedirs('static/generated_csvs')

	export_csv = export_csv.to_csv( 'static/' + csv_filename, sep = ",", index=False, encoding = 'utf-8')
	return jsonify(file_link = csv_filename)

@application.route('/get_stats', methods=['GET'])
def get_stats():
	
	# Request name info, for safety encode utf8 and then back to unicode. 
	# Question: what happens for requests that come from other kinds of browsers?
	name_1 = request.args.get('name_1').strip().title()
	name_2 = ''
	sex_name_1 = ''
	sex_name_2 = request.args.get('sex_name_2')
	session_ID = request.args.get('session_ID')
	user_ID = request.args.get('user_ID')
	from_landing_page = request.args.get('from_landing_page') == 'true'
	print('User request: name 1: {} of sex {}, from landing page: {}'.format(name_1.encode('ascii', 'replace'), sex_name_2, from_landing_page))
	
	# Query name 1
	query = '''SELECT *
				FROM voornamen_pivot_2 
				WHERE name = %(name)s
				AND region = 'Vlaanderen' '''

	params = {'name':name_1}
	name_1_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params)
	# Check that the name was in the database. If not, return all zeros
	if(len(name_1_kpis) == 0):
		print('No names found')
		name_1_kpis = pd.Series({'score_original':5.0,'score_vintage':0.0,'score_classic':0.0,'score_trend':0.0,'score_popular':0.0})
		sex_name_1 = 'M'
		name_1_ts = np.repeat(0, 20)
		name_1_meaning = 'Unknown'		
	# Else, set return values
	else:
		name_1_kpis = name_1_kpis.loc[name_1_kpis['all_ages'] == np.max(name_1_kpis['all_ages']),:].iloc[0,:]
		sex_name_1 = name_1_kpis['sex']
		name_1_ts = name_1_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values
		name_1_meaning = name_1_kpis['meaning']

	# Store away Lookup info
	lookup_info = {'session_id':session_ID,
					'user_id':user_ID,
					'time':datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
					'name_1': name_1.encode('utf-8'),
					'name_2': name_2.encode('utf-8'),
					'sex_name_1':sex_name_1,
					'sex_name_2':sex_name_2,
					'from_landing_page' :from_landing_page}
	write_dict_to_sql_usage(lookup_info, 'name_lookups')

	# Query name 2, if name is undefined (might be coming from landing page), select a name that is close the first name
	if(name_2 == ''):
		query = '''	SELECT *, public.levenshtein(%(name)s, name) as distance
					FROM voornamen_pivot_2
					WHERE sex = %(sex)s
					AND region = 'Vlaanderen'
					AND name <> %(name)s
					ORDER BY distance, all_ages DESC
					LIMIT 2;'''
		params = {'name':name_1, 'sex':sex_name_1}
		name_2_kpis = pd.read_sql_query(sql = query, con = sql_conn, params=params)
		if(len(name_2_kpis)==0):
			name_2 = None
			name_2_kpis = pd.Series({'score_original':5.0,'score_vintage':0.0,'score_classic':0.0,'score_trend':0.0,'score_popular':0.0})
			name_2_ts = np.repeat(0, 20)
			name_2_meaning = 'Unknown'
		else:
			name_2_kpis = name_2_kpis.loc[np.random.randint(2),:]
			name_2 = name_2_kpis['name']
			name_2_ts = name_2_kpis.loc[['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014']].fillna(0).values
			name_2_meaning = ''
			sex_name_2 = sex_name_1
	# Query the second name in the normal way as it is defined by the user
	else:
		query = '''SELECT *
				FROM voornamen_pivot_2
				WHERE name = %(name)s
				AND region = %(region)s
				LIMIT 1'''				
		params = {'name':name_2, 'region':region}
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
								'name_2':name_2_meaning},
					sexes = {'name_1':sex_name_1,
							 'name_2':sex_name_2},
					names = {'name_1':name_1.encode('utf-8'),
							 'name_2':name_2.encode('utf-8')})

@application.route('/')
def index():
	return redirect(url_for('static', filename='index.html'))

@application.route('/<path:javascript_file>')
def javascript():
	return redirect(url_for('static', filename=javascript_file))
	
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=True)




