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
