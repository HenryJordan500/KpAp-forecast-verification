import numpy as np
import pandas as pd

import datetime as dt
from pathlib import Path


def make_Ap_storage_list():

    return [[] for i in range(3)]


def make_Kp_storage_list():

    return [[] for i in range(24)]


def create_3day_Ap_from_real_vals(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('extracted_data/daily_Ap.csv')

    real_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'])-3):
        for j in range(len(real_Ap_lists)):
            real_Ap_lists[j].append(Ap_values[i+j+1])

    Ap_dict = {'Forecast Issued': df_real_Ap['Datetime'][:-3]}
    for i in range(len(real_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(real_Ap_lists[i], dtype=int)

    df_real_Ap_3day = pd.DataFrame(Ap_dict)

    df_real_Ap_3day.to_csv(f'{save_path_lead}/real_3day_daily_Ap.csv', index=False)

    return df_real_Ap_3day


def create_3day_Kp_from_real_vals(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('extracted_data/3hour_Kp.csv')

    real_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'])-24):
        for j in range(len(real_Kp_lists)):
            real_Kp_lists[j].append(Kp_values[i+j+1])

    Kp_dict = {'Forecast Issued': df_real_Kp['Datetime'][:-24]}
    for i in range(len(real_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(real_Kp_lists[i], dtype=float)
    
    df_real_Kp_3day = pd.DataFrame(Kp_dict)

    df_real_Kp_3day_filtered = df_real_Kp_3day[df_real_Kp_3day.index % 8 == 0].copy()

    df_real_Kp_3day_filtered['Forecast Issued'] = df_real_Kp_3day_filtered['Forecast Issued'].str[:-9]

    df_real_Kp_3day.to_csv(f'{save_path_lead}/real_3day_3hr_Kp.csv', index=False)

    return df_real_Kp_3day_filtered


def create_3day_ap_from_real_vals(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_ap = pd.read_csv('extracted_data/3hour_ap.csv')

    real_ap_lists = make_Kp_storage_list()

    ap_values = df_real_ap['ap'].values
    for i in range(len(df_real_ap['Datetime'])-24):
        for j in range(len(real_ap_lists)):
            real_ap_lists[j].append(ap_values[i+j+1])

    ap_dict = {'Forecast Issued': df_real_ap['Datetime'][:-24]}
    for i in range(len(real_ap_lists)):
        ap_dict[f'{3*(i+1)}hrap'] = np.array(real_ap_lists[i], dtype=float)
    
    df_real_ap_3day = pd.DataFrame(ap_dict)

    df_real_ap_3day_filtered = df_real_ap_3day[df_real_ap_3day.index % 8 == 0].copy()

    df_real_ap_3day_filtered['Forecast Issued'] = df_real_ap_3day_filtered['Forecast Issued'].str[:-9]

    df_real_ap_3day.to_csv(f'{save_path_lead}/real_3day_3hr_ap.csv', index=False)

    return df_real_ap_3day_filtered


def create_3day_Ap_persistence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('extracted_data/daily_Ap.csv')

    persistence_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'])):
        for j in range(len(persistence_Ap_lists)):
            persistence_Ap_lists[j].append(Ap_values[i])

    Ap_dict = {'Forecast Issued': df_real_Ap['Datetime']}
    for i in range(len(persistence_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(persistence_Ap_lists[i], dtype=int)

    df_persistence_Ap_3day = pd.DataFrame(Ap_dict)

    df_persistence_Ap_3day.to_csv(f'{save_path_lead}/persistence_3day_daily_Ap.csv', index=False)

    return df_persistence_Ap_3day


def create_3day_Kp_persistence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('extracted_data/3hour_Kp.csv')

    persistence_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'])):
        for j in range(len(persistence_Kp_lists)):
            persistence_Kp_lists[j].append(Kp_values[i])

    Kp_dict = {'Forecast Issued': df_real_Kp['Datetime']}
    for i in range(len(persistence_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(persistence_Kp_lists[i], dtype=float)

    df_persistence_Kp_3day = pd.DataFrame(Kp_dict)

    df_persistence_Kp_3day_filtered = df_persistence_Kp_3day[df_persistence_Kp_3day.index % 8 == 0].copy()

    df_persistence_Kp_3day_filtered['Forecast Issued'] = df_persistence_Kp_3day_filtered['Forecast Issued'].str[:-9]

    df_persistence_Kp_3day_filtered.to_csv(f'{save_path_lead}/persistence_3day_3hr_Kp.csv', index=False)

    return df_persistence_Kp_3day_filtered


def create_3day_ap_persistence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_ap = pd.read_csv('extracted_data/3hour_ap.csv')

    persistence_ap_lists = make_Kp_storage_list()

    ap_values = df_real_ap['ap'].values
    for i in range(len(df_real_ap['Datetime'])):
        for j in range(len(persistence_ap_lists)):
            persistence_ap_lists[j].append(ap_values[i])

    ap_dict = {'Forecast Issued': df_real_ap['Datetime']}
    for i in range(len(persistence_ap_lists)):
        ap_dict[f'{3*(i+1)}hrap'] = np.array(persistence_ap_lists[i], dtype=float)

    df_persistence_ap_3day = pd.DataFrame(ap_dict)

    df_persistence_ap_3day_filtered = df_persistence_ap_3day[df_persistence_ap_3day.index % 8 == 0].copy()

    df_persistence_ap_3day_filtered['Forecast Issued'] = df_persistence_ap_3day_filtered['Forecast Issued'].str[:-9]

    df_persistence_ap_3day_filtered.to_csv(f'{save_path_lead}/persistence_3day_3hr_ap.csv', index=False)

    return df_persistence_ap_3day_filtered


def create_3day_Ap_recurrence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('extracted_data/daily_Ap.csv')

    recurrence_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'][27:])):
        for j in range(len(recurrence_Ap_lists)):
            recurrence_Ap_lists[j].append(Ap_values[i+j])

    Ap_dict = {'Forecast Issued': df_real_Ap['Datetime'][27:]}
    for i in range(len(recurrence_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(recurrence_Ap_lists[i], dtype=int)

    df_recurrence_Ap_3day = pd.DataFrame(Ap_dict)

    df_recurrence_Ap_3day.to_csv(f'{save_path_lead}/recurrence_3day_daily_Ap.csv', index=False)

    return df_recurrence_Ap_3day


def create_3day_Kp_recurrence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('extracted_data/3hour_Kp.csv')

    recurrence_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'][27*8:])):
        for j in range(len(recurrence_Kp_lists)):
            recurrence_Kp_lists[j].append(Kp_values[i+j])

    Kp_dict = {'Forecast Issued': df_real_Kp['Datetime'][27*8:]}
    for i in range(len(recurrence_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(recurrence_Kp_lists[i], dtype=float)

    df_recurrence_Kp_3day = pd.DataFrame(Kp_dict)

    df_recurrence_Kp_3day_filtered = df_recurrence_Kp_3day[df_recurrence_Kp_3day.index % 8 == 0].copy()

    df_recurrence_Kp_3day_filtered['Forecast Issued'] = df_recurrence_Kp_3day_filtered['Forecast Issued'].str[:-9]

    df_recurrence_Kp_3day_filtered.to_csv(f'{save_path_lead}/recurrence_3day_3hr_Kp.csv', index=False)

    return df_recurrence_Kp_3day_filtered


def create_3day_ap_recurrence_forecast(test=False):

    if test is False:
        save_path_lead = 'baseline_forecasts'
    else:
        save_path_lead = test

    df_real_ap = pd.read_csv('extracted_data/3hour_ap.csv')

    recurrence_ap_lists = make_Kp_storage_list()

    ap_values = df_real_ap['ap'].values
    for i in range(len(df_real_ap['Datetime'][27*8:])):
        for j in range(len(recurrence_ap_lists)):
            recurrence_ap_lists[j].append(ap_values[i+j])

    ap_dict = {'Forecast Issued': df_real_ap['Datetime'][27*8:]}
    for i in range(len(recurrence_ap_lists)):
        ap_dict[f'{3*(i+1)}hrap'] = np.array(recurrence_ap_lists[i], dtype=float)

    df_recurrence_ap_3day = pd.DataFrame(ap_dict)

    df_recurrence_ap_3day_filtered = df_recurrence_ap_3day[df_recurrence_ap_3day.index % 8 == 0].copy()

    df_recurrence_ap_3day_filtered['Forecast Issued'] = df_recurrence_ap_3day_filtered['Forecast Issued'].str[:-9]

    df_recurrence_ap_3day_filtered.to_csv(f'{save_path_lead}/recurrence_3day_3hr_ap.csv', index=False)

    return df_recurrence_ap_3day_filtered