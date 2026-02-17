# geomag_forecast
wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/geomag_forecast https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/geomag_forecast/

# three_day_forecast
wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/three_day_forecast https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/3day_forecast/

# daypre
wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/daypre https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/daypre/

# the_weekly
wget -r -np -nd -A "*.pdf" -R "Usr_guide.pdf" -P raw_data/the_weekly https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/weekly_reports/PRFs_of_SGD/