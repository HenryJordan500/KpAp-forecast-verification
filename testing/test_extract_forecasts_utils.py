import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt

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

        self.assertTrue(Path(f'{self.temp_path}/daypre_3dayAp.csv').is_file())


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

        self.assertTrue(Path(f'{self.temp_path}/geomag_forecast_3dayKp.csv').is_file())
        self.assertTrue(Path(f'{self.temp_path}/geomag_forecast_3dayAp.csv').is_file())
    


if __name__ == '__main__':
    unittest.main()
