import numpy as np
import requests


def mensualité(alpha, C, N):
    return alpha * C / 12 / (1 - (1 + alpha / 12) ** (-12 * N))


def c(n, alpha, C, N):
    m = mensualité(alpha, C, N)
    if n <= 12 * N:
        return (1 + alpha / 12) ** n * (C - 12 * m / alpha) + 12 * m / alpha
    else:
        return 0


def rendement(n, l, alpha, C, N, mu, fn, A, fg, i):
    m = mensualité(alpha, C, N)
    Cn = c(n, alpha, C, N)
    if (
        n <= 12 * N
    ):  # On généralise la formule après avori remboursé la totalité du prêt
        return (
            n * (l * (1 - i) - m - fg * l)
            + C * (1 + mu) ** (n / 12)
            - Cn
            - (fn + A)
        ) / (fn + A)
    else:
        return (
            n * (l * (1 - i) - fg * l)
            - 12 * N * m
            + C * (1 + mu) ** (n / 12)
            - Cn
            - (fn + A)
        ) / (fn + A)


def get_dvf_data(commune_code, annee_min, annee_max):
    url = "https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?"
    params = {
        "anneemut_min": annee_min,
        "anneemut_max": annee_max,
        "code_insee": commune_code,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()["features"]
        return data
    else:
        print("Erreur lors de la récupération des données")
        return None


def calculate_price_per_sqm(data):
    if not data:
        return None

    records = []
    for item in data:
        properties_item = item.get("properties")
        surface_bati = properties_item.get("sbati")
        surface_terrain = properties_item.get("sterr")
        valeur_fonciere = properties_item.get("valeurfonc")
        if (surface_terrain or surface_bati) and valeur_fonciere:
            if float(surface_bati) + float(surface_terrain) != 0:
                price_per_sqm = float(valeur_fonciere) / (
                    float(surface_bati) + float(surface_terrain)
                )
                records.append(price_per_sqm)

    if records:
        return np.mean(records)
    else:
        return None


def get_avg_price_per_sqm_by_commune(commune_code, start_date, end_date):
    dvf_data = get_dvf_data(commune_code, start_date, end_date)
    avg_price_sqm = calculate_price_per_sqm(dvf_data)

    return avg_price_sqm
