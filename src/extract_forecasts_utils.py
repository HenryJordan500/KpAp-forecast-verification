import numpy as np
import pandas as pd

import datetime as dt
from pathlib import Path

def fill_nans_func(df):

    df = df.set_index('date')
    full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df = df.reindex(full_range)
    df = df.reset_index().rename(columns={'index': 'date'})

    return df

def extract_daypre_ap_from_file(file, ap_lists):

    with open(file, 'r', encoding='utf-8') as f:

        for line in f:
            
            if 'A_Planetary' in line:
                
                parts = line.split()

                ap_lists[0].append(parts[1])
                ap_lists[1].append(parts[2])
                ap_lists[2].append(parts[3])
                continue
            
    return

def extract_geomag_forecast_kp_from_file(file, kp_lists):

    with open(file, 'r', encoding='utf-8') as f:
        
            lines = [line for line in f]

            for i in range(len(lines)):

                if '00-03UT' in lines[i]:

                    lines = lines[i:i+8]

                    break
            
            for i in range(len(lines)):
                
                parts = lines[i].split()

                kp_lists[i].append(parts[1])
                kp_lists[i+8].append(parts[2])
                kp_lists[i+16].append(parts[3])

    return

def extract_geomag_forecast_ap_from_file(file, ap_lists):

    with open(file, 'r', encoding='utf-8') as f:

        for line in f:
            
            if 'Predicted Ap' in line:
                
                parts = line.split()
                ap_vals = parts[-1]
            
                ap_lists[0].append(ap_vals[:3])
                ap_lists[1].append(ap_vals[4:7])
                ap_lists[2].append(ap_vals[8:])
                continue
            
    return

def get_daypre_forecast(fill_nans=True, test=False):

    if test is False:
        dir_path = Path(f'raw_data/daypre')
        save_path_lead = 'processed_data'
    else:
        dir_path = Path(f'testing/resources/testing_files/testing_daypre')
        save_path_lead = test

    last_ind = 8
    raw_dt_strings = [p.name[:last_ind] for p in dir_path.iterdir() if p.is_file()]
    raw_file_strings = [p for p in dir_path.iterdir() if p.is_file()]
    unsorted_dt_list = np.array([dt.date(year=int(p[0:4]), month=int(p[4:6]), day=int(p[6:8])) for p in raw_dt_strings], dtype='datetime64[ns]')
    
    # Initialize lists to store daily Ap forecast
    ap_lists = [[] for i in range(3)]

    # Extract daily Ap forecast
    for file in raw_file_strings:

        extract_daypre_ap_from_file(file=file, ap_lists=ap_lists)
    
    ap_dict = {'date': unsorted_dt_list}
    for i in range(len(ap_lists)):
        ap_dict[f'{i+1}dAp'] = np.array(ap_lists[i], dtype=int)

    # Store in dataframe       
    df_daypre = pd.DataFrame(ap_dict)
    
    # Sort dataframe so that dates are in order
    df_daypre.sort_values('date', inplace=True)
    df_daypre.set_index(pd.Index([i for i in range(0, len(df_daypre['date']))]), inplace=True)

    if fill_nans is True:
        df_daypre = fill_nans_func(df=df_daypre)

    # if fill_nans is True:
        
    #     df_daypre = df_daypre.set_index('date')
    #     full_range = pd.date_range(start=df_daypre.index.min(), end=df_daypre.index.max(), freq='D')
    #     df_daypre = df_daypre.reindex(full_range)
    #     df_daypre = df_daypre.reset_index().rename(columns={'index': 'date'})

    df_daypre.to_csv(f'{save_path_lead}/daypre_3dayAp.csv')
    
    return df_daypre


def get_geomag_forecast(fill_nans=True, test=False):
    
    if test is False:
        dir_path = Path(f'raw_data/geomag_forecast')
        save_path_lead = 'processed_data'
    else:
        dir_path = Path(f'testing/resources/testing_files/testing_geomag_forecast')
        save_path_lead = test
        

    last_ind = 8
    raw_dt_strings = [p.name[:last_ind] for p in dir_path.iterdir() if p.is_file()]
    raw_file_strings = [p for p in dir_path.iterdir() if p.is_file()]
    unsorted_dt_list = np.array([dt.date(year=int(p[0:4]), month=int(p[4:6]), day=int(p[6:8])) for p in raw_dt_strings], dtype='datetime64[ns]')

    kp_lists = [[] for i in range(24)]
    ap_lists = [[] for i in range(3)]
    
    # Extract Kp forecast
    for file in raw_file_strings:

        extract_geomag_forecast_kp_from_file(file=file,
                             kp_lists=kp_lists)
        extract_geomag_forecast_ap_from_file(file=file,
                                             ap_lists=ap_lists)
        
    kp_dict = {'date': unsorted_dt_list}
    for i in range(len(kp_lists)):
        kp_dict[f'{3*(i+1)}hrKp'] = np.array(kp_lists[i], dtype=float)

    ap_dict = {'date': unsorted_dt_list}
    for i in range(len(ap_lists)):
        ap_dict[f'{i+1}dAp'] = np.array(ap_lists[i], dtype=int)

    # Store in dataframe               
    df_geomag_forecast_Kp = pd.DataFrame(kp_dict)
    df_geomag_forecast_Ap = pd.DataFrame(ap_dict)
    
    # Sort dataframe so that dates are in order
    df_geomag_forecast_Kp.sort_values('date', inplace=True)
    df_geomag_forecast_Kp.set_index(pd.Index([i for i in range(0, len(df_geomag_forecast_Kp['date']))]), inplace=True)

    df_geomag_forecast_Ap.sort_values('date', inplace=True)
    df_geomag_forecast_Ap.set_index(pd.Index([i for i in range(0, len(df_geomag_forecast_Ap['date']))]), inplace=True)

    # Fill missing forecast dates with Nan
    if fill_nans is True:
        df_geomag_forecast_Kp = fill_nans_func(df=df_geomag_forecast_Kp)
        df_geomag_forecast_Ap = fill_nans_func(df=df_geomag_forecast_Ap)

    df_geomag_forecast_Kp.to_csv(f'{save_path_lead}/geomag_forecast_3dayKp.csv')
    df_geomag_forecast_Ap.to_csv(f'{save_path_lead}/geomag_forecast_3dayAp.csv')
    
    return df_geomag_forecast_Kp, df_geomag_forecast_Ap

def extract_the_weekly_ap_from_file():
    return

def extract_the_weekly_kp_from_file():
    return

def get_the_weekly_forecast():
    return

def extract_three_day_forecast_kp_from_file():
    return

def get_three_day_forecast():
    return

def combine_daypre_geomag_ap_forecasts():
    return

