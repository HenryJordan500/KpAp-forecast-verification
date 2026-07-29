rule all:
    input:
        "analysis/geomag_forecast_calander.png",
        "processed_data/geomag_forecast_3dayKp.csv"

rule download_data_from_internet:
    output: 
        "raw_data/SWPC_Kp_Forecasts_2011_2025.csv",
        "raw_data/Kp_ap_Ap_SN_F107_since_1932.txt",
        "raw_data/Kp_ap_since_1932.txt",
#         directory("raw_data/daypre"),
        directory("raw_data/geomag_forecast"),
#         directory("raw_data/three_day_forecast")
    input:
        script = "scripts/download_swpc_forecasts_and_raw_vals.sh"
    shell:
        """
        bash {input.script}
        """

rule extract_geomag_forecast:
    output:
        "processed_data/geomag_forecast_3dayKp.csv",
    input:
        script = "scripts/extract_forecasts.py"
    shell:
        """
        python -m scripts.extract_forecasts
        """

rule extract_raw_kp:
    output:
        "processed_data/3hour_Kp.csv"
    input:
        "scripts/get_raw_kp_ap.py"
    shell:
        """
        python -m scripts.get_raw_kp_ap
        """

rule make_availability_plots:
    output:
        "analysis/geomag_forecast_calander.png"
    input:
        "scripts/make_calanders.py"
    shell:
        """
        python -m scripts.make_calanders
        """

# rule create_baseline_forecasts:
#     output:
#         ""
#     input:
#         ""
#     shell:
#         """
#         """