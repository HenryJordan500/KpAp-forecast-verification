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
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('processed_data/daily_Ap.csv')

    real_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'])-3):
        for j in range(len(real_Ap_lists)):
            real_Ap_lists[j].append(Ap_values[i+j+1])

    Ap_dict = {'date': df_real_Ap['Datetime'][:-3]}
    for i in range(len(real_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(real_Ap_lists[i], dtype=int)

    df_real_Ap_3day = pd.DataFrame(Ap_dict)

    df_real_Ap_3day.to_csv(f'{save_path_lead}/real_3dayAp.csv', index=False)

    return df_real_Ap_3day


def create_3day_Kp_from_real_vals(test=False):

    if test is False:
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('processed_data/3hour_Kp.csv')

    real_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'])-24):
        for j in range(len(real_Kp_lists)):
            real_Kp_lists[j].append(Kp_values[i+j+1])

    Kp_dict = {'date': df_real_Kp['Datetime'][:-24]}
    for i in range(len(real_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(real_Kp_lists[i], dtype=float)
    
    df_real_Kp_3day = pd.DataFrame(Kp_dict)

    df_real_Kp_3day_filtered = df_real_Kp_3day[df_real_Kp_3day.index % 8 == 0].copy()

    df_real_Kp_3day_filtered['date'] = df_real_Kp_3day_filtered['date'].str[:-9]

    df_real_Kp_3day.to_csv(f'{save_path_lead}/real_3dayKp.csv', index=False)

    return df_real_Kp_3day_filtered


def create_3day_Ap_persistence_forecast(test=False):

    if test is False:
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('processed_data/daily_Ap.csv')

    persistence_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'])):
        for j in range(len(persistence_Ap_lists)):
            persistence_Ap_lists[j].append(Ap_values[i])

    Ap_dict = {'date': df_real_Ap['Datetime']}
    for i in range(len(persistence_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(persistence_Ap_lists[i], dtype=int)

    df_persistence_Ap_3day = pd.DataFrame(Ap_dict)

    df_persistence_Ap_3day.to_csv(f'{save_path_lead}/persistence_3dayAp.csv')

    return df_persistence_Ap_3day


def create_3day_Kp_persistence_forecast(test=False):

    if test is False:
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('processed_data/3hour_Kp.csv')

    persistence_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'])):
        for j in range(len(persistence_Kp_lists)):
            persistence_Kp_lists[j].append(Kp_values[i])

    Kp_dict = {'date': df_real_Kp['Datetime']}
    for i in range(len(persistence_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(persistence_Kp_lists[i], dtype=float)

    df_persistence_Kp_3day = pd.DataFrame(Kp_dict)

    df_persistence_Kp_3day_filtered = df_persistence_Kp_3day[df_persistence_Kp_3day.index % 8 == 0].copy()

    df_persistence_Kp_3day_filtered['date'] = df_persistence_Kp_3day_filtered['date'].str[:-9]

    df_persistence_Kp_3day_filtered.to_csv(f'{save_path_lead}/persistence_3dayKp.csv')

    return df_persistence_Kp_3day_filtered


def create_3day_Ap_recurrence_forecast(test=False):

    if test is False:
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Ap = pd.read_csv('processed_data/daily_Ap.csv')

    recurrence_Ap_lists = make_Ap_storage_list()

    Ap_values = df_real_Ap['Ap'].values
    for i in range(len(df_real_Ap['Datetime'][27:])):
        for j in range(len(recurrence_Ap_lists)):
            recurrence_Ap_lists[j].append(Ap_values[i+j])

    Ap_dict = {'date': df_real_Ap['Datetime'][27:]}
    for i in range(len(recurrence_Ap_lists)):
        Ap_dict[f'{i+1}dAp'] = np.array(recurrence_Ap_lists[i], dtype=int)

    df_recurrence_Ap_3day = pd.DataFrame(Ap_dict)

    df_recurrence_Ap_3day.to_csv(f'{save_path_lead}/recurrence_3dayAp.csv')

    return df_recurrence_Ap_3day


def create_3day_Kp_recurrence_forecast(test=False):

    if test is False:
        save_path_lead = 'processed_data'
    else:
        save_path_lead = test

    df_real_Kp = pd.read_csv('processed_data/3hour_Kp.csv')

    recurrence_Kp_lists = make_Kp_storage_list()

    Kp_values = df_real_Kp['Kp'].values
    for i in range(len(df_real_Kp['Datetime'][27*8:])):
        for j in range(len(recurrence_Kp_lists)):
            recurrence_Kp_lists[j].append(Kp_values[i+j])

    Kp_dict = {'date': df_real_Kp['Datetime'][27*8:]}
    for i in range(len(recurrence_Kp_lists)):
        Kp_dict[f'{3*(i+1)}hrKp'] = np.array(recurrence_Kp_lists[i], dtype=float)

    df_recurrence_Kp_3day = pd.DataFrame(Kp_dict)

    df_recurrence_Kp_3day_filtered = df_recurrence_Kp_3day[df_recurrence_Kp_3day.index % 8 == 0].copy()

    df_recurrence_Kp_3day_filtered['date'] = df_recurrence_Kp_3day_filtered['date'].str[:-9]

    df_recurrence_Kp_3day_filtered.to_csv(f'{save_path_lead}/recurrence_3dayKp.csv')

    return df_recurrence_Kp_3day_filtered