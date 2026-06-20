#!/usr/bin/env python3
"""Funcoes do metodo Y (Y-factor) para temperatura equivalente e figura de ruido.

Trabalho extra -- Caracterizacao de LNA (FGA0092 / PRICOM).

Convencao de ENR adotada (referencia a T_0):

    ENR = (T_H - T_0) / T_0   ->   T_H = T_0 * (1 + ENR_lin)

Cadeia de calculo:

    ENR_lin = 10^(ENR_dB / 10)
    T_H     = T_0 * (1 + ENR_lin)
    Y       = N_H / N_C = (T_H + T_e) / (T_C + T_e)
    T_e     = (T_H - Y * T_C) / (Y - 1)
    F       = 1 + T_e / T_0
    NF      = 10 * log10(F)
"""

import math

T0_PADRAO = 290 # K, temperatura de referencia IEEE


def db_para_linear(valor_db):
    """Converte uma razao em dB para escala linear."""
    return 10.0 ** (valor_db / 10.0)


def linear_para_db(valor_lin):
    """Converte uma razao linear para dB."""
    return 10.0 * math.log10(valor_lin)


def y_de_potencias(nh_dbm, nc_dbm):
    """Fator Y linear a partir das potencias HOT e COLD em dBm: Y = N_H - N_C (dB)."""
    return db_para_linear(nh_dbm - nc_dbm)


def temperatura_hot(enr_db, t0=T0_PADRAO):
    """Temperatura 'hot' da fonte: T_H = T_0 * (1 + ENR_lin)."""
    enr_lin = db_para_linear(enr_db)
    return t0 * (1.0 + enr_lin)


def temperatura_equivalente(t_h, y_linear, t_c=T0_PADRAO):
    """Temperatura equivalente de ruido: T_e = (T_H - Y * T_C) / (Y - 1)."""
    if y_linear <= 1.0:
        raise ValueError("O fator Y deve ser maior que 1 (T_H > T_C).")
    return (t_h - y_linear * t_c) / (y_linear - 1.0)


def temperatura_hot_de_te(t_e, y_linear, t_c=T0_PADRAO):
    """Inverso do metodo Y: T_H = T_e * (Y - 1) + Y * T_C."""
    return t_e * (y_linear - 1.0) + y_linear * t_c


def enr_de_hot(t_h, t0=T0_PADRAO):
    """Estima o ENR a partir de T_H: ENR_lin = (T_H - T_0) / T_0. Retorna (linear, dB)."""
    enr_lin = (t_h - t0) / t0
    return enr_lin, linear_para_db(enr_lin)


def fator_ruido(t_e, t0=T0_PADRAO):
    """Fator de ruido linear: F = 1 + T_e / T_0."""
    return 1.0 + t_e / t0


def figura_ruido_db(f_lin):
    """Figura de ruido em dB: NF = 10 * log10(F)."""
    return linear_para_db(f_lin)


def erro_absoluto(medido, calculado):
    """Erro absoluto: medido - calculado."""
    return medido - calculado


def erro_relativo(medido, calculado):
    """Erro relativo percentual em relacao ao valor calculado (de referencia)."""
    return 100.0 * (medido - calculado) / calculado


def calcular_ruido(enr_db, y_linear, t_c=T0_PADRAO, t0=T0_PADRAO):
    """Aplica todo o metodo Y e devolve um dicionario com as grandezas.

    enr_db    -- ENR da fonte de ruido em dB (do catalogo do diodo).
    y_linear  -- fator Y em escala linear (> 1).
    t_c       -- temperatura 'cold'/ambiente em K (tipicamente ~290).
    t0        -- temperatura de referencia em K (290 por padrao).
    """
    enr_lin = db_para_linear(enr_db)
    t_h = temperatura_hot(enr_db, t0=t0)
    t_e = temperatura_equivalente(t_h, y_linear, t_c=t_c)
    f_lin = fator_ruido(t_e, t0=t0)
    nf_db = figura_ruido_db(f_lin)

    return {
        "ENR_dB": enr_db,
        "ENR_linear": enr_lin,
        "T_H": t_h,
        "T_C": t_c,
        "Y_linear": y_linear,
        "Y_dB": linear_para_db(y_linear),
        "T_e": t_e,
        "F_linear": f_lin,
        "NF_dB": nf_db,
    }


def imprimir(res):
    """Imprime de forma organizada o dicionario devolvido por calcular_ruido."""
    print("=" * 44)
    print("  Metodo Y -- Temperatura e figura de ruido")
    print("=" * 44)
    print(f"  ENR            = {res['ENR_dB']:.3f} dB  ({res['ENR_linear']:.4f} linear)")
    print(f"  T_C (ambiente) = {res['T_C']:.2f} K")
    print(f"  T_H (fonte)    = {res['T_H']:.2f} K")
    print(f"  Y              = {res['Y_linear']:.4f}  ({res['Y_dB']:.3f} dB)")
    print("-" * 44)
    print(f"  T_e            = {res['T_e']:.2f} K")
    print(f"  F              = {res['F_linear']:.4f} (linear)")
    print(f"  NF             = {res['NF_dB']:.3f} dB")
    print("=" * 44)


def tabela_comparacao(linhas):
    """Monta um DataFrame comparando medido e calculado.

    linhas -- lista de tuplas (grandeza, medido, calculado).
    Retorna um pandas.DataFrame com as colunas de erro absoluto e relativo.
    """
    import pandas as pd

    df = pd.DataFrame(linhas, columns=["Grandeza", "Medido", "Calculado"])
    df["Erro abs"] = df["Medido"] - df["Calculado"]
    df["Erro %"] = 100.0 * df["Erro abs"] / df["Calculado"]
    # grandezas sem referencia (Medido = None) ficam com traco no lugar do erro
    return df.set_index("Grandeza").round(3).fillna("-")


# ---------------------------------------------------------------------------
# MAIN -- preencha aqui os parametros medidos no laboratorio
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    # ENR da fonte de ruido (dB), lido no catalogo/curva do diodo:
    enr_db = 15


    # dados medidos no laboratorio (dBm) e coletados pelos alunos
    nh = -145.802 #dBW
    nc = -156.794 #dBW
    Te_medido = 420.571
    t_c = 303.40  # temperatura ambiente, medida com o termometro
    fo = 915e6 # frequencia de operacao (Hz)

    # Temperaturas (K):
    
    t0 = T0_PADRAO    # referencia
    Y_medido_dB = 10.486 # dB, fator Y medido (dB)
    Figura_ruido_medido_dB = 3.923 # dB, figura de ruido medida (dB)
   

    # --- Fator Y: escolha UMA das formas abaixo ---

    
    Y_line = y_de_potencias(nh, nc)     # fator Y medido (dB)
    T_H_calculado = (Y_line - 1) * Te_medido + Y_line * t_c
    ENR_calculado, ENR_calculado_dB = enr_de_hot(T_H_calculado, t0=t0)
    F = linear_para_db(1 + Te_medido / t0)

    print(f"Temperatura hot calculada: {T_H_calculado:.2f} K")
    print(f"Fator Y medido: {Y_medido_dB:.4f} dB")
    print(f"Fator Y calculaddo a partir das potencias: {Y_line:.4f} linear, {linear_para_db(Y_line):.3f} dB")
    print(f"ENR calculado a partir de T_H: {ENR_calculado:.4f} linear, {ENR_calculado_dB:.3f} dB")
    print(f"Fator de ruido calculado: {F:.3f} dB")

    # --- Comparacao medido x calculado (DataFrame) ---
    comparacao = tabela_comparacao([
        ("Y (dB)",   Y_medido_dB,             linear_para_db(Y_line)),
        ("ENR (dB)", enr_db,                  ENR_calculado_dB),
        ("NF (dB)",  Figura_ruido_medido_dB,  F),
        ("T_H (K)",  None,                    T_H_calculado),
    ])
    print("\nComparacao medido x calculado:")
    print(comparacao)
