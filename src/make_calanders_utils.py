import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

import datetime as dt
from pathlib import Path


def count_files(directory):
    """
    Counts the number of files in a directory.
    
    Parameters
    ----------
    directory: str
        Directory to count files within.
    
    Returns
    -------
    count: list
        Unsorted list containing names of all files in directory as strings.
    """
    
    dir_path = Path(directory)

    count = len([p for p in dir_path.iterdir() if p.is_file()])
    
    return count


def get_file_dates(report_name, test=False):
    """
    Finds all files in a directory and Ttims file name strings so that only date of file remains.
    
    Parameters
    ----------
    report_name: str
        Name of the report to study. One of 'daypre', 'geomag_forecast', 'rsga', 'the_weekly', 'three_day_forecast'
    
    Returns
    -------
    list_files: list
        Unsorted list containing all trimed string with date information of file.
    """

    if test is True:
        dir_path = Path(f'testing/resources/testing_files/testing_{report_name}')
    else:
        dir_path = Path(f'raw_data/{report_name}')

    if report_name == 'daypre' or report_name == 'geomag_forecast' or report_name == 'rsga':
        last_ind = 8
    if report_name == 'three_day_forecast':
        last_ind = 12

    list_files = [p.name[:last_ind] for p in dir_path.iterdir() if p.is_file()]

    return list_files


def file_names_to_datetimes(list_files, report_name):
    """
    Converts list of files with trimmed string to list of datetimes corresponding with file date.
    
    Parameters
    ----------
    list_files: list
        List of trimmed string containing date information of files for the report.
    report_name: str
        Name of the report to study. One of 'daypre', 'geomag_forecast', 'rsga', 'the_weekly', 'three_day_forecast'
    
    Returns
    -------
    dt_list_files: list
        Sorted list (oldest to newest) of dates/datetimes corresponding to the files for the report.
    """

    if report_name == 'daypre' or report_name == 'geomag_forecast' or report_name == 'rsga':
        date_format = [dt.date(year=int(p[0:4]), month=int(p[4:6]), day=int(p[6:8])) for p in list_files]
    if report_name == 'three_day_forecast':
        date_format = [dt.datetime(year=int(p[0:4]), month=int(p[4:6]), day=int(p[6:8]), hour=int(p[8:10]), minute=int(p[10:12])) for p in list_files]

    dt_list_files = sorted(date_format)

    return dt_list_files


def generate_date_range(dt_list_files, report_name):
    """
    Generates list of all dates between oldest and newest file for the report.
    
    Parameters
    ----------
    dt_list_files: list
        Sorted list (oldest to newest) of dates/datetimes corresponding to the files for the report.
    report_name: str
        Name of the report to study. One of 'daypre', 'geomag_forecast', 'rsga', 'the_weekly', 'three_day_forecast'
    
    Returns
    -------
    full_datetime_range: list
        Sorted list (oldest to newest) of all dates/datetimes between oldest and newest file for the report.
    """

    start_date = dt_list_files[0]
    end_date = dt_list_files[-1]

    if report_name == 'daypre' or report_name == 'geomag_forecast' or report_name == 'rsga':
        freq = '1d'
    if report_name == 'three_day_forecast':
        freq = '12h'
    if report_name == 'the_weekly':
        freq = '1W'

    full_datetime_range = pd.date_range(start=start_date,
                                        end=end_date,
                                        freq=freq).to_pydatetime().tolist()
    
    if report_name == 'daypre' or report_name == 'geomag_forecast' or report_name == 'the_weekly' or report_name == 'rsga':
        return [d.date() for d in full_datetime_range]
    if report_name == 'three_day_forecast':
        return full_datetime_range

 
def generate_date_mask(dt_list_files, full_date_range):
    """
    Generates list that masks full_date_range s.t. missing files are 0 and existing files are 1
    
    Parameters
    ----------
    dt_list_files: list
        Sorted list (oldest to newest) of dates/datetimes corresponding to the files for the report.
    full_date_range: list
        Sorted list (oldest to newest) of all dates/datetimes between oldest and newest file for the report.
    
    Returns
    -------
    date_ints: list
        List that masks full_date_range s.t. missing files are 0 and existing files are 1
    """

    date_mask = []
    for i in range(len(full_date_range)):
        date_mask.append(full_date_range[i] in dt_list_files)

    date_ints = [int(i) for i in date_mask]

    return date_ints


def count_missing_reports(date_ints):
    """
    Generates list that masks full_date_range s.t. missing files are 0 and existing files are 1
    
    Parameters
    ----------
    date_ints: list
        List that masks full_date_range s.t. missing files are 0 and existing files are 1
    
    Returns
    -------
    missing: int
        Number of files missing between start and end date of a report.
    
    """

    missing = int(date_ints.count(0))

    return missing


def reshape_mask(date_ints, width):
    """
    Reshapes date mask to 2d. Appends blank elements as needed.

    Parameters
    ----------
    date_ints: list
        List that masks full_date_range s.t. missing files are 0, and existing files are 1
    width: int
        Number of files represented in each row of the plot.
    
    Returns
    -------
    date_ints_2d: numpy.ndarry (n, width)
        2d date mask s.t. missing files are 0, existing files are 1, and extra dates needed for reshaping are -1
    """
    while len(date_ints) % width != 0:
        date_ints.append(-1)

    date_ints_2d = np.reshape(date_ints, (-1, width))

    return date_ints_2d


def create_color_map():
    """
    Creates color map for calander plot of missing reports. Missing is colored red and existing is colored green
    
    Returns
    -------
    cmap: matplotlib.colors.ListedColormap
        color map for calander plot of missing reports. Missing is colored red and existing is colored green
    """

    calander_cmap = mcolors.ListedColormap(['white', 'firebrick', 'forestgreen'])

    return calander_cmap


def create_daily_calander_plot(report_name, start_date=None, end_date=None, width=60, test=None):
    """
    Generates calander plot of files of a report. Red is missing, green exists.
    
    Parameters
    ----------
    report_name: str
        Name of the report to study. One of 'daypre', 'geomag_forecast', 'rsga', 'the_weekly', 'three_day_forecast'
    start_date: (dt.date | dt.datetime), optional
        Date to begin analysis. If None conducts analysis from the first file avilable. Default is None
    end_date: (dt.date | dt.datetime), optional
        Date to stop analysis. If None conducts analysis until the last avilable file. Default is None
    width: int, optional
        Number of files in each row of the plot. Default is 60.
    
    Returns
    -------
    None
        Displays and saves plot directly.
    """

    if test is not None:
        save_path_lead = test
    else:
        save_path_lead = f'analysis'
    
    # Generate image array
    raw_list_files = get_file_dates(report_name)
    dt_list_files = file_names_to_datetimes(raw_list_files, report_name)
    full_date_range = generate_date_range(dt_list_files, report_name)
    date_ints = generate_date_mask(dt_list_files, full_date_range)

    if start_date is not None and end_date is None:
        start_ind = full_date_range.index(start_date)
        full_date_range = full_date_range[start_ind:]
        date_ints = date_ints[start_ind:]
    elif start_date is None and end_date is not None:
        end_ind = full_date_range.index(end_date)
        full_date_range = full_date_range[:end_ind+1]
        date_ints = date_ints[:end_ind+1]
    elif start_date is not None and end_date is not None:
        start_ind = full_date_range.index(start_date)
        end_ind = full_date_range.index(end_date)
        full_date_range = full_date_range[start_ind:end_ind+1]
        date_ints = date_ints[start_ind:end_ind+1]
    
    # Reshape date array into 2D array of given width
    date_ints_2d = reshape_mask(date_ints, width)

    # Initialize figure
    cell_size = 0.2
    fig_width = width * cell_size
    fig_height = date_ints_2d.shape[0] * cell_size

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Create visual background grid
    ax.set_xticks(np.arange(-0.5, date_ints_2d.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, date_ints_2d.shape[0], 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=4*cell_size)
    ax.tick_params(which='minor', bottom=False, left=False)

    # Configure ticks
    ax.set_xticks([-0.5, width - 0.5], labels=[0, width])
    ax.set_yticks([-0.5, date_ints_2d.shape[0] - 0.5], labels=[full_date_range[0], full_date_range[-1]])
    ax.tick_params(axis='both', which='major', direction='out', labelsize=100*cell_size)

    # Set titles

    total = len(date_ints)
    missing = count_missing_reports(date_ints)

    if report_name == 'daypre':
        title = f'3-Day Space Weather Prediction: 1/2/3-day Ap forecast, {(missing/total)*100:.2f}% Missing'
    if report_name == 'geomag_forecast':
        title = f'3-Day Geomagnetic Forecast: 3-day/3-hr Kp forecast, 1/2/3-day Ap forecast, 1/2/3-day Probabalistic Geomagnetic Storm Forecast, {(missing/total)*100:.2f}% Missing'
    if report_name == 'three_day_forecast':
        title = f'3-Day Forecast:  3-day/3-hr Kp forecast, {(missing/total)*100:.2f}% Missing'
    if report_name == 'rsga':
        title = f'RSGA: 1/2/3-day F10.7cm forecast, {(missing/total)*100:.2f}% Missing'
    
    title_font_size = 1.4*fig_width

    ax.set_title(title, fontsize=title_font_size, pad=20)

    # Use Patches to create legend
    legend_elements = [mpatches.Patch(color='forestgreen', label='Exists'),
                       mpatches.Patch(color='firebrick', label='Missing')]
    #ax.legend(handles=legend_elements, fontsize=1.5*fig_size)

    calander_cmap = create_color_map()
    im = plt.imshow(date_ints_2d, cmap=calander_cmap)
    
    fig.savefig(f'{save_path_lead}/{report_name}_calander.png', bbox_inches='tight', facecolor='white')
    plt.show()

    return