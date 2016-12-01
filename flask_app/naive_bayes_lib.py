
import pandas as pd
import numpy as np
import re

def drop_unwanted_columns(df):
    df = df.drop(['1995', '1996', '1997', '1998', '1999', '2000',
       '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
       '2010', '2011', '2012', '2013', '2014', 'sex', 'region', 'between18and64', 'minus18','all_ages', 
    'plus64', 'origin', 'meaning','closest_match','closest_match_origin','origin_feature'], axis=1)
    return df
def drop_columns_with_no_variation(df):
    for column in df.columns:
        if(column not in ['name','feedback']):
            if(len(np.unique(df[column]))==1):
                df = df.drop(column, axis=1)
    return df
def drop_equal_columns(df):
    columns_to_drop = []
    for column_1 in df.columns:
        if column_1 == 'feedback': continue
        for column_2 in df.columns:
            if column_1 == column_2: continue
            if(sum(df[column_1] == df[column_2])> (len(df)*0.90)):
                columns_to_drop.extend([column_1])
            continue
    columns_to_drop = np.unique(columns_to_drop)
    df = df.drop(columns_to_drop, axis=1)
    return df 
    
def keep_only_interesting_origins(df, how_many):
    origin_features = []
    for feature in df.columns:
        if(re.search('origin_', feature)):
            origin_features.extend([feature])
    origin_features.extend(['feedback'])
    groupby_feedback = df[origin_features].groupby('feedback').mean()
    # Drop the columns with too little in between class variation
    columns_to_drop = np.abs(groupby_feedback.iloc[0,:] - groupby_feedback.iloc[1,:]).sort_values().index[:-how_many]
    df = df.drop(columns_to_drop, axis=1)
    return df 

class Naive_bayes_model:
    'Naive Bayes implementation'
    def __init__(self):
        self.class_summaries = {}
        self.features_dict = {}
        self.targets = []
        self.priors = {}
        self.len_training = 0
    
    def train(self,df, features_dict, target):
        self.features_dict = features_dict
        self.targets = np.unique(df[target])
        for feature, feature_type in features_dict.items():
            print(feature)
            self.class_summaries[feature] = self.calculate_class_summary(df[[feature, target]], feature_type, target)
        self.calculate_priors(df, target)
        self.len_training = len(df)
        
    def calculate_priors(self, df, target):
        self.priors = dict(df[target].value_counts()/len(df))
        
    def calculate_class_summary(self,df_feature_and_target, feature_type, target):
        # With this function we calculate the summaries per class, or the likelihood of X being X given the class
        # This summary depends of the kind of distribution
        if(feature_type == 'int_bigger_than_zero'):
            summary = df_feature_and_target.groupby(target).agg(lambda x: float(sum(x>0))/len(x))
            summary.columns = ['True']
            summary = summary.to_dict('index')            
        elif(feature_type=='bool'):
            summary = df_feature_and_target.groupby(target).mean()
            summary.columns=['True']
            summary = summary.to_dict('index')
            print(summary)
        elif(feature_type=='normal'):
            means = df_feature_and_target.groupby(target).mean()
            means.columns=['mean']
            stds = df_feature_and_target.groupby(target).std()
            stds.columns=['std']
            summary = pd.merge(means, stds, left_index=True, right_index=True).to_dict('index')
        return summary
    
    def predict(self, to_predict_df):
        odds_ratios = to_predict_df[list(self.features_dict.keys())].apply(self.predict_odds_ratio, axis=1)
        return odds_ratios
    
    def predict_odds_ratio(self, observation):
        if(len(self.targets) > 2): print('Error, odds ratio impossible for more than 2 target classes')
        odds_ratio = 0
        # Kind of additive model, assume the features are independent from eachother
        for feature, feature_type in self.features_dict.items():
            probabilities = {feature: 0 for feature in self.targets }
            # Calculate now the likelihood of finding the features of this observation, given the classes of the target
            if(feature_type == 'normal'):
                for target in self.targets:
                    temp_mean = self.class_summaries[feature][target]['mean']
                    temp_std = self.class_summaries[feature][target]['std']
                    temp_x = (observation[feature] - temp_mean)/temp_std
                    likelihood = np.exp(-.5*np.square(temp_x))/np.sqrt(2*3.141)/temp_std
                    probabilities[target] = likelihood
            if(feature_type == 'bool'):
                for target in self.targets:
                    if(bool(observation[feature])): probabilities[target] = self.class_summaries[feature][target]['True']
                    else: probabilities[target] = 1-self.class_summaries[feature][target]['True']
            if(feature_type == 'int_bigger_than_zero'):
                for target in self.targets:
                    if(observation[feature]>0): probabilities[target] = self.class_summaries[feature][target]['True']
                    else: probabilities[target] = 1-self.class_summaries[feature][target]['True']
            # Hier probleem, soms delen door 0
            teller = probabilities[self.targets[0]] + 1.0/self.len_training
            noemer = probabilities[self.targets[1]] + 1.0/self.len_training
            odds_ratio += np.log(teller/noemer)
        odds_ratio += np.log(self.priors[self.targets[0]]/self.priors[self.targets[1]])
        return odds_ratio
        