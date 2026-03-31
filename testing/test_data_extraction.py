import pandas as pd
import numpy as np

import pandas.testing as pdt
import numpy.testing as npt
import unittest

import src.get_raw_kp_ap_utils as get_raw_kp_ap_utils


class TestKpApExtraction(unittest.TestCase):

    # Function to find missing dates in list of datetimes
    def test_datetime_conversion(self):

        years = [1999,2000,1998]
        months = [1,2,3]
        days = [11,14,15]
        hours = [00.0, 10.0, 01.0]
        other = [2, 1, 0]

        full_test_data_hr = pd.DataFrame({'#YYY': years,
                                       'MM': months,
                                       'DD': days,
                                       'hh.h': hours,
                                       'other': other})
        
        full_test_data_nohr = pd.DataFrame({'#YYY': years,
                                       'MM': months,
                                       'DD': days,
                                       'other': other})
        
        ans_nohr = pd.Series([np.datetime64('1999-01-11'),
                              np.datetime64('2000-02-14'),
                              np.datetime64('1998-03-15')])
        
        ans_hr = pd.Series([np.datetime64('1999-01-11 00:00:00'),
                            np.datetime64('2000-02-14 10:00:00'),
                            np.datetime64('1998-03-15 01:00:00')])

        pdt.assert_series_equal(ans_nohr, get_raw_kp_ap_utils.convert_datetime(full_test_data_nohr))
        pdt.assert_series_equal(ans_hr, get_raw_kp_ap_utils.convert_datetime(full_test_data_hr))

        return
    def test_missing_dates(self):
        return
    def test_check_missing_data(self):
        return
    def test_Ap_extraction(self):
        return
    def test_Kp_extraction(self):
        return
    def test_ap_extraction(self):
        return


if __name__ == '__main__':

    unittest.main()
