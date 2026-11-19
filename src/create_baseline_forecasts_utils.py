import numpy as np
import pandas as pd

from src.extract_forecasts_utils import forecast_time_columns, save_forecast_csv

DEFAULT_START_DATE = '2011-01-01'

KP_LEAD_COLS = [f'{3*(i+1)}hrKp' for i in range(24)]
AP_3HR_LEAD_COLS = [f'{3*(i+1)}hrap' for i in range(24)]
AP_DAILY_LEAD_COLS = [f'{i+1}dAp' for i in range(3)]

THREE_HOUR = pd.Timedelta(hours=3)
ONE_DAY = pd.Timedelta(days=1)

# One solar rotation, in observation slots
RECURRENCE_LAG_3HR = 27 * 8
RECURRENCE_LAG_DAILY = 27


def load_observed(file, value_col):
    """
    Reads an observed series from extracted_data/.

    Parameters
    ----------
    file: str
        File name in extracted_data/, e.g. '3hour_Kp.csv'.
    value_col: str
        Name of the value column, e.g. 'Kp'.

    Returns
    -------
    slot_times: pandas.DatetimeIndex
        Start time of each observation slot.
    values: numpy.ndarray
        Observed value in each slot.
    """

    df = pd.read_csv(f'extracted_data/{file}')

    return pd.DatetimeIndex(pd.to_datetime(df['Datetime'])), df[value_col].to_numpy()


def make_baseline_values(values, method, n_leads, recurrence_lag):
    """
    Builds the forecast values of a baseline from an observed series.

    A forecast is issued when observed slot k finishes, so lead 1 is slot k+1.

    Parameters
    ----------
    values: numpy.ndarray
        Observed value in each slot, in time order with no gaps.
    method: str
        'real' (the observed values of slots k+1..k+n_leads), 'persistence' (the value of
        slot k, repeated) or 'recurrence' (the value of each target slot recurrence_lag
        slots earlier).
    n_leads: int
        Number of lead columns.
    recurrence_lag: int
        Recurrence lag in slots. Only used when method is 'recurrence'.

    Returns
    -------
    slot_idx: numpy.ndarray
        Index k of the last observed slot before each forecast is issued.
    forecast_values: numpy.ndarray
        Shape (len(slot_idx), n_leads). Row i is the forecast issued when slot slot_idx[i] finishes.
    """

    n = len(values)
    windows = np.lib.stride_tricks.sliding_window_view(values, n_leads)

    if method == 'real':
        slot_idx = np.arange(0, n - n_leads)
        forecast_values = windows[slot_idx + 1]
    elif method == 'persistence':
        slot_idx = np.arange(0, n)
        forecast_values = np.repeat(values[:, None], n_leads, axis=1)
    elif method == 'recurrence':
        # Issue slot must be observed (k <= n-1) and its window must exist (k+1-lag <= n-n_leads)
        slot_idx = np.arange(recurrence_lag - 1, min(n, n - n_leads + recurrence_lag))
        forecast_values = windows[slot_idx + 1 - recurrence_lag]
    else:
        raise ValueError(f'Unknown baseline method: {method}')

    return slot_idx, forecast_values


def create_baseline_forecast(method, obs_file, value_col, lead_cols, step, recurrence_lag,
                             dtype, out_name, start_date=DEFAULT_START_DATE, test=False):
    """
    Builds a baseline forecast dataframe in the shared forecast schema and saves it to csv.

    Each forecast is issued at T, the end of an observed slot, and starts at T, so
    'Forecast Issued' == 'Forecast Start' and 'Start Offset (hr)' is 0.

    Parameters
    ----------
    method: str
        'real', 'persistence' or 'recurrence' (see make_baseline_values).
    obs_file: str
        Observed series file in extracted_data/.
    value_col: str
        Value column of obs_file.
    lead_cols: list of str
        Names of the lead columns, e.g. ['3hrKp', ..., '72hrKp'].
    step: pandas.Timedelta
        Length of an observation slot (3 hours or 1 day).
    recurrence_lag: int
        Recurrence lag in slots.
    dtype: type
        dtype of the forecast values.
    out_name: str
        Output csv file name.
    start_date: str, optional
        Only forecasts issued at or after this time are kept.
    test: (bool | str | pathlib.Path), optional
        Directory to save to instead of baseline_forecasts/.

    Returns
    -------
    df: pandas.DataFrame
        The saved forecast dataframe.
    """

    save_path_lead = 'baseline_forecasts' if test is False else test

    slot_times, values = load_observed(obs_file, value_col)

    slot_idx, forecast_values = make_baseline_values(values=values,
                                                     method=method,
                                                     n_leads=len(lead_cols),
                                                     recurrence_lag=recurrence_lag)

    issue_times = slot_times[slot_idx] + step

    forecast_dict = forecast_time_columns(issue_times, issue_times)
    for i, col in enumerate(lead_cols):
        forecast_dict[col] = forecast_values[:, i].astype(dtype)

    df = pd.DataFrame(forecast_dict)
    df = df[df['Forecast Issued'] >= pd.Timestamp(start_date)].reset_index(drop=True)

    save_forecast_csv(df, f'{save_path_lead}/{out_name}')

    return df


def _daily_Ap(method, out_name, start_date, test):

    return create_baseline_forecast(method=method, obs_file='daily_Ap.csv', value_col='Ap',
                                    lead_cols=AP_DAILY_LEAD_COLS, step=ONE_DAY,
                                    recurrence_lag=RECURRENCE_LAG_DAILY, dtype=int,
                                    out_name=out_name, start_date=start_date, test=test)


def _3hr_Kp(method, out_name, start_date, test):

    return create_baseline_forecast(method=method, obs_file='3hour_Kp.csv', value_col='Kp',
                                    lead_cols=KP_LEAD_COLS, step=THREE_HOUR,
                                    recurrence_lag=RECURRENCE_LAG_3HR, dtype=float,
                                    out_name=out_name, start_date=start_date, test=test)


def _3hr_ap(method, out_name, start_date, test):

    return create_baseline_forecast(method=method, obs_file='3hour_ap.csv', value_col='ap',
                                    lead_cols=AP_3HR_LEAD_COLS, step=THREE_HOUR,
                                    recurrence_lag=RECURRENCE_LAG_3HR, dtype=float,
                                    out_name=out_name, start_date=start_date, test=test)


def create_3day_Ap_from_real_vals(start_date=DEFAULT_START_DATE, test=False):

    return _daily_Ap('real', 'real_3day_daily_Ap.csv', start_date, test)


def create_3day_Kp_from_real_vals(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_Kp('real', 'real_3day_3hr_Kp.csv', start_date, test)


def create_3day_ap_from_real_vals(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_ap('real', 'real_3day_3hr_ap.csv', start_date, test)


def create_3day_Ap_persistence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _daily_Ap('persistence', 'persistence_3day_daily_Ap.csv', start_date, test)


def create_3day_Kp_persistence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_Kp('persistence', 'persistence_3day_3hr_Kp.csv', start_date, test)


def create_3day_ap_persistence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_ap('persistence', 'persistence_3day_3hr_ap.csv', start_date, test)


def create_3day_Ap_recurrence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _daily_Ap('recurrence', 'recurrence_3day_daily_Ap.csv', start_date, test)


def create_3day_Kp_recurrence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_Kp('recurrence', 'recurrence_3day_3hr_Kp.csv', start_date, test)


def create_3day_ap_recurrence_forecast(start_date=DEFAULT_START_DATE, test=False):

    return _3hr_ap('recurrence', 'recurrence_3day_3hr_ap.csv', start_date, test)
