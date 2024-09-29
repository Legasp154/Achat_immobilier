def mensualité(alpha, C, N):
    return alpha * C / 12 / (1 - (1 + alpha / 12) ** (-12 * N))


def c(n, alpha, C, N):
    m = mensualité(alpha, C, N)
    if n <= 12 * N:
        return (1 + alpha / 12) ** n * (C - 12 * m / alpha) + 12 * m / alpha
    else:
        return 0


def rendement_1(fn, A, n, l, C, fg, i, alpha, N, mu):
    loyer = n*(1-fg-i)*l/C
    taux_apport = (fn+A)/C
    paiement_mens = alpha*n/12/(1-(1+alpha/12)**(-12*N))
    valeur_bien = (1+mu/12)**(n)
    dette = ((1+alpha/12)**n-(1+alpha/12)**(12*N))/(1-(1+alpha/12)**(12*N))
    
    return taux_apport, loyer, paiement_mens, valeur_bien, dette


def rendement_2(perc, rho, n, fg, i, alpha, N, mu):
    loyer = n*(1-fg-i)*rho
    taux_apport = perc
    paiement_mens = alpha*n/12/(1-(1+alpha/12)**(-12*N))
    valeur_bien = (1+mu/12)**(n)
    dette = ((1+alpha/12)**n-(1+alpha/12)**(12*N))/(1-(1+alpha/12)**(12*N))
    
    return taux_apport, loyer, paiement_mens, valeur_bien, dette