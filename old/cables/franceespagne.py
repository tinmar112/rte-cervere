import numpy as np
import os
import pandas as pd
import pytz

from old.functions.logging_config import logger
from old.cables.cable import Cable

class FranceEspagne(Cable):
    """Extracteur des câbles France-Espagne 1 et 2

    Méthodes privées:
        FranceEspagne.__read_data_15_17(chemin)
        FranceEspagne.__read_data_18_now(chemin)
    """

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)
        self._tz = pytz.timezone('CET')

    def __read_data_15_17(self, chemin: str) -> None:
        """Routine de lecture d'un fichier DTS brut entre 2015 et 2017"""
        if not chemin.endswith('.csv'):
            pass
        try:
            date = pd.to_datetime(chemin.strip('.csv')[-19:], format='%Y.%m.%d-%H.%M.%S').tz_localize(self._tz)
            if self._date_debut <= date <= self._date_fin:
                df = pd.read_csv(filepath_or_buffer=chemin, names=['KP', 'temperature'],
                                 sep=';', decimal=',',
                                 dtype={'KP': np.float32, 'temperature': np.float32})
                df.insert(loc=0, column='time', value=np.full((df.shape[0],), date))
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers parcourus")
        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")

    def __read_data_18_now(self, chemin: str) -> None:
        """Routine de lecture d'un fichier DTS brut entre 2018 et aujourd'hui"""
        if not chemin.endswith('.csv'):
            pass
        try:
            date = pd.to_datetime(chemin.strip('.csv')[-15:], format='%Y%m%d_%H%M%S').tz_localize(self._tz)
            if self._date_debut <= date <= self._date_fin:
                df = pd.read_csv(filepath_or_buffer=chemin,
                                 names=['KP', 'temperature'], skiprows=1,
                                 dtype={'KP': np.float32, 'temperature': np.float32})
                df.insert(loc=0, column='time', value=np.full((df.shape[0],), fill_value=date))
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")
        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")

    def _loop(self) -> None:

        for year in self._years_to_unpack():

            if int(year) <= 2017:
                for fichier in os.listdir(self._dossier + '/' + year):
                    self.__read_data_15_17(chemin = self._dossier + '/' + year + '/' + fichier)

            elif 2018 <= int(year) <= 2022:
                for day in os.listdir(self._dossier + '/' + year):
                    for fichier in os.listdir(self._dossier + '/' + year + '/' + day):
                        self.__read_data_18_now(chemin = self._dossier + '/' + year + '/' + day + '/' + fichier)

            elif int(year) >= 2023:
                for fichier in os.listdir(self._dossier + '/' + year):
                    self.__read_data_18_now(chemin = self._dossier + '/' + year + '/' + fichier)

            else:
                logger.error('Vérifier les plages de date renseignées.')