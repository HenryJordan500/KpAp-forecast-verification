import pandas as pd

def convert_datetime(data_df):

    # Assume only year, month, day are to be converted
    date_keys = ['#YYY', 'MM', 'DD']
    new_columns = {'#YYY': 'year', 'MM': 'month', 'DD': 'day'}

    # If hours column exists in array, add it to conversion
    if 'hh.h' in data_df.keys().to_list():

        new_columns['hh.h'] = 'hours'
        date_keys.append('hh.h')

    date_slice = data_df[date_keys].copy()

    # Rename columns to what to_datetime expects
    date_slice = date_slice.rename(columns=new_columns)

    datetimes = pd.to_datetime(date_slice)

    return datetimes


def extract_Ap(Ap_file):

    full_data_df = pd.read_csv(filepath_or_buffer='raw_data/' + Ap_file,
                               sep=r'\s+',
                               skiprows=39)
    
    year_mm_dd = full_data_df[['#YYY', 'MM', 'DD']].copy()

    year_mm_dd = year_mm_dd.rename(columns={'#YYY': 'year', 'MM': 'month', 'DD': 'day'})

    dates = pd.to_datetime(year_mm_dd)
    
    Ap_df = pd.DataFrame({'Datetime': dates, 'Ap': full_data_df['Ap']})

    # No missing data values in Ap
    # Guessing they just averaged the data available for the day
    Ap_df.to_csv('processed_data/daily_Ap.csv', index=False)

    return 

def extract_Kp(Kp_file):

    full_data_df = pd.read_csv(filepath_or_buffer='raw_data/' + Kp_file,
                               sep=r'\s+',
                               skiprows=29)
    
    year_mm_dd_hh = full_data_df[['#YYY', 'MM', 'DD', 'hh.h']].copy()

    year_mm_dd_hh = year_mm_dd_hh.rename(columns={'#YYY': 'year', 'MM': 'month', 'DD': 'day', 'hh.h': 'hour'})

    dates = pd.to_datetime(year_mm_dd_hh)

    Kp_df = pd.DataFrame({'Datetime': dates, 'Kp': full_data_df['Kp']})

    Kp_df.to_csv('processed_data/3hour_Kp.csv', index=False)

    return


def extract_ap(ap_file):

    full_data_df = pd.read_csv(filepath_or_buffer='raw_data/' + ap_file,
                               sep=r'\s+',
                               skiprows=29)
    
    year_mm_dd_hh = full_data_df[['#YYY', 'MM', 'DD', 'hh.h']].copy()

    year_mm_dd_hh = year_mm_dd_hh.rename(columns={'#YYY': 'year', 'MM': 'month', 'DD': 'day', 'hh.h': 'hour'})

    dates = pd.to_datetime(year_mm_dd_hh)

    ap_df = pd.DataFrame({'Datetime': dates, 'ap': full_data_df['ap']})

    ap_df.to_csv('processed_data/3hour_ap.csv', index=False)

    return



# 


# Inputs

# Function to get Kp and ap
# Function to get Ap
# Function to remove bad values (-1.000 Kp, -1 ap)

# Outputs:
# Csv with Kp for each time
# Csv with ap for each time
# Csv with daily Ap

def main():

    return

if __name__ == '__main__':

    main()