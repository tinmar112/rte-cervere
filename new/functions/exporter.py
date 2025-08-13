import os
import pandas as pd
import xarray as xr

def exporter(df, path_save):
    """
    Exporte les données DTS (format long) sous forme de fichiers NetCDF compressés, un par mois.

    Paramètres :
        df (pandas.DataFrame): DataFrame contenant les colonnes 'time', 'KP' et 'temperature'
        path_save (str): Dossier où sauvegarder les fichiers NetCDF

    Retour :
        dict[(year, month)] (xarray.DataArray) : DataArray sauvegardé
    """
    df = df.copy()
    df['time'] = df['time'].dt.tz_localize(None)
    # Ajout des colonnes année et mois
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month

    resultat = {}

    # Groupement par année et mois
    grouped = df.groupby(['year', 'month'])

    for (year, month), group in grouped:
        # Tri et nettoyage
        group = group.sort_values(['time', 'KP'])

        # Pivot pour avoir un tableau 2D temps x KP
        pivot = group.pivot(index='time', columns='KP', values='temperature')

        # Conversion en DataArray
        theta = xr.DataArray(
            pivot.values,
            coords=[pivot.index, pivot.columns],
            dims=["time", "KP"],
            name="temperature"
        )

        # Attributs NetCDF
        theta.attrs["units"] = "degC"
        theta.attrs["description"] = f"Température horaire - {year}-{month:02d}"

        # Nom du fichier
        nom_nc = f"temp_dts_{year}_{month:02d}.nc"
        filename = os.path.join(path_save, nom_nc)

        # Export NetCDF compressé
        theta.to_netcdf(
            filename,
            encoding={"temperature": {"zlib": True, "complevel": 4}}
        )

        resultat[(year, month)] = theta

    return resultat