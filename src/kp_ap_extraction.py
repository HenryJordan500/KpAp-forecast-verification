import pandas as pd
from utils import *

Ap_file = 'Kp_ap_Ap_SN_F107_since_1932.txt'
Kp_ap_file = 'Kp_ap_since_1932.txt'

extract_Ap(Ap_file=Ap_file)
extract_Kp(Kp_file=Kp_ap_file)
extract_ap(ap_file=Kp_ap_file)
