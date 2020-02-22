import glob
from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import preprocess as prep

user_input = pkg.setup_pkg()

prep.data_handling()  # Uses 0.05 as default value to filter for measurement depth


#############################
## Funktion erstellen, die:
# 1. Alle .stm Daten aus dem "./data/ISMN_Filt" Order als dataframes importiert
# 2. Eine CSV Datei exportiert mit den Stationen und den jeweiligen
#    Koordinaten
# 3. Eine dictionary erstellt mit folgendem Aufbau:
#           - key       = Name der station
#           - val_1     = [lat, long]
#           - val_2     = Dataframe mit den Messungen
#                         (datum-zeit / Messwert / flag?)


sm_files_filt = [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm", recursive=True)]

dict_ISMN = prep.data_import(sm_files_filt)


