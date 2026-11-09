import argparse
import yaml

from src.extract_forecasts_utils import *


df_geomag_forecast = get_geomag_forecast(fill_nans=True)
df_SWPC_Kp_7day, df_SWPC_Kp_3day = extract_Kp_from_SWPC_sheet(fill_nans=True)
df_geomag_forecast_ap = convert_Kp_forecast_to_ap('extracted_data/geomag_forecast_3day_3hr_Kp.csv')
df_SWPC_ap_7day = convert_Kp_forecast_to_ap('extracted_data/SWPC_7day_3hr_Kp.csv')
df_SWPC_ap_3day = convert_Kp_forecast_to_ap('extracted_data/SWPC_3day_3hr_Kp.csv')
