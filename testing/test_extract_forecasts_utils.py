import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt
import shutil

import unittest
import pandas.testing as pdt
import numpy.testing as npt
import tempfile

import src.extract_forecasts_utils as efu
import testing.resources.testing_resources as t


class TestFillNansFunc(unittest.TestCase):

    def test_nans_filled(self):

        result_fill_nans_func = efu.fill_nans_func(df=t.expected_get_daypre_no_nans)

        expected_fill_nans_func = t.expected_get_daypre_nans
        pdt.assert_frame_equal(result_fill_nans_func, expected_fill_nans_func)

    def test_off_grid_issue_times_kept(self):

        # Issue times vary within the day and are not on a 3 hr grid; 2022-11-15 is missing
        df = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-11-13 22:05', '2022-11-14 22:10', '2022-11-16 22:00']),
                           '1dAp': [5, 7, 9]})

        result = efu.fill_nans_func(df=df)

        expected = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-11-13 22:05', '2022-11-14 22:10', pd.NaT, '2022-11-16 22:00']),
                                 '1dAp': [5, 7, np.nan, 9]})
        pdt.assert_frame_equal(result, expected)

    def test_no_missing_slots_unchanged(self):

        df = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-11-13 22:05', '2022-11-14 22:30']),
                           '1dAp': [5.0, 7.0]})

        result = efu.fill_nans_func(df=df)

        pdt.assert_frame_equal(result, df)

    def test_twelve_hour_cadence(self):

        # three_day_forecast style: issued 00:30 and 12:30, the 2022-03-25 12:30 report is missing
        df = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-03-25 00:30', '2022-03-26 00:30']),
                           '3hrKp': [3.0, 2.0]})

        result = efu.fill_nans_func(df=df, freq='12h')

        expected = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-03-25 00:30', pd.NaT, '2022-03-26 00:30']),
                                 '3hrKp': [3.0, np.nan, 2.0]})
        pdt.assert_frame_equal(result, expected)

    def test_missing_forecast_start_inferred(self):

        # geomag style: each report starts the day after issue, 2022-11-15 report missing
        df = pd.DataFrame(efu.forecast_time_columns(issue_times=pd.to_datetime(['2022-11-14 22:05', '2022-11-16 22:10']),
                                                    start_times=pd.to_datetime(['2022-11-15', '2022-11-17'])))
        df['1dAp'] = [5, 9]

        result = efu.fill_nans_func(df=df)

        expected = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-11-14 22:05', pd.NaT, '2022-11-16 22:10']),
                                 'Forecast Start': pd.to_datetime(['2022-11-15', '2022-11-16', '2022-11-17']),
                                 'Start Offset (hr)': [1.92, np.nan, 1.83],
                                 '1dAp': [5, np.nan, 9]})
        pdt.assert_frame_equal(result, expected)

    def test_missing_forecast_start_inferred_per_time_of_day(self):

        # three_day_forecast style: both the 00:30 and the 12:30 report start at 00 UT that day,
        # so the gap from the issue slot is 0 hr for 00:00 slots and -12 hr for 12:00 slots
        df = pd.DataFrame(efu.forecast_time_columns(issue_times=pd.to_datetime(['2022-03-25 00:30', '2022-03-25 12:30', '2022-03-26 00:30', '2022-03-27 00:30', '2022-03-27 12:30']),
                                                    start_times=pd.to_datetime(['2022-03-25', '2022-03-25', '2022-03-26', '2022-03-27', '2022-03-27'])))

        result = efu.fill_nans_func(df=df, freq='12h')

        expected_start = pd.Series(pd.to_datetime(['2022-03-25', '2022-03-25', '2022-03-26', '2022-03-26', '2022-03-27', '2022-03-27']), name='Forecast Start')
        pdt.assert_series_equal(result['Forecast Start'], expected_start)
        self.assertTrue(pd.isna(result['Forecast Issued'][3]))
        self.assertEqual(result['Start Offset (hr)'][1], -12.5)

    def test_two_reports_in_one_slot_raises(self):

        df = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2022-11-13 01:00', '2022-11-13 22:05']),
                           '1dAp': [5, 7]})

        with self.assertRaises(ValueError):
            efu.fill_nans_func(df=df)

class TestExtractIssueTimeFromFile(unittest.TestCase):

    def test_geomag_forecast(self):

        file = 'testing/resources/testing_files/testing_geomag_forecast/20221114geomag_forecast.txt'

        self.assertEqual(efu.extract_issue_time_from_file(file), dt.datetime(2022, 11, 14, 22, 0))

    def test_daypre(self):

        file = 'testing/resources/testing_files/testing_daypre/20131222daypre.txt'

        self.assertEqual(efu.extract_issue_time_from_file(file), dt.datetime(2013, 12, 22, 22, 0))

    def test_three_day_forecast_no_leading_colon(self):

        file = 'testing/resources/testing_files/testing_three_day_forecast/202203251230three_day_forecast.txt'

        self.assertEqual(efu.extract_issue_time_from_file(file), dt.datetime(2022, 3, 25, 12, 30))

    def test_missing_header_raises(self):

        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'no_header.txt'
            file.write_text(':Product: something\nno issue line here\n')

            with self.assertRaises(ValueError):
                efu.extract_issue_time_from_file(file)

class TestExtractForecastStartFromFile(unittest.TestCase):

    def test_geomag_forecast(self):

        file = 'testing/resources/testing_files/testing_geomag_forecast/20221114geomag_forecast.txt'

        result = efu.extract_geomag_forecast_start_from_file(file, issue_time=dt.datetime(2022, 11, 14, 22, 0))

        self.assertEqual(result, dt.datetime(2022, 11, 15))

    def test_geomag_forecast_december_to_january(self):

        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / '20221231geomag_forecast.txt'
            file.write_text('NOAA Kp index forecast 01 Jan - 03 Jan\n'
                            '             Jan 01    Jan 02    Jan 03\n'
                            '00-03UT        2.00      2.67      1.67\n')

            result = efu.extract_geomag_forecast_start_from_file(file, issue_time=dt.datetime(2022, 12, 31, 22, 5))

        self.assertEqual(result, dt.datetime(2023, 1, 1))

    def test_daypre(self):

        file = 'testing/resources/testing_files/testing_daypre/20131222daypre.txt'

        self.assertEqual(efu.extract_daypre_forecast_start_from_file(file), dt.datetime(2013, 12, 23))

class TestForecastTimeColumns(unittest.TestCase):

    def test_offsets(self):

        result = efu.forecast_time_columns(issue_times=pd.to_datetime(['2022-11-14 22:05', '2022-03-25 12:30']),
                                           start_times=pd.to_datetime(['2022-11-15', '2022-03-25']))

        self.assertEqual(list(result.keys()), efu.TIME_COLS)
        npt.assert_array_equal(result['Start Offset (hr)'], [1.92, -12.5])

class TestExtractDaypreApFromFile(unittest.TestCase):

    def test_correct_vals(self):

        file = 'testing/resources/testing_files/testing_daypre/20131222daypre.txt'

        ap_lists = [[] for i in range(3)]

        efu.extract_daypre_ap_from_file(file=file, ap_lists=ap_lists)

        self.assertEqual(ap_lists[0], ['5'])
        self.assertEqual(ap_lists[1], ['5'])
        self.assertEqual(ap_lists[2], ['10'])

class TestExtractGeomagForecastApFromFile(unittest.TestCase):

    def test_correct_vals(self):

        file = 'testing/resources/testing_files/testing_geomag_forecast/20221114geomag_forecast.txt'

        ap_lists = [[] for i in range(3)]

        efu.extract_geomag_forecast_ap_from_file(file=file, ap_lists=ap_lists)

        self.assertEqual(ap_lists[0], ['010'])
        self.assertEqual(ap_lists[1], ['010'])
        self.assertEqual(ap_lists[2], ['005'])
class TestExtractGeomagForecastKpFromFile(unittest.TestCase):

    def test_correct_vals(self):
        
        file = 'testing/resources/testing_files/testing_geomag_forecast/20221114geomag_forecast.txt'

        kp_lists = [[] for i in range(24)]
        efu.extract_geomag_forecast_kp_from_file(file=file, kp_lists=kp_lists)

        self.assertEqual(kp_lists[0], ['2.00'])
        self.assertEqual(kp_lists[1], ['2.00'])
        self.assertEqual(kp_lists[2], ['1.33'])
        self.assertEqual(kp_lists[3], ['1.33'])
        self.assertEqual(kp_lists[4], ['2.00'])
        self.assertEqual(kp_lists[5], ['3.00'])
        self.assertEqual(kp_lists[6], ['3.00'])
        self.assertEqual(kp_lists[7], ['3.00'])
        self.assertEqual(kp_lists[8], ['2.67'])
        self.assertEqual(kp_lists[9], ['2.67'])
        self.assertEqual(kp_lists[10], ['2.67'])
        self.assertEqual(kp_lists[11], ['2.67'])
        self.assertEqual(kp_lists[12], ['2.67'])
        self.assertEqual(kp_lists[13], ['2.00'])
        self.assertEqual(kp_lists[14], ['2.00'])
        self.assertEqual(kp_lists[15], ['2.33'])
        self.assertEqual(kp_lists[16], ['1.67'])
        self.assertEqual(kp_lists[17], ['1.33'])
        self.assertEqual(kp_lists[18], ['1.33'])
        self.assertEqual(kp_lists[19], ['1.33'])
        self.assertEqual(kp_lists[20], ['1.33'])
        self.assertEqual(kp_lists[21], ['1.33'])
        self.assertEqual(kp_lists[22], ['1.67'])
        self.assertEqual(kp_lists[23], ['1.67'])

class TestGetDaypreForecast(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        
        self.temp_dir.cleanup()

    def test_correct_vals_no_nans(self):
        
        result_get_daypre_forecast = efu.get_daypre_forecast(fill_nans=False, test=self.temp_path)

        expected_get_daypre_forecast = t.expected_get_daypre_no_nans
        pdt.assert_frame_equal(result_get_daypre_forecast, expected_get_daypre_forecast)

    def test_csv_exists(self):
        
        _ = efu.get_daypre_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/daypre_3day_daily_Ap.csv').is_file())


class TestGetGeomagForecast(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals_Kp_no_nans(self):

        result_get_geomag_forecast_Kp_no_nans = efu.get_geomag_forecast(fill_nans=False, test=self.temp_path)[0]

        expected_get_geomag_forecast_Kp_no_nans = t.expected_get_geomag_forecast_Kp_no_nans
        pdt.assert_frame_equal(result_get_geomag_forecast_Kp_no_nans, expected_get_geomag_forecast_Kp_no_nans)

    def test_correct_vals_Ap_no_nans(self):

        result_get_geomag_forecast_Ap_no_nans = efu.get_geomag_forecast(fill_nans=False, test=self.temp_path)[1]

        expected_get_geomag_forecast_Ap_no_nans = t.expected_get_geomag_forecast_Ap_no_nans
        pdt.assert_frame_equal(result_get_geomag_forecast_Ap_no_nans, expected_get_geomag_forecast_Ap_no_nans)
    
    def test_csv_exists(self):

        _ = efu.get_geomag_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/geomag_forecast_3day_3hr_Kp.csv').is_file())
        self.assertTrue(Path(f'{self.temp_path}/geomag_forecast_3day_daily_Ap.csv').is_file())

    def test_csv_forecast_start_has_time(self):

        _ = efu.get_geomag_forecast(test=self.temp_path)

        for name in ['geomag_forecast_3day_3hr_Kp.csv', 'geomag_forecast_3day_daily_Ap.csv']:
            # Read as text so pandas doesn't re-parse the column
            df = pd.read_csv(f'{self.temp_path}/{name}', dtype=str)
            self.assertEqual(df['Forecast Issued'][0], '2022-11-14 22:00:00')
            self.assertEqual(df['Forecast Start'][0], '2022-11-15 00:00:00')
            # Missing 2022-11-16 report still shows its inferred start time
            self.assertEqual(df['Forecast Start'][2], '2022-11-17 00:00:00')

class TestSaveForecastCsv(unittest.TestCase):

    def test_midnight_start_keeps_time_and_df_unchanged(self):

        df = pd.DataFrame({'Forecast Issued': pd.to_datetime(['2011-11-28']),
                           'Forecast Start': pd.to_datetime(['2011-11-29']),
                           '3hrKp': [1.0]})
        df_before = df.copy()

        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'f.csv'
            efu.save_forecast_csv(df, file)
            text = file.read_text()

        self.assertIn('2011-11-29 00:00:00', text)
        pdt.assert_frame_equal(df, df_before)


class TestExtractKpFromSWPCSheet(unittest.TestCase):

    def setUp(self):
    
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals_no_nans(self):

        result_extract_kp_from_SWPC_sheet_7day, result_extract_kp_from_SWPC_sheet_3day = efu.extract_Kp_from_SWPC_sheet(fill_nans=False, test=self.temp_path)

        expected_extract_kp_from_SWPC_sheet_7day = t.expected_extract_kp_from_SWPC_sheet_7day
        expected_extract_kp_from_SWPC_sheet_3day = t.expected_extract_kp_from_SWPC_sheet_3day
        pdt.assert_frame_equal(result_extract_kp_from_SWPC_sheet_7day, expected_extract_kp_from_SWPC_sheet_7day)
        pdt.assert_frame_equal(result_extract_kp_from_SWPC_sheet_3day, expected_extract_kp_from_SWPC_sheet_3day)

    def test_csv_exists(self):
    
        _ = efu.extract_Kp_from_SWPC_sheet(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/SWPC_7day_3hr_Kp.csv').is_file())
        self.assertTrue(Path(f'{self.temp_path}/SWPC_3day_3hr_Kp.csv').is_file())


class TestRoundDecimal(unittest.TestCase):

    def test_correct_rounding(self):

        self.assertAlmostEqual(0.33, efu.round_decimal(0.33))
        self.assertAlmostEqual(1.33, efu.round_decimal(1.33))

        self.assertAlmostEqual(0.33, efu.round_decimal(0.333))
        self.assertAlmostEqual(1.33, efu.round_decimal(1.333))

        self.assertAlmostEqual(1.67, efu.round_decimal(1.667))

        self.assertAlmostEqual(12.33, efu.round_decimal(12.333))


class TestConvertKpToap(unittest.TestCase):

    def test_correct_conversion(self):

        self.assertEqual(0, efu.convert_Kp_to_ap(0))
        self.assertEqual(2, efu.convert_Kp_to_ap(0.33))
        self.assertEqual(3, efu.convert_Kp_to_ap(0.67))
        self.assertEqual(4, efu.convert_Kp_to_ap(1))
        self.assertEqual(22, efu.convert_Kp_to_ap(3.67))


class TestConvertKpForecastToap(unittest.TestCase):

    def setUp(self):
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.file_name = 'testing_SWPC_3day_3hr_Kp.csv'

        shutil.copy(Path(f'testing/resources/testing_files/{self.file_name}'), self.temp_path)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_file_exists(self):

        _ = efu.convert_Kp_forecast_to_ap(Path(f'{self.temp_path}/{self.file_name}'))

        self.assertTrue(Path(f'{self.temp_path}/testing_SWPC_3day_3hr_ap.csv').is_file())

    def test_correct_vals(self):

        result_convert_Kp_forecast_to_ap = efu.convert_Kp_forecast_to_ap(Path(f'{self.temp_path}/{self.file_name}'))
        expected_convert_Kp_forecast_to_ap = t.expected_convert_Kp_forecast_to_ap

        pdt.assert_frame_equal(result_convert_Kp_forecast_to_ap, expected_convert_Kp_forecast_to_ap)

if __name__ == '__main__':
    unittest.main()
