import argparse
import yaml

from src.extract_forecasts_utils import *

parser = argparse.ArgumentParser(description='Input',
                                 prog='Extract forecast data from reports')

parser.add_argument('--config',
                    type=str,
                    help='Config file what contains arguments for extracting forecasts from reports',
                    required=False,
                    default='configs/extract_forecasts.yml')

args = parser.parse_args()

f = open(file=args.config, mode='r')
config = yaml.load(f, Loader=yaml.FullLoader)
f.close()

if config['daypre']['extract'] is True:
    df_daypre = get_daypre_forecast(fill_nans=config['daypre']['fill_nans'])

if config['geomag_forecast']['extract'] is True:
    df_geomag_forecast = get_geomag_forecast(fill_nans=config['geomag_forecast']['fill_nans'])