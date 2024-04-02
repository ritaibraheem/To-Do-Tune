# import streamlit as st
import pandas as pd 
from db_funcs import *
from sklearn.ensemble import RandomForestClassifier


def run_ml_model():

    train = get_all_ml_data('dataML')
    train_df = pd.DataFrame(train,columns=["index", "total_days_from_input", "amount_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "chore_type", "count_times_late_in_this_chore", "is_postponed"])

    data = get_all_ml_data('dataMLCopy') # np 'is_postponed' column
    data_df = pd.DataFrame(data,columns=["index", "total_days_from_input", "amount_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "chore_type", "count_times_late_in_this_chore"])

    X = train_df[["total_days_from_input", "amount_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "chore_type", "count_times_late_in_this_chore"]]
    y = train_df['is_postponed']  # This should be a binary column in your dataset

        # Training the RandomForestClassifier on the entire dataset
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    pred_data_df = data_df[["total_days_from_input", "amount_days_late", "avg_mood_int", "avg_sleep_hours_int", "medication_taken", "chore_type", "count_times_late_in_this_chore"]]

    probabilities = clf.predict_proba(pred_data_df)
    
    # Extracting the probabilities for being postponed (assuming it's class 1)
    postponed_probabilities = probabilities[:, 1]

    pred_data_df['probability_postponed'] = postponed_probabilities

    highest_prob_index = pred_data_df['probability_postponed'].idxmax()

    return 'Index of the row with the highest probability of being postponed: ' + str(highest_prob_index)