import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from pathlib import Path
import datetime as dt

import pandas.testing as pdt
import numpy.testing as npt
import unittest
import tempfile

import src.make_calanders_utils as mcu
import testing.resources.testing_resources as t

class TestCountFiles(unittest.TestCase):

    def test_right_number(self):

        result_count_files = mcu.count_files(t.daypre_test_files_dir)

        expected_count_files = 3

        self.assertEqual(result_count_files, expected_count_files)

class TestGetFileDates(unittest.TestCase):

    def test_daypre_dates(self):

        report_name = 'daypre'
        result_get_file_dates_daypre = mcu.get_file_dates(report_name=report_name, test=True)

        expected_get_file_dates_daypre = ['20131222', '20131223', '20131225']

        self.assertCountEqual(result_get_file_dates_daypre, expected_get_file_dates_daypre) 

    def test_three_day_forecast_dates(self):

        report_name = 'three_day_forecast'
        result_get_file_dates_three_day_forecast = mcu.get_file_dates(report_name=report_name, test=True)

        expected_get_file_dates_three_day_forecast = ['202203250030', '202203251230', '202203260030']

        self.assertCountEqual(result_get_file_dates_three_day_forecast, expected_get_file_dates_three_day_forecast) 
    
class TestFileNamesToDatetimes(unittest.TestCase):

    def test_daypre_datetimes(self):

        report_name = 'daypre'
        list_files_daypre = ['20131222', '20131223', '20131225']
        result_file_names_to_datetimes_daypre = mcu.file_names_to_datetimes(list_files=list_files_daypre, report_name=report_name)

        expected_file_names_to_datetimes_daypre = [dt.date(2013, 12, 22), dt.date(2013, 12, 23), dt.date(2013, 12, 25)]
        self.assertCountEqual(result_file_names_to_datetimes_daypre, expected_file_names_to_datetimes_daypre)
        
    def test_three_day_forecast_datetimes(self):

        report_name = 'three_day_forecast'
        list_files_three_day_forecast = ['202203250030', '202203251230', '202203260030']
        result_file_names_to_datetimes_three_day_forecast = mcu.file_names_to_datetimes(list_files=list_files_three_day_forecast, report_name=report_name)

        expected_file_names_to_datetimes_three_day_forecast = [dt.datetime(2022, 3, 25, 00, 30), dt.datetime(2022, 3, 25, 12, 30), dt.datetime(2022, 3, 26, 00, 30)]
        self.assertCountEqual(result_file_names_to_datetimes_three_day_forecast, expected_file_names_to_datetimes_three_day_forecast)

class TestGenerateDateRange(unittest.TestCase):

    def test_daypre_daterange(self):
        
        report_name = 'daypre'
        dt_list_files_daypre = [dt.date(2013, 12, 22), dt.date(2013, 12, 24)]
        result_generate_date_range_daypre = mcu.generate_date_range(dt_list_files=dt_list_files_daypre, report_name=report_name)

        expected_generate_date_range_daypre = [dt.date(2013, 12, 22), dt.date(2013, 12, 23), dt.date(2013, 12, 24)]
        self.assertCountEqual(result_generate_date_range_daypre, expected_generate_date_range_daypre)

    def test_three_day_forecast_daterange(self):
        
        report_name = 'three_day_forecast'
        dt_list_files_three_day_forecast = [dt.datetime(2022, 3, 25, 00, 30), dt.datetime(2022, 3, 26, 00, 30)]
        result_generate_date_range_three_day_forecast = mcu.generate_date_range(dt_list_files=dt_list_files_three_day_forecast, report_name=report_name)

        expected_generate_date_range_three_day_forecast = [dt.datetime(2022, 3, 25, 00, 30), dt.datetime(2022, 3, 25, 12, 30), dt.datetime(2022, 3, 26, 00, 30)]
        self.assertCountEqual(result_generate_date_range_three_day_forecast, expected_generate_date_range_three_day_forecast)

    def test_the_weekly_daterange(self):
        
        report_name = 'the_weekly'
        dt_list_files_the_weekly = [dt.date(2026, 3, 8), dt.date(2026, 3, 22)]
        result_generate_date_range_the_weekly = mcu.generate_date_range(dt_list_files=dt_list_files_the_weekly, report_name=report_name)

        expected_generate_date_range_the_weekly = [dt.date(2026, 3, 8), dt.date(2026, 3, 15), dt.date(2026, 3, 22)]
        self.assertCountEqual(result_generate_date_range_the_weekly, expected_generate_date_range_the_weekly)

class TestGenerateDateMask(unittest.TestCase):

    def test_correct_date_mask(self):
        
        dt_list_files = [dt.date(2013, 12, 22), dt.date(2013, 12, 24)]
        full_date_range = [dt.date(2013, 12, 22), dt.date(2013, 12, 23), dt.date(2013, 12, 24)]
        result_generate_date_mask = mcu.generate_date_mask(dt_list_files=dt_list_files, full_date_range=full_date_range)

        expected_generate_date_mask = [1, 0 ,1]

        self.assertCountEqual(result_generate_date_mask, expected_generate_date_mask)

class TestCountMissingReports(unittest.TestCase):

    def test_correct_number_missing(self):
        
        count_missing_date_ints = [1, 1, 0, 1, 0]
        result_count_missing = mcu.count_missing_reports(count_missing_date_ints)
        
        expected_count_missing = 2

        self.assertEqual(result_count_missing, expected_count_missing)

class TestReshapeMask(unittest.TestCase):

    def test_correct_shape(self):

        reshape_mask_arr = [1, 1, 1, 1, 1]
        result_reshape_mask = mcu.reshape_mask(date_ints=reshape_mask_arr, width=3)

        expected_reshape_mask = np.array([[1, 1, 1], [1, 1, -1]])

        npt.assert_array_equal(result_reshape_mask, expected_reshape_mask)

class TestCreateColorMap(unittest.TestCase):

    def test_colormap_exists(self):
        
        result_create_cmap = mcu.create_color_map()

        self.assertIsInstance(result_create_cmap, mcolors.ListedColormap)

class TestCreateDailyCalanderPlot(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        
        self.temp_dir.cleanup()

    def test_plot_exists(self):
        
        mcu.create_daily_calander_plot(report_name='daypre', test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/daypre_calander.png').is_file())
        

if __name__ == '__main__':
    unittest.main()
