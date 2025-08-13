import os
import pandas as pd
import pytz

def latest(dossier: str, tz=pytz.timezone('UTC')) -> pd.Timestamp:
    """
    Détermine le mois le plus récent déjà exporté sous format xz.

    Arg:
        dossier (str) : Chemin du dossier d'export

    Retourne:
        latest_mo (pandas.DateTime) : Le mois le plus récent déjà présent dans le répertoire
    """
    latest_mo = pd.Timestamp(year=2015, month=1, day=1, tz=tz)
    for compressed_file in os.listdir(dossier):
        if compressed_file.endswith(".xz"):
            month = pd.to_datetime(compressed_file[-13:-6] + '_01',
                                   format='%Y_%m_%d').tz_localize(tz) # 1er jour du mois
            if month >= latest_mo:
                if month.month == 12:
                    latest_mo = pd.Timestamp(year=month.year+1, month=1, day=1, tz=tz)
                else:
                    latest_mo = pd.Timestamp(year=month.year, month=month.month+1, day=1, tz=tz)
    return latest_mo