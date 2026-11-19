import numpy as np
import pandas as pd

import re
import datetime as dt
from pathlib import Path

TIME_COLS = ['Forecast Issued', 'Forecast Start', 'Start Offset (hr)']


def forecast_time_columns(issue_times, start_times):
    """
    Builds the three time columns that lead every forecast dataframe.

    Parameters
    ----------
    issue_times: array-like of datetimes
        When each forecast was issued.
    start_times: array-like of datetimes
        Start (00 UT) of the first period in each forecast's table, i.e. the start of
        the 3hrKp slot or the 1dAp day.

    Returns
    -------
    time_cols: dict
        'Forecast Issued', 'Forecast Start' and 'Start Offset (hr)' (Start - Issued, in hours,
        rounded to 0.01; negative when the table begins before the issue time).
    """

    issued = np.array(issue_times, dtype='datetime64[ns]')
    start = np.array(start_times, dtype='datetime64[ns]')
    offset = np.round((start - issued) / np.timedelta64(1, 'h'), 2)

    return {'Forecast Issued': issued, 'Forecast Start': start, 'Start Offset (hr)': offset}


def save_forecast_csv(df, file_path):
    """
    Writes a forecast dataframe to csv with 'Forecast Start' always shown as a full UTC
    time (e.g. '2022-11-15 00:00:00').

    pandas drops the time from a datetime column when every value is at midnight, which
    would hide that Forecast Start is the start time of the first forecast bin.

    Parameters
    ----------
    df: pandas.DataFrame
        Forecast dataframe. It is not modified.
    file_path: (str | pathlib.Path)
        Where to write the csv.
    """

    df_out = df.copy()

    if 'Forecast Start' in df_out.columns:
        df_out['Forecast Start'] = df_out['Forecast Start'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df_out.to_csv(file_path, index=False)


def infer_missing_forecast_start(df):
    """
    Fills 'Forecast Start' for slots that have no report.

    A missing slot gets slot + the most common (Forecast Start - slot) gap among reports
    in slots at the same time of day. E.g. geomag_forecast reports always start the day
    after issue, so a missing 2022-11-16 slot gets Forecast Start 2022-11-17 00:00.

    Parameters
    ----------
    df: pandas.DataFrame
        Forecast dataframe indexed by issue slot, with a 'Forecast Start' column.

    Returns
    -------
    forecast_start: pandas.Series
        'Forecast Start' with missing values inferred. Stays NaT if no report shares that slot's time of day.
    """

    slots = df.index.to_series()
    gap = df['Forecast Start'] - slots
    slot_time_of_day = slots - slots.dt.floor('D')

    typical_gap = gap.groupby(slot_time_of_day).transform(lambda g: g.mode().iloc[0] if g.notna().any() else pd.NaT)

    return df['Forecast Start'].fillna(slots + typical_gap)


def fill_nans_func(df, freq='D', slots=None):
    """
    Inserts an all-NaN row for every issue slot with no report.

    Each report is assigned to the slot of length freq that contains its issue time
    (Forecast Issued floored to freq). So a report issued at 22:05 fills the slot for
    its day without needing to sit on a grid point.

    Parameters
    ----------
    df: pandas.DataFrame
        Forecast dataframe with a datetime 'Forecast Issued' column, at most one report per slot.
    freq: str, optional
        Issue cadence of the report, as a pandas frequency string. Default is 'D' (one report per day).
    slots: array-like of datetimes, optional
        Slot of each report, one per row of df, used instead of Forecast Issued. Use it when a
        report's issue time can fall outside its own slot (e.g. a 1230 three_day_forecast
        issued late, after midnight). Each value is floored to freq.

    Returns
    -------
    df: pandas.DataFrame
        One row per slot from the first to the last report, in order. Missing slots have
        'Forecast Issued' = NaT, 'Start Offset (hr)' and forecast values NaN, and an inferred
        'Forecast Start' (see infer_missing_forecast_start) if that column exists.
    """

    if slots is None:
        slots = df['Forecast Issued'].dt.floor(freq)
    else:
        slots = pd.Series(pd.to_datetime(slots), index=df.index).dt.floor(freq)

    if slots.duplicated().any():
        duplicate_slots = sorted(set(slots[slots.duplicated()]))
        raise ValueError(f'More than one report issued in the same {freq} slot: {duplicate_slots}')

    full_range = pd.date_range(start=slots.min(), end=slots.max(), freq=freq)

    # Index by slot (the 'Forecast Issued' column is kept) and insert missing slots
    df = df.set_index(slots).reindex(full_range)

    if 'Forecast Start' in df.columns:
        df['Forecast Start'] = infer_missing_forecast_start(df)

    df = df.reset_index(drop=True)

    return df


def extract_issue_time_from_file(file):
    """
    Reads the issue time from the header of a SWPC text product.

    The header line looks like ':Issued: 2022 Nov 14 2205 UTC'. three_day_forecast
    reports write it without the leading ':'.

    Parameters
    ----------
    file: (str | pathlib.Path)
        Path to the report.

    Returns
    -------
    issue_time: dt.datetime
        Issue time of the report in UTC.
    """

    with open(file, 'r', encoding='utf-8') as f:

        for line in f:

            if line.lstrip(':').startswith('Issued:'):

                parts = line.split()

                return dt.datetime.strptime(' '.join(parts[1:5]), '%Y %b %d %H%M')

    raise ValueError(f'No issue time found in {file}')


def extract_kp_table_start_from_file(file, issue_time):
    """
    Reads the first day of the 3 hourly Kp table in a geomag_forecast or three_day_forecast report.

    The table header (the line above '00-03UT') looks like '   Nov 15    Nov 16    Nov 17'
    and has no year, so the year is taken from issue_time, then moved forward for a report
    issued in December whose table starts in January, or back for one issued in January
    whose table starts in December (a late three_day_forecast).

    Parameters
    ----------
    file: (str | pathlib.Path)
        Path to the report.
    issue_time: dt.datetime
        Issue time of the report, from extract_issue_time_from_file.

    Returns
    -------
    forecast_start: dt.datetime
        00 UT on the first day of the Kp table.
    """

    with open(file, 'r', encoding='utf-8') as f:
        lines = [line for line in f]

    for i in range(len(lines)):

        if '00-03UT' in lines[i]:

            parts = lines[i-1].split()
            forecast_start = dt.datetime.strptime(f'{issue_time.year} {parts[0]} {parts[1]}', '%Y %b %d')

            # Report issued in December forecasting January
            if (forecast_start - issue_time).days < -180:
                forecast_start = forecast_start.replace(year=forecast_start.year + 1)
            # Report issued in January with a table starting in December
            elif (forecast_start - issue_time).days > 180:
                forecast_start = forecast_start.replace(year=forecast_start.year - 1)

            return forecast_start

    raise ValueError(f'No Kp table found in {file}')


def extract_geomag_forecast_start_from_file(file, issue_time):
    """
    Reads the first day of the Kp table in a geomag_forecast report (the day after issue).
    See extract_kp_table_start_from_file.
    """

    return extract_kp_table_start_from_file(file, issue_time)


def extract_three_day_forecast_start_from_file(file, issue_time):
    """
    Reads the first day of the Kp table in a three_day_forecast report (normally the issue
    day, for both the 0030 and 1230 reports). See extract_kp_table_start_from_file.
    """

    return extract_kp_table_start_from_file(file, issue_time)


def extract_three_day_forecast_slot_from_file_name(file):
    """
    Nominal issue slot of a three_day_forecast report, from the 12 character timestamp at the
    start of its file name (e.g. '202203251230three_day_forecast.txt' -> 2022-03-25 12:30).

    The 0030 and 1230 reports are occasionally issued late (a 1230 report issued at 00:20 the
    next day), so the header issue time can fall in the next report's 12 hr slot. The file name
    keeps the slot the report belongs to.

    Returns
    -------
    slot_time: dt.datetime
        Timestamp from the file name (not floored).
    """

    return dt.datetime.strptime(Path(file).name[:12], '%Y%m%d%H%M')


def extract_daypre_forecast_start_from_file(file):
    """
    Reads the first prediction date of a daypre report from its
    ':Prediction_dates:   2013 Dec 23   2013 Dec 24   2013 Dec 25' line.

    Returns
    -------
    forecast_start: dt.datetime
        00 UT on the first prediction date.
    """

    with open(file, 'r', encoding='utf-8') as f:

        for line in f:

            if line.startswith(':Prediction_dates:'):

                parts = line.split()

                return dt.datetime.strptime(' '.join(parts[1:4]), '%Y %b %d')

    raise ValueError(f'No prediction dates found in {file}')


def list_report_files(dir_path):
    """
    Lists the report files in a directory, skipping hidden files such as .DS_Store.

    Returns
    -------
    files: list
        Sorted list of pathlib.Path objects.
    """

    return sorted(p for p in Path(dir_path).iterdir() if p.is_file() and p.name[0] != ".")

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

    raw_file_strings = list_report_files(dir_path)
    issue_times = [extract_issue_time_from_file(p) for p in raw_file_strings]
    start_times = [extract_daypre_forecast_start_from_file(p) for p in raw_file_strings]

    # Initialize lists to store daily Ap forecast
    ap_lists = [[] for i in range(3)]

    # Extract daily Ap forecast
    for file in raw_file_strings:

        extract_daypre_ap_from_file(file=file, ap_lists=ap_lists)

    ap_dict = forecast_time_columns(issue_times, start_times)
    for i in range(len(ap_lists)):
        ap_dict[f'{i+1}dAp'] = np.array(ap_lists[i], dtype=int)

    # Store in dataframe       
    df_daypre = pd.DataFrame(ap_dict)
    
    # Sort dataframe so that dates are in order
    df_daypre.sort_values('Forecast Issued', inplace=True)
    df_daypre.set_index(pd.Index([i for i in range(0, len(df_daypre['Forecast Issued']))]), inplace=True)

    if fill_nans is True:
        df_daypre = fill_nans_func(df=df_daypre)

    save_forecast_csv(df_daypre, f'{save_path_lead}/daypre_3day_daily_Ap.csv')
    
    return df_daypre


def get_geomag_forecast(fill_nans=True, test=False):
    
    if test is False:
        dir_path = Path(f'raw_data/geomag_forecast')
        save_path_lead = 'extracted_data'
    else:
        dir_path = Path(f'testing/resources/testing_files/testing_geomag_forecast')
        save_path_lead = test
        

    raw_file_strings = list_report_files(dir_path)
    issue_times = [extract_issue_time_from_file(p) for p in raw_file_strings]
    start_times = [extract_geomag_forecast_start_from_file(p, t) for p, t in zip(raw_file_strings, issue_times)]

    kp_lists = [[] for i in range(24)]
    ap_lists = [[] for i in range(3)]
    
    # Extract Kp forecast
    for file in raw_file_strings:

        extract_geomag_forecast_kp_from_file(file=file,
                                             kp_lists=kp_lists)
        extract_geomag_forecast_ap_from_file(file=file,
                                             ap_lists=ap_lists)
        
    # The Ap and Kp tables in a geomag_forecast report start on the same day
    kp_dict = forecast_time_columns(issue_times, start_times)
    for i in range(len(kp_lists)):
        kp_dict[f'{3*(i+1)}hrKp'] = np.array(kp_lists[i], dtype=float)

    ap_dict = forecast_time_columns(issue_times, start_times)
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

    save_forecast_csv(df_geomag_forecast_Kp, f'{save_path_lead}/geomag_forecast_3day_3hr_Kp.csv')
    save_forecast_csv(df_geomag_forecast_Ap, f'{save_path_lead}/geomag_forecast_3day_daily_Ap.csv')
    
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

    df_wide = df_wide.round(2).sort_index()

    # day1 is the day after 'Forecast Day': its values match the geomag_forecast report issued
    # on 'Forecast Day' (which forecasts the next 3 days) for ~90% of dates, and no other offset matches.
    # The sheet has no issue time. It is declared issued at 00:00 on day1 (Forecast Day + 1), so
    # 'Start Offset (hr)' is 0. Forecasters have the 21-00UT slot of Forecast Day by then: they
    # sometimes revise day1 between the ~22 UT geomag_forecast and the 0030 three_day_forecast, and
    # the sheet carries some of those revisions (see notebooks/SWPC_forecast_origin.ipynb).
    forecast_days = df_wide.index
    issue_times = forecast_days + pd.Timedelta(days=1)
    start_times = forecast_days + pd.Timedelta(days=1)
    df_time_cols = pd.DataFrame(forecast_time_columns(issue_times, start_times))

    df_SWPC_Kp_7day = pd.concat([df_time_cols, df_wide.reset_index(drop=True)], axis=1)

    # Fill missing forecast dates with Nan
    if fill_nans is True:
        df_SWPC_Kp_7day = fill_nans_func(df=df_SWPC_Kp_7day)

    # 3 day forecast: time columns + first 24 three-hour lead times (3hrKp..72hrKp)
    df_SWPC_Kp_3day = df_SWPC_Kp_7day[TIME_COLS + [f'{3*(i+1)}hrKp' for i in range(24)]]

    save_forecast_csv(df_SWPC_Kp_7day, f'{save_path_lead}/SWPC_7day_3hr_Kp.csv')
    save_forecast_csv(df_SWPC_Kp_3day, f'{save_path_lead}/SWPC_3day_3hr_Kp.csv')

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
    for col in ['Forecast Issued', 'Forecast Start']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    save_path = file_path.with_name(file_path.name.replace('Kp', 'ap'))
    save_forecast_csv(df, save_path)

    return df

def extract_the_weekly_ap_from_file():
    return

def extract_the_weekly_kp_from_file():
    return

def get_the_weekly_forecast():
    return

def extract_three_day_forecast_kp_from_file(file, kp_lists):
    """
    Appends the 24 values of the 'NOAA Kp index breakdown' table of a three_day_forecast
    report to kp_lists, as strings.

    Rows look like '12-15UT       5.33 (G1)    4.67 (G1)    3.67'. The '(G1)' style NOAA
    scale tags are removed. Before 2022-11-15 the values are whole numbers ('5 (G1)').

    Parameters
    ----------
    file: (str | pathlib.Path)
        Path to the report.
    kp_lists: list
        24 lists, one per 3 hr lead time, ordered day 1 00-03UT ... day 1 21-00UT, day 2 ..., day 3 ...
    """

    with open(file, 'r', encoding='utf-8') as f:
        lines = [line for line in f]

    for i in range(len(lines)):

        if '00-03UT' in lines[i]:

            lines = lines[i:i+8]

            break

    for i in range(len(lines)):

        parts = re.sub(r'\(G\d\)', '', lines[i]).split()

        kp_lists[i].append(parts[1])
        kp_lists[i+8].append(parts[2])
        kp_lists[i+16].append(parts[3])

    return


def drop_repeated_reports(df):
    """
    Drops reports that repeat an earlier report exactly: the same 'Forecast Issued' and
    the same forecast values.

    A few three_day_forecast files are copies of the report before them (e.g.
    202205221230three_day_forecast.txt holds the 2022-05-21 1230 report), so their
    own slot has no report of its own.

    Parameters
    ----------
    df: pandas.DataFrame
        Forecast dataframe, sorted in the order to keep (the first copy is kept).

    Returns
    -------
    df: pandas.DataFrame
        df without the repeated rows. The index is not reset.
    """

    value_cols = [c for c in df.columns if c not in TIME_COLS]

    return df[~df.duplicated(subset=['Forecast Issued'] + value_cols, keep='first')]


# three_day_forecast files skipped entirely by get_three_day_forecast, as if they were never
# downloaded. Their slots come out as missing reports.
THREE_DAY_FORECAST_EXCLUDED_FILES = {
    # Kp table contains 3.37 (Oct 07 15-18UT), which is not a valid Kp value
    '202510071230three_day_forecast.txt': 'invalid Kp value',
    # 0030 reports whose header issue time reads ~12:25 the same day. Their Kp tables match the
    # previous evening's geomag_forecast exactly, so the header time is wrong.
    '202405140030three_day_forecast.txt': 'mistyped issue time (header 2024 May 14 1225)',
    '202502110030three_day_forecast.txt': 'mistyped issue time (header 2025 Feb 11 1235)',
    '202504260030three_day_forecast.txt': 'mistyped issue time (header 2025 Apr 26 1225)',
}


def get_three_day_forecast(fill_nans=True, test=False, exclude=None):
    """
    Extracts the 3 hourly Kp tables of every three_day_forecast report into
    three_day_forecast_3day_3hr_Kp.csv, one row per 12 hr slot (0030 and 1230 reports).

    Parameters
    ----------
    fill_nans: bool, optional
        Insert NaN rows for slots with no report. Default True.
    test: (False | str | pathlib.Path), optional
        False reads raw_data/three_day_forecast and saves to extracted_data. Otherwise reads the
        testing fixtures and saves to this directory.
    exclude: collection of str, optional
        File names to skip as if they did not exist. Default is THREE_DAY_FORECAST_EXCLUDED_FILES.

    Returns
    -------
    df_three_day_forecast_Kp: pandas.DataFrame
    """

    if test is False:
        dir_path = Path(f'raw_data/three_day_forecast')
        save_path_lead = 'extracted_data'
    else:
        dir_path = Path(f'testing/resources/testing_files/testing_three_day_forecast')
        save_path_lead = test

    if exclude is None:
        exclude = THREE_DAY_FORECAST_EXCLUDED_FILES

    raw_file_strings = [p for p in list_report_files(dir_path) if p.name not in exclude]
    issue_times = [extract_issue_time_from_file(p) for p in raw_file_strings]
    start_times = [extract_three_day_forecast_start_from_file(p, t) for p, t in zip(raw_file_strings, issue_times)]
    slot_times = [extract_three_day_forecast_slot_from_file_name(p) for p in raw_file_strings]

    kp_lists = [[] for i in range(24)]

    # Extract Kp forecast
    for file in raw_file_strings:

        extract_three_day_forecast_kp_from_file(file=file, kp_lists=kp_lists)

    kp_dict = forecast_time_columns(issue_times, start_times)
    for i in range(len(kp_lists)):
        kp_dict[f'{3*(i+1)}hrKp'] = np.array(kp_lists[i], dtype=float)

    # Store in dataframe, sorted by file name slot (the header issue time of a late report can sort out of order)
    df_three_day_forecast_Kp = pd.DataFrame(kp_dict)
    slots = pd.Series(pd.to_datetime(slot_times))
    order = np.argsort(slots.to_numpy(), kind='stable')
    df_three_day_forecast_Kp = df_three_day_forecast_Kp.iloc[order]

    # Drop files that are copies of an earlier report, leaving their slot empty
    df_three_day_forecast_Kp = drop_repeated_reports(df_three_day_forecast_Kp)
    slots = slots.loc[df_three_day_forecast_Kp.index].to_numpy()
    df_three_day_forecast_Kp.set_index(pd.Index([i for i in range(0, len(df_three_day_forecast_Kp['Forecast Issued']))]), inplace=True)

    # Fill missing forecast slots (0030 and 1230 each day) with Nan, placing each report in its file name slot
    if fill_nans is True:
        df_three_day_forecast_Kp = fill_nans_func(df=df_three_day_forecast_Kp, freq='12h', slots=slots)

    save_forecast_csv(df_three_day_forecast_Kp, f'{save_path_lead}/three_day_forecast_3day_3hr_Kp.csv')

    return df_three_day_forecast_Kp

def combine_daypre_geomag_ap_forecasts():
    return


def main():

    #convert_Kp_to_ap(0.67)
    print(round_decimal(12.456))

if __name__ == '__main__':

    main()

