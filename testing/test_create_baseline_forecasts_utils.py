import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt

import unittest
import pandas.testing as pdt
import numpy.testing as npt
import tempfile

import src.create_baseline_forecasts_utils as cbfu
import testing.resources.testing_resources as t


class TestMakeApStorageList(unittest.TestCase):

    def test_correct_length(self):

        expected_len = 3
        result_len = len(cbfu.make_Ap_storage_list())

        self.assertEqual(result_len, expected_len)


class TestMakeKpStorageList(unittest.TestCase):

    def test_correct_length(self):

        expected_len = 24
        result_len = len(cbfu.make_Kp_storage_list())

        self.assertEqual(result_len, expected_len)


class TestCreate3dayApFromRealVals(unittest.TestCase):

    def setUp(self):
    
            self.temp_dir = tempfile.TemporaryDirectory()
            self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals_subset(self):

        result = cbfu.create_3day_Ap_from_real_vals(test=self.temp_path)

        expected_19320101 = [26, 11, 4]
        expected_20120918 = [14, 10, 6]
        expected_20191029 = [7, 6, 3]

        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):

        _ = cbfu.create_3day_Ap_from_real_vals(test=self.temp_path)
    
        self.assertTrue(Path(f'{self.temp_path}/real_3day_daily_Ap.csv').is_file())
    
class TestCreate3dayKpFromRealVals(unittest.TestCase):

    def setUp(self):
    
            self.temp_dir = tempfile.TemporaryDirectory()
            self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals_subset(self):

        result = cbfu.create_3day_Kp_from_real_vals(test=self.temp_path)

        expected_19320101 = [2.667, 2.333, 2.667, 3.333, 2.667, 3.333, 3.333, 3.667, 3.667, 3.333, 3.667, 3.333, 4.667, 3.0, 5.0, 3.333, 3.333, 3.0, 1.0, 2.333, 1.667, 2.667, 2.0, 2.0]
        expected_20120918 = [3.333, 2.0, 1.667, 2.333, 2.667, 0.333, 1.0, 1.0, 2.333, 0.667, 1.333, 1.667, 3.667, 3.667, 4.667, 3.333, 2.0, 3.0, 2.333, 2.0, 2.0, 2.0, 1.667, 1.333]
        expected_20191029 = [3.0, 0.667, 0.0, 0.667, 2.667, 2.333, 1.333, 1.0, 1.333, 1.0, 1.0, 2.333, 2.333, 2.333, 2.333, 3.667, 0.333, 0.333, 1.333, 0.0, 0.333, 2.667, 1.667, 1.333]
        
        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)


    def test_csv_exists(self):

         _ = cbfu.create_3day_Kp_from_real_vals(test=self.temp_path)

         self.assertTrue(Path(f'{self.temp_path}/real_3day_3hr_Kp.csv').is_file())


class TestCreate3dayapFromRealVals(unittest.TestCase):

    def setUp(self):
    
            self.temp_dir = tempfile.TemporaryDirectory()
            self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals_subset(self):

        result = cbfu.create_3day_ap_from_real_vals(test=self.temp_path)

        expected_19320101 = [12, 9, 12, 18, 12, 18, 18, 22, 22, 18, 22, 18, 39, 15, 48, 18, 18, 15, 4, 9, 6, 12, 7, 7]
        expected_20120918 = [18, 7, 6, 9, 12, 2, 4, 4, 9, 3, 5, 6, 22, 22, 39, 18, 7, 15, 9, 7, 7, 7, 6, 5]
        expected_20191029 = [15, 3, 0, 3, 12, 9, 5, 4, 5, 4, 4, 9, 9, 9, 9, 22, 2, 2, 5, 0, 2, 12, 6, 5]
        
        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)


    def test_csv_exists(self):

         _ = cbfu.create_3day_ap_from_real_vals(test=self.temp_path)

         self.assertTrue(Path(f'{self.temp_path}/real_3day_3hr_ap.csv').is_file())

class TestCreate3DayApPersistenceForecast(unittest.TestCase):

    def setUp(self):
    
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):

        result = cbfu.create_3day_Ap_persistence_forecast(test=self.temp_path)

        expected_19320101 = [15, 15, 15]
        expected_20120918 = [9, 9, 9]
        expected_20191029 = [7, 7, 7]

        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_Ap_persistence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/persistence_3day_daily_Ap.csv').is_file())

class TestCreate3DayKpPersistenceForecast(unittest.TestCase):

    def setUp(self):
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):

        result = cbfu.create_3day_Kp_persistence_forecast(test=self.temp_path)

        expected_19320101 = [3.333 for i in range(24)]
        expected_20120918 = [3.0 for i in range(24)]
        expected_20191029 = [2.667 for i in range(24)]

        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_Kp_persistence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/persistence_3day_3hr_Kp.csv').is_file())


class TestCreate3DayapPersistenceForecast(unittest.TestCase):

    def setUp(self):
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):

        result = cbfu.create_3day_ap_persistence_forecast(test=self.temp_path)

        expected_19320101 = [18 for i in range(24)]
        expected_20120918 = [15 for i in range(24)]
        expected_20191029 = [12 for i in range(24)]

        result_19320101 = result.loc[result['Forecast Issued'] == '1932-01-01'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320101, expected_19320101)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_ap_persistence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/persistence_3day_3hr_ap.csv').is_file())
    

class TestCreate3DayApRecurrenceForecast(unittest.TestCase):

    def setUp(self):
            
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
            
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):
        
        result = cbfu.create_3day_Ap_recurrence_forecast(test=self.temp_path)

        expected_19320128 = [15, 26, 11]
        expected_20120918 = [5, 9, 7]
        expected_20191029 = [6, 4, 6]

        result_19320128 = result.loc[result['Forecast Issued'] == '1932-01-28'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320128, expected_19320128)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_Ap_recurrence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/recurrence_3day_daily_Ap.csv').is_file())


class TestCreate3DayKpRecurrenceForecast(unittest.TestCase):

    def setUp(self):
            
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
            
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):

        result = cbfu.create_3day_Kp_recurrence_forecast(test=self.temp_path)

        expected_19320128 = [3.333, 2.667, 2.333, 2.667, 3.333, 2.667, 3.333, 3.333, 3.667, 3.667, 3.333, 3.667, 3.333, 4.667, 3.0, 5.0, 3.333, 3.333, 3.0, 1.0, 2.333, 1.667, 2.667, 2.0]
        expected_20120918 = [1.0, 1.333, 0.333, 1.0, 2.333, 1.333, 1.0, 2.333, 3.0, 2.0, 2.0, 2.0, 2.0, 2.333, 3.0, 0.667, 2.333, 2.0, 1.333, 1.333, 2.0, 1.333, 2.0, 2.667]
        expected_20191029 = [3.0, 0.0, 0.0, 2.0, 2.667, 1.0, 1.0, 2.333, 1.667, 1.333, 1.0, 1.0, 0.333, 0.667, 1.333, 1.0, 1.0, 1.667, 2.667, 1.667, 2.0, 2.0, 1.667, 0.667]

        result_19320128 = result.loc[result['Forecast Issued'] == '1932-01-28'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320128, expected_19320128)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_Kp_recurrence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/recurrence_3day_3hr_Kp.csv').is_file())


class TestCreate3DayapRecurrenceForecast(unittest.TestCase):

    def setUp(self):
            
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
            
    def tearDown(self):

        self.temp_dir.cleanup()

    def test_correct_vals(self):

        result = cbfu.create_3day_ap_recurrence_forecast(test=self.temp_path)

        expected_19320128 = [18, 12, 9, 12, 18, 12, 18, 18, 22, 22, 18, 22, 18, 39, 15, 48, 18, 18, 15, 4, 9, 6, 12, 7]
        expected_20120918 = [4, 5, 2, 4, 9, 5, 4, 9, 15, 7, 7, 7, 7, 9, 15, 3, 9, 7, 5, 5, 7, 5, 7, 12]
        expected_20191029 = [15, 0, 0, 7, 12, 4, 4, 9, 6, 5, 4, 4, 2, 3, 5, 4, 4, 6, 12, 6, 7, 7, 6, 3]

        result_19320128 = result.loc[result['Forecast Issued'] == '1932-01-28'].values[0][1:].tolist()
        result_20120918 = result.loc[result['Forecast Issued'] == '2012-09-18'].values[0][1:].tolist()
        result_20191029 = result.loc[result['Forecast Issued'] == '2019-10-29'].values[0][1:].tolist()

        self.assertEqual(result_19320128, expected_19320128)
        self.assertEqual(result_20120918, expected_20120918)
        self.assertEqual(result_20191029, expected_20191029)

    def test_csv_exists(self):
    
        _ = cbfu.create_3day_ap_recurrence_forecast(test=self.temp_path)

        self.assertTrue(Path(f'{self.temp_path}/recurrence_3day_3hr_ap.csv').is_file())


if __name__ == '__main__':

    unittest.main()