import argparse
import yaml

from src.create_baseline_forecasts_utils import *

df_real_Ap_3day = create_3day_Ap_from_real_vals()
df_real_Kp_3day = create_3day_Kp_from_real_vals()
df_real_ap_3day = create_3day_ap_from_real_vals()
df_persistence_Ap_3day = create_3day_Ap_persistence_forecast()
df_persistence_Kp_3day = create_3day_Kp_persistence_forecast()
df_persistence_ap_3day = create_3day_ap_persistence_forecast()
df_reccurence_Ap_3day = create_3day_Ap_recurrence_forecast()
df_reccurence_Kp_3day = create_3day_Kp_recurrence_forecast()


# def main():

#     df_real_ap_3day = create_3day_ap_from_real_vals()

# if __name__ == '__main__':

#     main()