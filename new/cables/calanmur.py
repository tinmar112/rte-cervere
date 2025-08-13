import numpy as np
import pandas as pd

from functions.logging_config import logger
from cables.cable import Cable

class CalanMur(Cable):
    """Extracteur du câble Calan Mur"""

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)

    def _read_data(self, chemin: str) -> None:

        if not chemin.endswith('.txt'):
            pass

        try:
            date = pd.to_datetime(chemin.strip('.txt')[-19:],
                                  format="%Y-%m-%d-%H-%M-%S").tz_localize(self._tz)
            if self._date_debut <= date <= self._date_fin:

                with open(chemin, "r") as f:
                    lines = f.readlines()
                kp = lines[8].strip('\n').replace(',', '.').split(';')[1:]
                temp = lines[10].strip('\n').replace(',', '.').split(';')[1:]
                df = pd.DataFrame({'time': np.full((len(kp),), date),
                                   'KP': kp, 'temperature': temp})
                df['KP'] = pd.to_numeric(df['KP'], errors='coerce').astype(np.float32)
                df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce').astype(np.float32)
                self._data.append(df)
                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")

        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")