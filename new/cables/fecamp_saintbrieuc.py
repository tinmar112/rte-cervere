import numpy as np
import pandas as pd

from functions.logging_config import logger
from cables.cable import Cable

class FecampOuSaintBrieuc(Cable):
    """Extracteur des câbles Fécamp L1/L2 et Saint-Brieuc L1/L2"""

    def __init__(self, date_debut, date_fin, dossier):
        Cable.__init__(self, date_debut, date_fin, dossier)

    def _read_data(self, chemin: str) -> None:

        if not chemin.endswith('.csv'):
            pass

        try:
            date = pd.to_datetime('20' + chemin.strip('.csv')[-12:],
                                  format='%Y%m%d%H%M%S').tz_localize(self._tz)

            if self._date_debut <= date <= self._date_fin:
                with open(chemin, "r", encoding="ISO-8859-1") as f:
                    premiere_ligne = f.readline()
                delim = ';' if ';' in premiere_ligne else ','

                df = pd.read_csv(filepath_or_buffer=chemin, sep=delim,
                                 names=['KP', 'temperature'], skiprows=5)
                if delim == ',':
                    df['KP'] = df['KP'].str.replace(',', '.')
                    df['temperature'] = df['temperature'].str.replace(',', '.')
                df['KP'] = pd.to_numeric(df['KP']).astype(np.float32)
                df['temperature'] = pd.to_numeric(df['temperature']).astype(np.float32)
                df.insert(loc=0, column='time', value=np.full((df.shape[0],), date))
                # retirer les erreurs de mesure
                mask = df['temperature'] >= -273
                if (~mask).sum() > 0:
                    logger.debug(f'Mesures invalides présentes dans le fichier {chemin}')
                df = df[mask]
                self._data.append(df)

                self._fichiers_lus += 1
                if self._fichiers_lus % 100 == 0:
                    logger.info(f"{self._fichiers_lus} fichiers ouverts")

        except Exception as e:
            logger.error(f"Erreur de lecture : {chemin}, {e}")