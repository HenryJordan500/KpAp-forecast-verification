import pandas as pd
import numpy as np
from pathlib import Path

import unittest
import numpy.testing as npt
import tempfile

import src.create_baseline_forecasts_utils as cbfu
from src.extract_forecasts_utils import TIME_COLS

THREE_HOUR = pd.Timedelta(hours=3)
ONE_DAY = pd.Timedelta(days=1)


def row_values(df, issued):
    """Forecast values (everything after the time columns) of the forecast issued at `issued`."""

    row = df.loc[df['Forecast Issued'] == pd.Timestamp(issued)]

    return row.values[0][len(TIME_COLS):].tolist()


def load_observed_series(file, value_col):

    df = pd.read_csv(f'extracted_data/{file}', parse_dates=['Datetime'])

    return df.set_index('Datetime')[value_col]


class TestMakeBaselineValues(unittest.TestCase):

    def setUp(self):

        self.values = np.arange(10)

    def test_real(self):

        slot_idx, result = cbfu.make_baseline_values(self.values, 'real', n_leads=3, recurrence_lag=4)

        npt.assert_array_equal(slot_idx, np.arange(0, 7))
        npt.assert_array_equal(result[0], [1, 2, 3])
        npt.assert_array_equal(result[-1], [7, 8, 9])

    def test_persistence(self):

        slot_idx, result = cbfu.make_baseline_values(self.values, 'persistence', n_leads=3, recurrence_lag=4)

        npt.assert_array_equal(slot_idx, np.arange(0, 10))
        npt.assert_array_equal(result[0], [0, 0, 0])
        npt.assert_array_equal(result[-1], [9, 9, 9])

    def test_recurrence(self):

        slot_idx, result = cbfu.make_baseline_values(self.values, 'recurrence', n_leads=3, recurrence_lag=4)

        # Slot k finished -> targets k+1..k+3, each taken from 4 slots earlier
        npt.assert_array_equal(slot_idx, np.arange(3, 10))
        npt.assert_array_equal(result[0], [0, 1, 2])
        npt.assert_array_equal(result[-1], [6, 7, 8])

    def test_unknown_method_raises(self):

        with self.assertRaises(ValueError):
            cbfu.make_baseline_values(self.values, 'climatology', n_leads=3, recurrence_lag=4)


class BaselineTestCase(unittest.TestCase):
    """Shared setup and schema checks for the baseline forecast functions."""

    func = None
    out_name = None
    lead_cols = None
    step = None

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):

        self.temp_dir.cleanup()

    def run_func(self):

        return type(self).func(test=self.temp_path)

    def check_schema(self, result):

        self.assertEqual(result.columns.tolist(), TIME_COLS + self.lead_cols)
        self.assertTrue((result['Forecast Start'] == result['Forecast Issued']).all())
        self.assertTrue((result['Start Offset (hr)'] == 0).all())

        # One forecast per issue slot, starting at the default start date
        self.assertEqual(result['Forecast Issued'].iloc[0], pd.Timestamp(cbfu.DEFAULT_START_DATE))
        self.assertTrue((result['Forecast Issued'].diff().dropna() == self.step).all())

    def check_csv_exists(self):

        _ = self.run_func()

        self.assertTrue(Path(f'{self.temp_path}/{self.out_name}').is_file())


class TestCreate3dayApFromRealVals(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Ap_from_real_vals)
    out_name = 'real_3day_daily_Ap.csv'
    lead_cols = cbfu.AP_DAILY_LEAD_COLS
    step = ONE_DAY

    def test_correct_vals_subset(self):

        result = self.run_func()

        self.assertEqual(row_values(result, '2012-09-18'), [9, 14, 10])
        self.assertEqual(row_values(result, '2019-10-29'), [7, 7, 6])

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_start_date(self):

        result = cbfu.create_3day_Ap_from_real_vals(start_date='2019-10-29', test=self.temp_path)

        self.assertEqual(result['Forecast Issued'].iloc[0], pd.Timestamp('2019-10-29'))

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3dayKpFromRealVals(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Kp_from_real_vals)
    out_name = 'real_3day_3hr_Kp.csv'
    lead_cols = cbfu.KP_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals_subset(self):

        result = self.run_func()

        expected_20120918 = [3.0, 3.333, 2.0, 1.667, 2.333, 2.667, 0.333, 1.0, 1.0, 2.333, 0.667, 1.333, 1.667, 3.667, 3.667, 4.667, 3.333, 2.0, 3.0, 2.333, 2.0, 2.0, 2.0, 1.667]
        expected_20191029 = [2.667, 3.0, 0.667, 0.0, 0.667, 2.667, 2.333, 1.333, 1.0, 1.333, 1.0, 1.0, 2.333, 2.333, 2.333, 2.333, 3.667, 0.333, 0.333, 1.333, 0.0, 0.333, 2.667, 1.667]
        expected_20191029_15 = [2.667, 2.333, 1.333, 1.0, 1.333, 1.0, 1.0, 2.333, 2.333, 2.333, 2.333, 3.667, 0.333, 0.333, 1.333, 0.0, 0.333, 2.667, 1.667, 1.333, 2.333, 0.667, 0.333, 0.667]

        self.assertEqual(row_values(result, '2012-09-18 00:00'), expected_20120918)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), expected_20191029)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), expected_20191029_15)

    def test_matches_observed(self):

        result = self.run_func()
        obs = load_observed_series('3hour_Kp.csv', 'Kp')

        T = pd.Timestamp('2019-10-29 15:00')
        self.assertEqual(row_values(result, T), obs[T:T + 23 * THREE_HOUR].tolist())

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3dayapFromRealVals(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_ap_from_real_vals)
    out_name = 'real_3day_3hr_ap.csv'
    lead_cols = cbfu.AP_3HR_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals_subset(self):

        result = self.run_func()

        expected_20120918 = [15, 18, 7, 6, 9, 12, 2, 4, 4, 9, 3, 5, 6, 22, 22, 39, 18, 7, 15, 9, 7, 7, 7, 6]
        expected_20191029 = [12, 15, 3, 0, 3, 12, 9, 5, 4, 5, 4, 4, 9, 9, 9, 9, 22, 2, 2, 5, 0, 2, 12, 6]
        expected_20191029_15 = [12, 9, 5, 4, 5, 4, 4, 9, 9, 9, 9, 22, 2, 2, 5, 0, 2, 12, 6, 5, 9, 3, 2, 3]

        self.assertEqual(row_values(result, '2012-09-18 00:00'), expected_20120918)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), expected_20191029)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), expected_20191029_15)

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayApPersistenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Ap_persistence_forecast)
    out_name = 'persistence_3day_daily_Ap.csv'
    lead_cols = cbfu.AP_DAILY_LEAD_COLS
    step = ONE_DAY

    def test_correct_vals(self):

        result = self.run_func()

        # Ap of the day before issue
        self.assertEqual(row_values(result, '2012-09-18'), [4, 4, 4])
        self.assertEqual(row_values(result, '2019-10-29'), [10, 10, 10])

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayKpPersistenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Kp_persistence_forecast)
    out_name = 'persistence_3day_3hr_Kp.csv'
    lead_cols = cbfu.KP_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals(self):

        result = self.run_func()

        # Kp of the slot that finished at issue time
        self.assertEqual(row_values(result, '2012-09-18 00:00'), [1.667] * 24)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), [2.333] * 24)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), [0.667] * 24)

    def test_matches_observed(self):

        result = self.run_func()
        obs = load_observed_series('3hour_Kp.csv', 'Kp')

        T = pd.Timestamp('2019-10-29 15:00')
        self.assertEqual(row_values(result, T), [obs[T - THREE_HOUR]] * 24)

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayapPersistenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_ap_persistence_forecast)
    out_name = 'persistence_3day_3hr_ap.csv'
    lead_cols = cbfu.AP_3HR_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals(self):

        result = self.run_func()

        self.assertEqual(row_values(result, '2012-09-18 00:00'), [6] * 24)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), [9] * 24)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), [3] * 24)

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayApRecurrenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Ap_recurrence_forecast)
    out_name = 'recurrence_3day_daily_Ap.csv'
    lead_cols = cbfu.AP_DAILY_LEAD_COLS
    step = ONE_DAY

    def test_correct_vals(self):

        result = self.run_func()

        # Ap 27 days before each target day
        self.assertEqual(row_values(result, '2012-09-18'), [5, 9, 7])
        self.assertEqual(row_values(result, '2019-10-29'), [6, 4, 6])

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayKpRecurrenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_Kp_recurrence_forecast)
    out_name = 'recurrence_3day_3hr_Kp.csv'
    lead_cols = cbfu.KP_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals(self):

        result = self.run_func()

        expected_20120918 = [1.0, 1.333, 0.333, 1.0, 2.333, 1.333, 1.0, 2.333, 3.0, 2.0, 2.0, 2.0, 2.0, 2.333, 3.0, 0.667, 2.333, 2.0, 1.333, 1.333, 2.0, 1.333, 2.0, 2.667]
        expected_20191029 = [3.0, 0.0, 0.0, 2.0, 2.667, 1.0, 1.0, 2.333, 1.667, 1.333, 1.0, 1.0, 0.333, 0.667, 1.333, 1.0, 1.0, 1.667, 2.667, 1.667, 2.0, 2.0, 1.667, 0.667]
        expected_20191029_15 = [1.0, 1.0, 2.333, 1.667, 1.333, 1.0, 1.0, 0.333, 0.667, 1.333, 1.0, 1.0, 1.667, 2.667, 1.667, 2.0, 2.0, 1.667, 0.667, 1.333, 1.333, 1.0, 2.0, 1.667]

        self.assertEqual(row_values(result, '2012-09-18 00:00'), expected_20120918)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), expected_20191029)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), expected_20191029_15)

    def test_matches_observed(self):

        result = self.run_func()
        obs = load_observed_series('3hour_Kp.csv', 'Kp')

        T = pd.Timestamp('2019-10-29 15:00')
        T_27 = T - pd.Timedelta(days=27)
        self.assertEqual(row_values(result, T), obs[T_27:T_27 + 23 * THREE_HOUR].tolist())

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


class TestCreate3DayapRecurrenceForecast(BaselineTestCase):

    func = staticmethod(cbfu.create_3day_ap_recurrence_forecast)
    out_name = 'recurrence_3day_3hr_ap.csv'
    lead_cols = cbfu.AP_3HR_LEAD_COLS
    step = THREE_HOUR

    def test_correct_vals(self):

        result = self.run_func()

        expected_20120918 = [4, 5, 2, 4, 9, 5, 4, 9, 15, 7, 7, 7, 7, 9, 15, 3, 9, 7, 5, 5, 7, 5, 7, 12]
        expected_20191029 = [15, 0, 0, 7, 12, 4, 4, 9, 6, 5, 4, 4, 2, 3, 5, 4, 4, 6, 12, 6, 7, 7, 6, 3]
        expected_20191029_15 = [4, 4, 9, 6, 5, 4, 4, 2, 3, 5, 4, 4, 6, 12, 6, 7, 7, 6, 3, 5, 5, 4, 7, 6]

        self.assertEqual(row_values(result, '2012-09-18 00:00'), expected_20120918)
        self.assertEqual(row_values(result, '2019-10-29 00:00'), expected_20191029)
        self.assertEqual(row_values(result, '2019-10-29 15:00'), expected_20191029_15)

    def test_schema(self):

        self.check_schema(self.run_func())

    def test_csv_exists(self):

        self.check_csv_exists()


if __name__ == '__main__':

    unittest.main()
