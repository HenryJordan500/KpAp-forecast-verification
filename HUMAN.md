# Human Discussion of Key Decisions and Results for Project

## Data Preprocessing

### SWPC Forecast Issue Time

The SWPC Kp forecasts from the geomag_forecast and three_day_forecast reports include an issue time. The more extensive Kp forecast from the internal SWPC spreadsheet only provides a day that it was issued. It is a neccessary step in the analysis to determine a time at which it was issued in order to compare it to the correct baseline forecast. 

We compared the forecasts within the SWPC sheet to those in the geomag_forecast and three_day_forecast reports. We found that both the three_day_forecast and geomag_forecast matched very well (over 95% of slots match). The geomag_forecast report was more often what was represented on the first day (96% vs. 88%) while both forecasts were provided by the sheet 99% of the time on the 2nd and 3rd day. 

Given that the issue time of the three_day_forecast is provided around 3 hours after the geomag_forecast, it would appear that the sheet is generated around the time of the geomag_forecast. Then, as new information becomes available, a human forecaster slightly tweaks some of these values as new information comes in between the releases of geomag_forecast and three_day_forecast. As there is not a 100% match between any of the forecasts it is unclear exactly when the sheet is generated and how it is modified between each forecast is released. However, I think we can anchor it to the geomag_forecast and say that it is likely generated slightly before the report is released and then modified as new information is available to generate the reports. 

The decision is that the forecast will be declared issued at 21:00UTC on the day indicated in the SWPC sheet