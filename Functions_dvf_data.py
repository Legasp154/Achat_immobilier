import os
import pandas as pd
import requests
from tqdm import tqdm
from config import data_dvf_path, data_path, file_INSEE

# Download data from dvf database
def create_data_folder() -> None:
    if not os.path.exists(f"{data_dvf_path}"):
        os.makedirs(f"{data_dvf_path}")
    dep_INSEE = set(pd.read_csv(f"{data_path}/{file_INSEE}")["DEP"].to_list())
    to_remove = ["971", "972", "973", "974", "976"]
    dep_INSEE = [dep for dep in dep_INSEE if dep not in to_remove]
    dep_INSEE=["75"]

    for dep in dep_INSEE:
        if not os.path.exists(f"{data_dvf_path}/{dep}"):
            os.makedirs(f"{data_dvf_path}/{dep}")
    os.rmdir(f"{data_dvf_path}/nan")
    if os.path.exists(f"{data_dvf_path}/20"):
        os.rmdir(f"{data_dvf_path}/20")

def get_dvf_data_com(
    commune_code: str, annee_min: str, annee_max: str, timeout=2
) -> list:
    url = "https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?"
    params = {
        "anneemut_min": annee_min,
        "anneemut_max": annee_max,
        "code_insee": commune_code,
    }

    response = requests.get(url, params=params, timeout=timeout).json()
    features = response["features"]
    while response["next"]:
        response = requests.get(response["next"], timeout=timeout).json()
        features = features + response["features"]
    return features

def export_dvf_data(commune_code: str) -> pd.DataFrame:
    dvf_data = get_dvf_data_com(commune_code, 2010, 2025)
    dvf_data = pd.json_normalize(dvf_data, sep="_")
    dvf_data.to_csv(
        f"{data_dvf_path}{commune_code[:2]}/{commune_code}.csv",
        index=False,
    )
    return dvf_data

def get_dvf_data():
    create_data_folder()
    com_INSEE = pd.read_csv(f"{data_path}/{file_INSEE}")["COM"].to_list()
    com_dwnl = []
    for directory in os.scandir(f"{data_dvf_path}"):
        if directory.is_dir():
            com_dwnl = com_dwnl + [
                f[:-4] for f in os.listdir(f"{data_dvf_path}{directory.name}")
            ]
    for com in tqdm(set(com_INSEE) - set(com_dwnl)):
        try:
            export_dvf_data(com)
        except Exception as e:
            pass

def consolidate_dvf_data_dep(dep: str) -> pd.DataFrame:
    all_dfs = []
    for entry in os.scandir(f"{data_dvf_path}{dep}"):
        if entry.is_file() and entry.name.endswith(".csv"):
            try:
                dvf_commune = pd.read_csv(
                    entry.path,
                    skip_blank_lines=True,
                    dtype={"properties_coddep": str},
                )
                dvf_commune["properties_l_codinsee"] = entry.name[:-4]
                dvf_commune = dvf_commune.dropna(
                    subset=["properties_valeurfonc"]
                )
                dvf_commune = dvf_commune.drop(
                    [
                        "geometry",
                        "properties_l_idparmut",
                        "properties_l_idlocmut",
                    ],
                    axis=1,
                )
                all_dfs.append(dvf_commune)
            except Exception as e:
                pass

    if all_dfs:
        dvf_data = pd.concat(all_dfs, ignore_index=True)

        df_grouped = (
            dvf_data.groupby(
                [
                    "properties_l_codinsee",
                    "properties_codtypbien",
                    "properties_anneemut",
                ]
            )
            .agg(
                {
                    "properties_valeurfonc": "sum",
                    "properties_sterr": "sum",
                    "properties_sbati": "sum",
                    "id": "count",
                    "properties_coddep": "max",
                }
            )
            .reset_index()
        )

        df_grouped.to_csv(
            f"{data_dvf_path}/dvf_{dep}_consolidated.csv", index=False
        )
        return df_grouped
    else:
        return None

def consolidate_dvf_data_deps() -> None:
    for directory in tqdm(os.scandir(f"{data_dvf_path}")):
        if directory.is_dir():
            consolidate_dvf_data_dep(directory.name)

def consolidate_dvf_data_France() -> pd.DataFrame:
    all_dfs = []
    for entry in os.scandir(f"{data_dvf_path}"):
        if entry.is_file() and entry.name.endswith(".csv"):
            try:
                df_dep = pd.read_csv(
                    entry.path,
                    dtype={"properties_coddep": str},
                    skip_blank_lines=True,
                )
                all_dfs.append(df_dep)
            except Exception as e:
                pass

    if all_dfs:
        df_deps = pd.concat(all_dfs, ignore_index=True)
        df_grouped = (
            df_deps.groupby(
                [
                    "properties_coddep",
                    "properties_codtypbien",
                    "properties_anneemut",
                ]
            )
            .agg(
                {
                    "properties_valeurfonc": "sum",
                    "properties_sterr": "sum",
                    "properties_sbati": "sum",
                    "id": "sum",
                }
            )
            .reset_index()
        )

        df_grouped.to_csv(f"{data_path}/dvf_consolidated.csv", index=False)
        return df_grouped
    else:
        return None


