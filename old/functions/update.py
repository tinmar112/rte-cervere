import datetime
import pandas as pd
import pytz

from old.functions.logging_config import logger

from old.cables.cable import Cable
from old.cables.bianconfrejus import BianconFrejus
from old.cables.boutretrans import BoutreTrans
from old.cables.calanmur import CalanMur
from old.cables.courseulles import Courseulles
from old.cables.fecamp_saintbrieuc import FecampOuSaintBrieuc
from old.cables.franceespagne import FranceEspagne
from old.cables.noirmoutier import Noirmoutier
from old.cables.saintnazaire import SaintNazaire

from old.functions.latest import latest
from old.functions.exporter import exporter
from old.functions.compresser_en_xz import compresser_en_xz

def update(nom_cable: str, path_raw: str, path_save: str) -> None:
    """
    Implémente la routine de mise à jour des données DTS.

    Args:
        nom_cable (str): Nom du parc
        path_raw (str): Chemin du dossier des données brutes
        path_save (str): Chemin où sont compressées les données sous format xz

    Retourne:
        None
    """

    parcs: dict[str: Cable] = {
        'BIANCL61FREJU': BianconFrejus,
        'BOUTRL61TRANS': BoutreTrans,
        'B.GUEL61PRINQ': SaintNazaire, "B.GUEL62PRINQ": SaintNazaire,
        'B.SSBL61DOBER': FecampOuSaintBrieuc, 'B.SSBL62DOBER': FecampOuSaintBrieuc,
        'CALA5L61MUR': CalanMur,
        'CZSEUL61RANVI': Courseulles, 'CZSEUL62RANVI': Courseulles,
        'G.ROUL61V.ILE': Noirmoutier, 'G.ROUL62V.ILE': Noirmoutier,
        'H.FALL61SAINN': FecampOuSaintBrieuc, 'H.FALL62SAINN': FecampOuSaintBrieuc,
        '.S.LLL91BAIXA': FranceEspagne, '.S.LLL92BAIXA': FranceEspagne
    }

    tz = pytz.timezone('UTC')

    # Détermine la période restant à exporter (entre maintenant et le dernier export).
    now = pd.Timestamp(datetime.datetime.now(), tz=tz)
    then = latest(dossier=path_save, tz=tz)

    # Export mois par mois pour faciliter l'enregistrement
    intervals = pd.date_range(start=then, end=now, freq='MS', normalize=True, tz=tz)
    if len(intervals)<=1:
        logger.warning("Pas de période à mettre à jour")

    for i in range (len(intervals)-1):
        logger.info(f"Mise à jour des données DTS jusqu'au {intervals[-1]} pour : {nom_cable}")
        logger.info(f"Chemin source    : {path_raw}")
        logger.info(f"Chemin export NC : {path_save}")
        logger.info(f"⏳ Intervalle {i+1}/{len(intervals)-1}   : {intervals[i]} ➝ {intervals[i+1]}")

        parc = parcs[nom_cable](date_debut=intervals[i], date_fin=intervals[i + 1], dossier=path_raw)
        df = parc.extract()

        if df.empty:
            logger.error('Compression : aucune nouvelle donnée trouvée')

        else:
            logger.info('Compression NetCDF en cours')
            dataarrays = exporter(df, path_save=path_save)
            # Compression .xz
            for (year, month), _ in dataarrays.items():
                nom_nc = f"temp_dts_{year}_{month:02d}.nc"
                chemin_nc = path_save + '/' + nom_nc
                compresser_en_xz(chemin_nc)
                logger.info(f"[✔] Archive compressée : {chemin_nc}")