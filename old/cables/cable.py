import pandas as pd
import pytz
from tqdm import tqdm

from old.functions.logging_config import logger

class Cable:
    """Un extracteur de données pour un câble de liaison LS/LSM."""

    def __init__(self, date_debut: pd.Timestamp, date_fin: pd.Timestamp, dossier: str):
        assert date_debut < date_fin
        self._date_debut = date_debut
        self._date_fin = date_fin
        self._dossier = dossier
        self._data: list[pd.DataFrame] = []
        self._fichiers_lus: int = 0
        self._tz: pytz.tzinfo.BaseTzInfo = pytz.timezone('UTC')

    def _years_to_unpack(self) -> list[str]:
        """
        Donne la liste des années dans lesquelles sont les données.

        Retourne:
            years (list[str]) : liste contenant les années (dossiers) à explorer.
        """
        date_fin = self._date_fin - pd.Timedelta(value=1, unit='sec')
        end = pd.Timestamp(year=date_fin.year, month=1, day=1)
        start = pd.Timestamp(year=self._date_debut.year, month=1, day=1)
        years = [str(date.year) for date in pd.date_range(start, end, freq='YS')]
        return years

    def _loop(self) -> None:
        """Passe dans l'ensemble des dossiers contenant les données."""
        pass

    def _interpolate(self) -> pd.DataFrame:
        """
        Construit la DataFrame contenant toutes les données entre _date_debut et _date_fin
        pour ce parc. Les données sont interpolées, afin d'obtenir une résolution heure par
        heure.

        Retourne:
            df (pandas.DataFrame) : DataFrame des données DTS du parc avec les colonnes
            ['time','KP','temperature']. Résolution temporaire : horaire (temps UTC).
        """

        if not self._data:  # df vide si aucune liste de données
            return pd.DataFrame(columns=['time', 'KP', 'temperature'])

        else:
            df = pd.concat(self._data, axis=0, ignore_index=True)
            logger.info(f"{len(self._data)} mesures temporaires valides chargées")
            df['time'] = df['time'].dt.tz_convert('UTC')

            # interpolation
            grouped = df.groupby(['KP'])

            time_range = pd.date_range(start=self._date_debut,
                                       end=self._date_fin,
                                       freq='h', tz='UTC', inclusive='left')
            new_df = pd.DataFrame(index= time_range,
                                  columns=['KP', 'temperature'], dtype='float32')

            to_concat: list[pd.DataFrame] = []
            logger.info('Interpolation en cours sur la longueur du câble')
            for i in tqdm(grouped.groups.keys(), desc='Interpolation'):
                group_i = grouped.get_group((i,)).set_index('time')
                df_i = pd.concat(objs=[group_i, new_df],
                                 axis=0, ignore_index=False)
                df_i = df_i.sort_index(axis=0)
                df_i = df_i.interpolate(method='time', axis=0,
                                        limit_area='inside') #NaN laissés au bord
                df_i = df_i.loc[time_range].dropna(axis=0, how='any').reset_index(names='time')
                df_i = df_i.drop_duplicates(subset=['time'])
                to_concat.append(df_i)
            # Concaténer sur toute la longueur puis remettre 'temps' comme attribut NetCDF
            df = pd.concat(to_concat, axis=0, ignore_index=True)
            return df

    def extract(self) -> pd.DataFrame:
        """
        Extrait toutes les données DTS du parc entre les dates fournies à l'instanciation.

        Retourne:
            df (pandas.DataFrame): DataFrame contenant les mesures DTS interpolées
        """
        self._loop()
        return self._interpolate()