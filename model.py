# import streamlit as st
import pandas as pd 
from db_funcs import *
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta, date

def run_ml_model():
    
    def count_days_late(row):
        if row['is_late']:
            return (row['end_time']-row['deadline']).days
        else: return timedelta(days=0).days

    def count_times_late_in_this_chore(tag):
        return done_tasks_tag_dic[tag]

    result = view_all_data()
    result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'medication_taken', 'avg_mood_int', 'avg_sleep_hours_int'])
    result_df['deadline']=pd.to_datetime(result_df['deadline'])
    result_df['end_time']=pd.to_datetime(result_df['end_time'])

    # TRAIN DATA = DONE TASKS
    done_tasks = result_df[(result_df['task_status']=='Done')]
    done_tasks['count_days_late'] = done_tasks.apply(count_days_late, axis=1)
    done_tasks['tag'].replace(['exercise', 'studies', 'home', 'health', 'bureaucracy', 'work','fun'], [1,2,3,4,5,6,7], inplace=True)
    done_tasks_tag_gb = done_tasks.groupby('tag').size()
    done_tasks_tag_dic = done_tasks_tag_gb.to_dict()
    done_tasks['count_times_late_in_this_chore'] = done_tasks['tag'].apply(count_times_late_in_this_chore)

    ml_data_train_df = done_tasks[["guid", "count_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "tag", "count_times_late_in_this_chore", "is_late"]]
    ml_data_train_df = ml_data_train_df.rename(columns={"tag": "chore_type", "is_late": "is_postponed"})

    X = ml_data_train_df[["count_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "chore_type", "count_times_late_in_this_chore"]]
    y = ml_data_train_df['is_postponed']


    # RRED DATA = TO-DO IN-PROGRESS &  TASKS
    un_done_tasks = result_df[(result_df['task_status']!='Done')]
    un_done_tasks = un_done_tasks[['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'today_date', 'medication_taken', 'avg_mood_int', 'avg_sleep_hours_int']]
    un_done_tasks['count_days_late'] = 0
    un_done_tasks['tag'].replace(['exercise', 'studies', 'home', 'health', 'bureaucracy', 'work','fun'], [1,2,3,4,5,6,7], inplace=True)
    un_done_tasks['count_times_late_in_this_chore'] = un_done_tasks['tag'].apply(count_times_late_in_this_chore)

#     print(un_done_tasks)
    
    ml_data_pred_df = un_done_tasks[["count_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "tag", "count_times_late_in_this_chore"]]
    ml_data_pred_df = ml_data_pred_df.rename(columns={"tag": "chore_type"})

    # Training the RandomForestClassifier on the entire dataset
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    probabilities = clf.predict_proba(ml_data_pred_df)
    postponed_probabilities = probabilities[:, 1]
    
    un_done_tasks['probability_postponed'] = postponed_probabilities
    highest_prob_index = un_done_tasks['probability_postponed'].idxmax()
    
    next_postponed_task = un_done_tasks.loc[highest_prob_index]
    next_postponed_task = pd.DataFrame(next_postponed_task).transpose()
    next_postponed_task['tag'].replace([1,2,3,4,5,6,7],['exercise', 'studies', 'home', 'health', 'bureaucracy', 'work','fun'], inplace=True)
    
    return next_postponed_task