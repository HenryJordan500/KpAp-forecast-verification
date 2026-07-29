#geomag_forecast
wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/geomag_forecast https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/geomag_forecast/

# three_day_forecast
# wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/three_day_forecast https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/3day_forecast/

# daypre
#wget -r -np -nd -A "*.txt" -R "robots.txt" -P raw_data/daypre https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/daypre/

# # the_weekly
# wget -r -np -nd -A "*.pdf" -R "Usr_guide.pdf" -P raw_data/the_weekly https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/weekly_reports/PRFs_of_SGD/

# # RSGA
# wget -r -np -nd -A "*.pdf, *.txt" -R "Usr_guide.pdf, robots.txt" -P raw_data/rsga https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/reports_solar_geophysical_activity/

# SWPC Internal Data
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1Vth9tXoFJTah5x3jrbxbwn3FASPnOVWs" -O raw_data/SWPC_Kp_Forecasts_2011_2025.csv

# Download raw Kp and ap Data
wget https://kp.gfz.de/fileadmin/files_for_gfz_cms/Kp_ap_Ap_SN_F107_since_1932.txt -O raw_data/Kp_ap_Ap_SN_F107_since_1932.txt
wget https://kp.gfz.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt -O raw_data/Kp_ap_since_1932.txt