import numpy as np
import os
import pandas as pd
import pytz

from old.functions.logging_config import logger
from old.cables.cable import Cable

class BianconFrejus(Cable):
    """Extracteur du câble Biançon Fréjus

    Méthodes privées:
        BianconFrejus.__read_data(chemin)"""

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)
        self._tz = pytz.timezone('CET') # Dans les fichiers BF, on s'arrête au jour suivant +2h en été => CET

    def __read_data_14_17(self, chemin: str) -> None:
        """Routine de lecture d'un fichier DTS brut entre 2015 et 2017"""
        if not chemin.endswith('.csv'):
            pass
        try:
            date = pd.to_datetime(chemin.strip('.csv')[-19:],
                                  format='%Y.%m.%d-%H.%M.%S').tz_localize(self._tz)
            if self._date_debut <= date <= self._date_fin:
                df = pd.read_csv(filepath_or_buffer=chemin, names=['KP', 'temperature'],
                                 sep=';', decimal=',',
                                 dtype={'KP': np.float32, 'temperature': np.float32})
                df.insert(loc=0, column='time', value=np.full((df.shape[0],), date))
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")
        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")

    def __read_data_18_now(self, chemin: str) -> None:
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

    def _loop(self) -> None:
        for year in self._years_to_unpack():
            if int(year) <= 2017:
                for fichier in os.listdir(self._dossier + '/' + year):
                    self.__read_data_14_17(self._dossier + '/' + year + '/' + fichier)
            elif int(year) >= 2018:
                for fichier in os.listdir(self._dossier + '/' + year):
                    self.__read_data_18_now(self._dossier + '/' + year + '/' + fichier)
        logger.info(f"{self._fichiers_lus} fichiers ouverts")