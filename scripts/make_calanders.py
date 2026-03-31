import argparse
import yaml
import datetime as dt

from src.make_calanders_utils import *

parser = argparse.ArgumentParser(description='Input',
                                 prog='Create calander plots of reports')

parser.add_argument('--config',
                    type=str,
                    help='Config file what contains arguments for calander plots',
                    required=False,
                    default='configs/calanders.yml')

args = parser.parse_args()

f = open(file=args.config, mode='r')
config = yaml.load(f, Loader=yaml.FullLoader)
f.close()

for key in config.keys():

    plot_config = config[key]
    
    if plot_config['include'] is True:

        start_date = plot_config['start_date']
        end_date = plot_config['end_date']
        width = plot_config['width']

        # Clunky, fix at some point
        if key == 'three_day_forecast':
            start_date = dt.datetime.combine(start_date, dt.time(hour=00, minute=30))

        create_daily_calander_plot(report_name=key,
                                   start_date=start_date,
                                   end_date=end_date,
                                   width=width)
    