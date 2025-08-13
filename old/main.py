from functions.update import update

nom_cable = '.S.LLL91BAIXA'

path_raw = f"//nashdprdif274/SMB_DTS-DAS/DTS/RAW/{nom_cable}"
path_save = f"//nashdprdif274/SMB_DTS-DAS/DTS/{nom_cable}"

if __name__ == "__main__":
    update(nom_cable, path_raw, path_save)