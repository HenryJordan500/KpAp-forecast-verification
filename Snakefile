rule all:
    input:
        "analysis/geomag_forecast_calander.png",
        "extracted_data/3hour_Kp.csv",
        "extracted_data/daily_Ap.csv",
        "extracted_data/3hour_ap.csv",
        "extracted_data/geomag_forecast_3day_3hr_Kp.csv",
        "extracted_data/geomag_forecast_3day_3hr_ap.csv",
        "extracted_data/geomag_forecast_3day_daily_Ap.csv",
        "extracted_data/SWPC_7day_3hr_Kp.csv",
        "extracted_data/SWPC_3day_3hr_Kp.csv",
        "extracted_data/SWPC_7day_3hr_ap.csv",
        "extracted_data/SWPC_3day_3hr_ap.csv",
        "baseline_forecasts/real_3day_daily_Ap.csv",
        "baseline_forecasts/real_3day_3hr_Kp.csv",
        "baseline_forecasts/real_3day_3hr_ap.csv",
        "baseline_forecasts/persistence_3day_daily_Ap.csv",
        "baseline_forecasts/persistence_3day_3hr_Kp.csv",
        "baseline_forecasts/persistence_3day_3hr_ap.csv",
        "baseline_forecasts/recurrence_3day_daily_Ap.csv",
        "baseline_forecasts/recurrence_3day_3hr_Kp.csv",
        "baseline_forecasts/recurrence_3day_3hr_ap.csv",

checkpoint download_data_from_internet:
    output: 
        "raw_data/SWPC_Kp_Forecasts_2011_2025.csv",
        "raw_data/Kp_ap_Ap_SN_F107_since_1932.txt",
        "raw_data/Kp_ap_since_1932.txt",
        geomag = directory("raw_data/geomag_forecast"),
    input:
        script = "scripts/download_swpc_forecasts_and_raw_vals.sh"
    shell:
        """
        bash {input.script}
        n=$(ls {output.geomag}/*.txt 2>/dev/null | wc -l)
        if [ "$n" -eq 0 ]; then echo "No geomag_forecast .txt files downloaded" >&2; exit 1; fi
        echo "Downloaded $n geomag_forecast files"
        """


def geomag_forecast_files(wildcards):
    d = checkpoints.download_data_from_internet.get().output.geomag
    dates = glob_wildcards(f"{d}/{{date}}geomag_forecast.txt").date
    return expand(f"{d}/{{date}}geomag_forecast.txt", date=dates)


rule extract_SWPC_forecast:
    output:
        "extracted_data/geomag_forecast_3day_3hr_Kp.csv",
        "extracted_data/geomag_forecast_3day_3hr_ap.csv",
        "extracted_data/geomag_forecast_3day_daily_Ap.csv",
        "extracted_data/SWPC_7day_3hr_Kp.csv",
        "extracted_data/SWPC_3day_3hr_Kp.csv",
        "extracted_data/SWPC_7day_3hr_ap.csv",
        "extracted_data/SWPC_3day_3hr_ap.csv",
    input:
        "raw_data/SWPC_Kp_Forecasts_2011_2025.csv",
        script = "scripts/extract_forecasts.py",
        utils = "src/extract_forecasts_utils.py",
        geomag = geomag_forecast_files,
    shell:
        """
        python -m scripts.extract_forecasts
        """

rule extract_raw_kp_Ap_ap:
    output:
        "extracted_data/3hour_Kp.csv",
        "extracted_data/daily_Ap.csv",
        "extracted_data/3hour_ap.csv",
    input:
        "raw_data/Kp_ap_Ap_SN_F107_since_1932.txt",
        "raw_data/Kp_ap_since_1932.txt",
        script = "scripts/get_raw_kp_ap.py",
        utils = "src/get_raw_kp_ap_utils.py",
    shell:
        """
        python -m scripts.get_raw_kp_ap
        """


rule create_baseline_forecasts:
    output:
        "baseline_forecasts/real_3day_daily_Ap.csv",
        "baseline_forecasts/real_3day_3hr_Kp.csv",
        "baseline_forecasts/real_3day_3hr_ap.csv",
        "baseline_forecasts/persistence_3day_daily_Ap.csv",
        "baseline_forecasts/persistence_3day_3hr_Kp.csv",
        "baseline_forecasts/persistence_3day_3hr_ap.csv",
        "baseline_forecasts/recurrence_3day_daily_Ap.csv",
        "baseline_forecasts/recurrence_3day_3hr_Kp.csv",
        "baseline_forecasts/recurrence_3day_3hr_ap.csv",
    input:
        "extracted_data/3hour_Kp.csv",
        "extracted_data/daily_Ap.csv",
        "extracted_data/3hour_ap.csv",
        script = "scripts/create_baseline_forecasts.py",
        utils = "src/create_baseline_forecasts_utils.py",
    shell:
        """
        python -m scripts.create_baseline_forecasts
        """


rule make_availability_plots:
    output:
        "analysis/geomag_forecast_calander.png"
    input:
        script = "scripts/make_calanders.py",
        utils = "src/make_calanders_utils.py",
        geomag = geomag_forecast_files,
    shell:
        """
        python -m scripts.make_calanders
        """