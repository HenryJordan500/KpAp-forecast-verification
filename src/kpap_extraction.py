import pandas as pd
import datetime as dt

def extract_Ap(Ap_file):

    full_data_df = pd.read_csv(filepath_or_buffer='data/' + Ap_file,
                               sep=r'\s+',
                               skiprows=39)
    
    year_mm_dd = full_data_df[['#YYY', 'MM', 'DD']].copy()

    year_mm_dd = year_mm_dd.rename(columns={'#YYY': 'year', 'MM': 'month', 'DD': 'day'})

    dates = pd.to_datetime(year_mm_dd)
    
    Ap_df = pd.DataFrame({'Datetime': dates, 'Ap': full_data_df['Ap']})

    # Add thing to deal with bad Ap values
    
    Ap_df.to_csv('Ap.csv', index=False)

    return 


# Inputs

# Function to get Kp and ap
# Function to get Ap
# Function to remove bad values (-1.000 Kp, -1 ap)

# Outputs:
# Csv with Kp for each time
# Csv with ap for each time
# Csv with daily Ap

def main():

    Ap_file = 'Kp_ap_Ap_SN_F107_since_1932.txt'

    extract_Ap(Ap_file=Ap_file)

    return

if __name__ == '__main__':

    main()