# KpAp-forecast-verification
Repository for forecast verification and data extraction of Kp and Ap forecasts


## Pipeline:

1. Run script to download raw data files
    a. Downloads Kp and ap values from GFZ
    b. Downloads geomag_forecast report from SWPC
    c. Downloads SWPC internal 7-day Kp forecast csv hosted on google drive
2. Run script to extract data from files and put them into csvs
    a. Extracts forecast form geomag_forecast report and saves it as csv
    b. Extracts raw Kp vals from GFZ data and saves as csv
3. Run script to make plots showing report availability
4. Run script to create baseline forecasts
5. Run script to conduct analysis


## Executing Pipeline

Pipeline is constructed using snakemake. To run snakemake execute

    snakemake --cores 1

