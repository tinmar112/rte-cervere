import numpy as np
import os
import pandas as pd

from old.functions.logging_config import logger
from old.cables.cable import Cable

class Courseulles(Cable):
    """Extracteur des câbles Courseulles L1/L2

    Méthodes privées:
        Courseulles.__read_data(chemin)
    """

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)

    def __read_data(self, chemin: str) -> None:
        """Routine de lecture actuelle d'un fichier DTS brut"""
        if not chemin.endswith('.csv'):
            pass

        try:
            date = pd.to_datetime(chemin.strip('_UTC.csv')[-15:], format='%Y%m%d_%H%M%S', utc=True)
            if self._date_debut <= date <= self._date_fin:

                df = pd.read_csv(filepath_or_buffer=chemin,
                                 sep=';', names=['KP', 'temperature'], skiprows=1,
                                 dtype={'KP': np.float32, 'temperature': np.float32})
                df.insert(loc=0, column='time', value=np.full((df.shape[0],), date))
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")

        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")

    def _loop(self) -> None:
        for folder in os.listdir(self._dossier):
            for fichier in os.listdir(self._dossier + '/' + folder):
                self.__read_data(chemin = self._dossier + '/' + folder + '/' + fichier)