# data_filter(data_dict, filter=None)
#   - filter:
#       - (Default) filter=None: Nur die ISMN-Messung unmittelbar
#       vor S1-Aufnahme
#       - filter="mean": Durchschnitt der ISMN-Messungen bilden
#       (müssen nur überlegen was mehr Sinn macht. Entweder zB 3 Messungen vor
#       S1-Aufnahme oder villt 2 Messungen davor und 1 danach?)
#   - Output: Neuer dataframe in der dict (time / ismn_data / s1_data)
