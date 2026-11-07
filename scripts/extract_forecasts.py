import argparse
import yaml

from src.extract_forecasts_utils import *


df_geomag_forecast = get_geomag_forecast(fill_nans=True)
df_SWPC_Kp_7day, df_SWPC_Kp_3day = extract_Kp_from_SWPC_sheet(fill_nans=True)

