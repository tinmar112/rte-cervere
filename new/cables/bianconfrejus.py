import numpy as np
import pandas as pd

from functions.logging_config import logger
from cables.cable import Cable

class BianconFrejus(Cable):
    """Extracteur du câble Biançon Fréjus

    Méthodes privées:
        BianconFrejus.__read_data(chemin)"""

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)

    def _read_data(self, chemin: str) -> None:
        if not chemin.endswith('.csv'):
            pass
        try:
            df = pd.read_csv(chemin, header=None, dtype='object').drop(labels=[2, 3], axis=0)
            for i in range(1, df.shape[1]):
                df_i = df.iloc[:, [0, i]]
                date, time = df_i.iloc[0, 1], df_i.iloc[1, 1]
                date_time = pd.to_datetime(date + '-' + time,
                                           format='%d.%m.%Y-%H:%M:%S').tz_localize(self._tz)
                if self._date_debut <= date_time <= self._date_fin:

                    df_i = df_i.drop(labels=[0, 1], axis=0)
                    df_i.columns = ['KP', 'temperature']
                    df_i.insert(loc=0, column='time', value=np.full((df_i.shape[0],), fill_value=date_time))
                    df_i = df_i.astype({'KP': np.float32, 'temperature': np.float32})
                    self._data.append(df_i)
                    self._fichiers_lus += 1
                    if self._fichiers_lus % 100 == 0:
                        logger.info(f"{self._fichiers_lus} mesures ouvertes")

        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")