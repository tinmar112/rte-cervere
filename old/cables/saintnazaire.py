import numpy as np
import os
import pandas as pd
import pytz

from old.functions.logging_config import logger
from old.cables.cable import Cable

class SaintNazaire(Cable):
    """Extracteur des câbles Saint-Nazaire L1/L2

    Méthodes privées:
        SaintNazaire.__read_data(chemin)
    """

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)
        self._tz = pytz.timezone('CET') # fuseau horaire spécifique au parc

    def __read_data(self, chemin: str) -> None:
        """Routine de lecture actuelle d'un fichier DTS brut"""
        if not chemin.endswith('.txt'):
            pass

        try:
            date = pd.to_datetime(chemin.strip('.txt')[-19:],
                                  format='%Y-%m-%d-%H-%M-%S', utc=True)

            if self._date_debut <= date <= self._date_fin:
                with open (file=chemin, mode='r') as f:
                    lines = f.readlines()
                distances, temps = lines[0], lines[2]

                distances = distances.replace(',','.').strip('\n').split('\t')[1:]
                temps = temps.replace(',','.').strip('\n').split('\t')[1:]

                df = pd.DataFrame(data={'KP': distances, 'temperature': temps}, dtype=np.float32)
                df.insert(loc=0, column='time', value=np.full(shape=(df.shape[0],), fill_value=date))
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")

        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")

    def _loop(self) -> None:
        for year in self._years_to_unpack():
            for fichier in os.listdir(self._dossier + '/' + year):
                self.__read_data(chemin = self._dossier + '/' + year + '/' + fichier)