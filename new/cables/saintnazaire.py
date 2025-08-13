import numpy as np
import pandas as pd
import pytz

from functions.logging_config import logger
from cables.cable import Cable

class SaintNazaire(Cable):
    """Extracteur des câbles Saint-Nazaire L1/L2"""

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)
        self._tz = pytz.timezone('CET') # fuseau horaire spécifique au parc

    def _read_data(self, chemin: str) -> None:

        if not chemin.endswith('.txt'):
            pass

        try:
            date = pd.to_datetime(chemin.strip('.txt')[-19:],
                                  format='%Y-%m-%d-%H-%M-%S').tz_localize(self._tz)

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