import numpy as np
import pandas as pd

import datetime as dt
from pathlib import Path

def fill_nans_func(df):

    df = df.set_index('Forecast Issued')
    full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df = df.reindex(full_range)
    df = df.reset_index().rename(columns={'index': 'Forecast Issued'})

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
        save_path_lead = 'extracted_data'
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
    
    ap_dict = {'Forecast Issued': unsorted_dt_list}
    for i in range(len(ap_lists)):
        ap_dict[f'{i+1}dAp'] = np.array(ap_lists[i], dtype=int)

    # Store in dataframe       
    df_daypre = pd.DataFrame(ap_dict)
    
    # Sort dataframe so that dates are in order
    df_daypre.sort_values('Forecast Issued', inplace=True)
    df_daypre.set_index(pd.Index([i for i in range(0, len(df_daypre['Forecast Issued']))]), inplace=True)

    if fill_nans is True:
        df_daypre = fill_nans_func(df=df_daypre)

    df_daypre.to_csv(f'{save_path_lead}/daypre_3day_daily_Ap.csv', index=False)
    
    return df_daypre


def get_geomag_forecast(fill_nans=True, test=False):
    
    if test is False:
        dir_path = Path(f'raw_data/geomag_forecast')
        save_path_lead = 'extracted_data'
    else:
        dir_path = Path(f'testing/resources/testing_files/testing_geomag_forecast')
        save_path_lead = test
        

    last_ind = 8
    raw_dt_strings = [p.name[:last_ind] for p in dir_path.iterdir() if p.is_file() and p.name[0] != "."]
    raw_file_strings = [p for p in dir_path.iterdir() if p.is_file() and p.name[0] != "."]
    unsorted_dt_list = np.array([dt.date(year=int(p[0:4]), month=int(p[4:6]), day=int(p[6:8])) for p in raw_dt_strings], dtype='datetime64[ns]')

    kp_lists = [[] for i in range(24)]
    ap_lists = [[] for i in range(3)]
    
    # Extract Kp forecast
    for file in raw_file_strings:

        extract_geomag_forecast_kp_from_file(file=file,
                                             kp_lists=kp_lists)
        extract_geomag_forecast_ap_from_file(file=file,
                                             ap_lists=ap_lists)
        
    kp_dict = {'Forecast Issued': unsorted_dt_list}
    for i in range(len(kp_lists)):
        kp_dict[f'{3*(i+1)}hrKp'] = np.array(kp_lists[i], dtype=float)

    ap_dict = {'Forecast Issued': unsorted_dt_list}
    for i in range(len(ap_lists)):
        ap_dict[f'{i+1}dAp'] = np.array(ap_lists[i], dtype=int)

    # Store in dataframe               
    df_geomag_forecast_Kp = pd.DataFrame(kp_dict)
    df_geomag_forecast_Ap = pd.DataFrame(ap_dict)
    
    # Sort dataframe so that dates are in order
    df_geomag_forecast_Kp.sort_values('Forecast Issued', inplace=True)
    df_geomag_forecast_Kp.set_index(pd.Index([i for i in range(0, len(df_geomag_forecast_Kp['Forecast Issued']))]), inplace=True)

    df_geomag_forecast_Ap.sort_values('Forecast Issued', inplace=True)
    df_geomag_forecast_Ap.set_index(pd.Index([i for i in range(0, len(df_geomag_forecast_Ap['Forecast Issued']))]), inplace=True)

    # Fill missing forecast dates with Nan
    if fill_nans is True:
        df_geomag_forecast_Kp = fill_nans_func(df=df_geomag_forecast_Kp)
        df_geomag_forecast_Ap = fill_nans_func(df=df_geomag_forecast_Ap)

    df_geomag_forecast_Kp.to_csv(f'{save_path_lead}/geomag_forecast_3day_3hr_Kp.csv', index=False)
    df_geomag_forecast_Ap.to_csv(f'{save_path_lead}/geomag_forecast_3day_daily_Ap.csv', index=False)
    
    return df_geomag_forecast_Kp, df_geomag_forecast_Ap


def extract_Kp_from_SWPC_sheet(fill_nans=True, test=False):

    if test is False:
        file_path = Path('raw_data/SWPC_Kp_Forecasts_2011_2025.csv')
        save_path_lead = 'extracted_data'
    else:
        file_path = Path('testing/resources/testing_files/testing_SWPC_Kp_Forecasts_2011_2025.csv')
        save_path_lead = test

    df = pd.read_csv(file_path)

    # Parse issue date and lead day number ('day3' -> 3)
    df['Forecast Issued'] = pd.to_datetime(df['Forecast Day'], format='%m/%d/%Y')
    df['day'] = df['Day after forecast'].str.replace('day', '').astype(int)

    slot_cols = [c for c in df.columns if 'UTC' in c]  # 8 three-hour slots in time order
    n_days = df['day'].max()

    # Long (one row per issue date + lead day) -> wide (one row per issue date)
    df_wide = df.pivot(index='Forecast Issued', columns='day', values=slot_cols)

    # Order columns day1 slots 00-03..21-00, then day2, etc.
    ordered_cols = [(slot, day) for day in range(1, n_days + 1) for slot in slot_cols]
    df_wide = df_wide[ordered_cols]
    df_wide.columns = [f'{3*(i+1)}hrKp' for i in range(len(ordered_cols))]

    df_SWPC_Kp_7day = df_wide.round(2).sort_index().reset_index()

    # Fill missing forecast dates with Nan
    if fill_nans is True:
        df_SWPC_Kp_7day = fill_nans_func(df=df_SWPC_Kp_7day)

    # 3 day forecast: issue date + first 24 three-hour lead times (3hrKp..72hrKp)
    df_SWPC_Kp_3day = df_SWPC_Kp_7day[['Forecast Issued'] + [f'{3*(i+1)}hrKp' for i in range(24)]]

    df_SWPC_Kp_7day.to_csv(f'{save_path_lead}/SWPC_7day_3hr_Kp.csv', index=False)
    df_SWPC_Kp_3day.to_csv(f'{save_path_lead}/SWPC_3day_3hr_Kp.csv', index=False)

    return df_SWPC_Kp_7day, df_SWPC_Kp_3day


def round_decimal(num):

    int_part = int(num)
    decimal = num - int_part
    rounded_decimal = round(decimal, 2)
    
    return rounded_decimal + int_part


def convert_Kp_to_ap(Kp):

    Kp = round_decimal(Kp)
    
    Kp_vals = [0.0, 0.33, 0.67, 1.0, 1.33, 1.67, 2.0,
               2.33, 2.67, 3.0, 3.33, 3.67, 4.0, 4.33,
               4.67, 5.0, 5.33, 5.67, 6.0, 6.33, 6.67,
               7.0, 7.33, 7.67, 8.0, 8.33, 8.67, 9.0]

    ap_vals = [0, 2, 3, 4, 5, 6, 7,
               9, 12, 15, 18, 22, 27, 32,
               39, 48, 56, 67, 80, 94, 111,
               132, 154, 179, 207, 236, 300, 400]

    converted_ap = ap_vals[Kp_vals.index(Kp)]

    return converted_ap


def convert_Kp_forecast_to_ap(file_path):

    file_path = Path(file_path)
    df = pd.read_csv(file_path)

    kp_cols = [c for c in df.columns if c.endswith('Kp')]

    # Convert each Kp value to ap, leaving missing values as NaN
    for col in kp_cols:
        df[col] = df[col].apply(lambda Kp: np.nan if pd.isna(Kp) else convert_Kp_to_ap(Kp))

    # Rename columns 3hrKp -> 3hrap
    df = df.rename(columns={c: c[:-2] + 'ap' for c in kp_cols})
    df['Forecast Issued'] = pd.to_datetime(df['Forecast Issued'])

    save_path = file_path.with_name(file_path.name.replace('Kp', 'ap'))
    df.to_csv(save_path, index=False)

    return df

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


def main():

    #convert_Kp_to_ap(0.67)
    print(round_decimal(12.456))

if __name__ == '__main__':

    main()

