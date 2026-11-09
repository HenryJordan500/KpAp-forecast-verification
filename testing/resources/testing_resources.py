import numpy as np
import pandas as pd
import datetime as dt

# Used across many tests
daypre_test_files_dir = 'testing/resources/testing_files/testing_daypre'
three_day_forecast_test_files_dir = 'testing/resources/testing_files/testing_three_day_forecast'


expected_get_daypre_no_nans_dict = {'Forecast Issued': np.array([dt.date(2013, 12, 22), dt.date(2013, 12, 23), dt.date(2013, 12, 25)], dtype='datetime64[ns]'),
                                '1dAp': [5, 5, 10],
                                '2dAp': [5, 10, 8],
                                '3dAp': [10, 8, 5]}

expected_get_daypre_no_nans = pd.DataFrame(expected_get_daypre_no_nans_dict)

expected_get_daypre_nans_dict = {'Forecast Issued': np.array([dt.date(2013, 12, 22), dt.date(2013, 12, 23), dt.date(2013, 12, 24), dt.date(2013, 12, 25)], dtype='datetime64[ns]'),
                             '1dAp': [5, 5, np.nan, 10],
                             '2dAp': [5, 10, np.nan, 8],
                             '3dAp': [10, 8, np.nan, 5]}

expected_get_daypre_nans = pd.DataFrame(expected_get_daypre_nans_dict)

expected_get_geomag_forecast_Kp_no_nans_dict = {'Forecast Issued': np.array([dt.date(2022, 11, 14), dt.date(2022, 11, 15), dt.date(2022, 11, 17)], dtype='datetime64[ns]'),
                                         '3hrKp': [2.00, 1.67, 1.33], 
                                         '6hrKp': [2.00, 2.67, 1.67], 
                                         '9hrKp': [1.33, 2.00, 3.00], 
                                         '12hrKp': [1.33, 1.67, 2.67],
                                         '15hrKp': [2.00, 1.33, 2.33], 
                                         '18hrKp': [3.00, 1.33, 2.33], 
                                         '21hrKp': [3.00, 2.00, 2.67], 
                                         '24hrKp': [3.00, 2.67, 2.67], 
                                         '27hrKp': [2.67, 1.67, 2.67],
                                         '30hrKp': [2.67, 1.33, 2.67],
                                         '33hrKp': [2.67, 1.33, 2.33],
                                         '36hrKp': [2.67, 1.33, 2.33],
                                         '39hrKp': [2.67, 1.33, 3.00],
                                         '42hrKp': [2.00, 1.33, 3.33],
                                         '45hrKp': [2.00, 1.67, 4.00],
                                         '48hrKp': [2.33, 1.67, 4.67],
                                         '51hrKp': [1.67, 1.67, 4.67],
                                         '54hrKp': [1.33, 1.67, 4.33],
                                         '57hrKp': [1.33, 1.33, 5.33],
                                         '60hrKp': [1.33, 1.67, 3.33], 
                                         '63hrKp': [1.33, 2.33, 2.67],
                                         '66hrKp': [1.33, 2.33, 3.00],
                                         '69hrKp': [1.67, 2.67, 3.67],
                                         '72hrKp': [1.67, 2.67, 4.00]}

expected_get_geomag_forecast_Kp_no_nans = pd.DataFrame(expected_get_geomag_forecast_Kp_no_nans_dict)

expected_get_geomag_forecast_Ap_no_nans_dict = {'Forecast Issued': np.array([dt.date(2022, 11, 14), dt.date(2022, 11, 15), dt.date(2022, 11, 17)], dtype='datetime64[ns]'),
                                '1dAp': [10, 8, 10],
                                '2dAp': [10, 5, 18],
                                '3dAp': [5, 8, 28]}

expected_get_geomag_forecast_Ap_no_nans = pd.DataFrame(expected_get_geomag_forecast_Ap_no_nans_dict)

expected_extract_kp_from_SWPC_sheet_7day_dict = {'Forecast Issued':  np.array([dt.date(2011, 11, 28), dt.date(2012, 9, 24)], dtype='datetime64[ns]'),
                                                 '3hrKp': [1.00, 1.33],
                                                 '6hrKp': [1.00, 1.67],
                                                 '9hrKp': [1.00, 1.33],
                                                 '12hrKp': [4.67, 1.33],
                                                 '15hrKp': [4.00, 1.33],
                                                 '18hrKp': [4.00, 1.33], 
                                                 '21hrKp': [3.33, 1.33], 
                                                 '24hrKp': [3.33, 1.33],
                                                 '27hrKp': [3.00, 1.33],
                                                 '30hrKp': [2.67, 1.33],
                                                 '33hrKp': [2.67, 1.33],
                                                 '36hrKp': [2.67, 1.33],
                                                 '39hrKp': [2.67, 1.33],
                                                 '42hrKp': [2.67, 1.33],
                                                 '45hrKp': [2.67, 1.33],
                                                 '48hrKp': [2.67, 1.33],
                                                 '51hrKp': [2.0, 1],
                                                 '54hrKp': [1.67, 1],
                                                 '57hrKp': [2.33, 1],
                                                 '60hrKp': [2.33, 1], 
                                                 '63hrKp': [2.33, 1.33],
                                                 '66hrKp': [2.33, 1.33],
                                                 '69hrKp': [2.33, 1.33],
                                                 '72hrKp': [2.33, 1.33],
                                                 '75hrKp': [1.67, 1.67],
                                                 '78hrKp': [1.67, 1.33],
                                                 '81hrKp': [1.67, 1.33],
                                                 '84hrKp': [1.33, 1.33],
                                                 '87hrKp': [1.33, 1.33],
                                                 '90hrKp': [1.33, 1.33],
                                                 '93hrKp': [1.33, 1.67],
                                                 '96hrKp': [1.33, 1.67],
                                                 '99hrKp': [1.67, 1.67],
                                                 '102hrKp': [1.33, 1.33],
                                                 '105hrKp': [1.33, 1.33],
                                                 '108hrKp': [1.33, 1.33],
                                                 '111hrKp': [1.33, 1.33],
                                                 '114hrKp': [1.33, 1.33],
                                                 '117hrKp': [1.67, 1.67],
                                                 '120hrKp': [1.67, 1.67],
                                                 '123hrKp': [1.67, 1.67],
                                                 '126hrKp': [1.33, 1.33],
                                                 '129hrKp': [1.33, 1.33],
                                                 '132hrKp': [1.33, 1.33],
                                                 '135hrKp': [1.33, 1.33],
                                                 '138hrKp': [1.33, 1.33],
                                                 '141hrKp': [1.67, 1.67],
                                                 '144hrKp': [1.67, 1.67],
                                                 '147hrKp': [1.67, 1.67],
                                                 '150hrKp': [1.33, 1.33],
                                                 '153hrKp': [1.67, 1.33],
                                                 '156hrKp': [1.33, 1.33],
                                                 '159hrKp': [1.67, 1.33],
                                                 '162hrKp': [1.33, 1.33],
                                                 '165hrKp': [1.33, 1.67],
                                                 '168hrKp': [1.33, 1.67]}

expected_extract_kp_from_SWPC_sheet_7day = pd.DataFrame(expected_extract_kp_from_SWPC_sheet_7day_dict)


expected_extract_kp_from_SWPC_sheet_3day_dict = {'Forecast Issued':  np.array([dt.date(2011, 11, 28), dt.date(2012, 9, 24)], dtype='datetime64[ns]'),
                                                 '3hrKp': [1.00, 1.33],
                                                 '6hrKp': [1.00, 1.67],
                                                 '9hrKp': [1.00, 1.33],
                                                 '12hrKp': [4.67, 1.33],
                                                 '15hrKp': [4.00, 1.33],
                                                 '18hrKp': [4.00, 1.33], 
                                                 '21hrKp': [3.33, 1.33], 
                                                 '24hrKp': [3.33, 1.33],
                                                 '27hrKp': [3.00, 1.33],
                                                 '30hrKp': [2.67, 1.33],
                                                 '33hrKp': [2.67, 1.33],
                                                 '36hrKp': [2.67, 1.33],
                                                 '39hrKp': [2.67, 1.33],
                                                 '42hrKp': [2.67, 1.33],
                                                 '45hrKp': [2.67, 1.33],
                                                 '48hrKp': [2.67, 1.33],
                                                 '51hrKp': [2.0, 1],
                                                 '54hrKp': [1.67, 1],
                                                 '57hrKp': [2.33, 1],
                                                 '60hrKp': [2.33, 1], 
                                                 '63hrKp': [2.33, 1.33],
                                                 '66hrKp': [2.33, 1.33],
                                                 '69hrKp': [2.33, 1.33],
                                                 '72hrKp': [2.33, 1.33]}

expected_extract_kp_from_SWPC_sheet_3day = pd.DataFrame(expected_extract_kp_from_SWPC_sheet_3day_dict)


expected_convert_Kp_forecast_to_ap_dict = {'Forecast Issued': np.array([dt.date(2011, 11, 28), dt.date(2011, 11, 29)], dtype='datetime64[ns]'),
                                           '3hrap': [2, np.nan],
                                           '6hrap': [22, np.nan],
                                           '9hrap': [400, np.nan]}

expected_convert_Kp_forecast_to_ap = pd.DataFrame(expected_convert_Kp_forecast_to_ap_dict)



