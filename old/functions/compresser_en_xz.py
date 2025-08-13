import lzma
import os
import shutil

def compresser_en_xz(fichier_nc: str, fichier_xz: str =None):
    """
    Compresse un fichier nc en un fichier xz.

    Paramètres:
        fichier_nc (str): chemin du fichier à compresser en xz
        fichier_xz (str, optionnel): chemin du fichier dans lequel compresser

    Retourne :
        fichier_xz (str)
    """

    # Si aucun fichier xz n'est présent, on en crée un avec le même nom.
    if fichier_xz is None:
        fichier_xz = fichier_nc + ".xz"

    # Ouverture du fichier nc, à convertir en xz.
    with open(fichier_nc, 'rb') as f_in: # mode lecture binaire 'rb'
        with lzma.open(fichier_xz, mode='wb') as f_out: # mode écriture binaire
            shutil.copyfileobj(f_in, f_out)

    os.remove(fichier_nc)

    return fichier_xz