import pandas as pd
import requests


def get_dvf_data(commune_code, annee_min, annee_max, timeout=2):
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


def export_dvf_data(commune_code):
    dvf_data = get_dvf_data(commune_code, 2014, 2024)
    dvf_data = pd.json_normalize(dvf_data, sep="_")
    dvf_data.to_csv(f"Data/valeurs foncières/{commune_code}.csv", index=False)


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
