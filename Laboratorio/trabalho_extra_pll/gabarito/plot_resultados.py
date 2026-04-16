"""Lê os arquivos .dat gerados pelo ngspice e produz as figuras do gabarito."""
import numpy as np
import matplotlib.pyplot as plt
import os

DIR = os.path.dirname(__file__)
FIG = os.path.join(DIR, '..', 'figuras')
os.makedirs(FIG, exist_ok=True)


def load(fname):
    """wrdata gera colunas: t1 v1 t2 v2 t3 v3 ..."""
    a = np.loadtxt(os.path.join(DIR, fname))
    t = a[:, 0]
    return t, a[:, 1], a[:, 3], a[:, 5]   # pdf, ctrl, terr


t1, pdf1, ctrl1, terr1 = load('pll_1a_rampa.dat')
t2, pdf2, ctrl2, terr2 = load('pll_2a_rampa.dat')
t3, pdf3, ctrl3, terr3 = load('pll_2a_quadratica.dat')

# Parâmetros para linhas teóricas
fc, df, alpha = 2_000.0, 50.0, 1_000.0
Kv = 500.0
Kvco = 2*np.pi*Kv
Kd = 1.0
Kp = 0.283
wn = 2*np.pi*50.0

err_1a_teor = 2*np.pi*df / (Kvco*Kd*Kp)        # ~0.353 rad
err_2a_quad_teor = 2*np.pi*alpha / wn**2       # ~0.0637 rad
ctrl_step_teor = df / Kv                       # 0.1 V
ctrl_ramp_teor = lambda t: alpha*t / Kv         # rampa de tensão para acompanhar α

# ---- Fig 1: rampa de fase, 1a vs 2a ordem ----
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(t1*1e3, terr1, label='1ª ordem')
ax[0].plot(t2*1e3, terr2, label='2ª ordem')
ax[0].axhline(err_1a_teor, color='gray', ls='--', lw=1, label=f'teor 1ª ≈ {err_1a_teor:.3f} rad')
ax[0].axhline(0, color='k', lw=0.5)
ax[0].set_ylabel(r'Erro de fase $\theta_e$ (rad)')
ax[0].set_title(f'Teste A — Rampa de fase Δf = {df:.0f} Hz')
ax[0].grid(True); ax[0].legend(loc='right')

ax[1].plot(t1*1e3, ctrl1, label='1ª ordem')
ax[1].plot(t2*1e3, ctrl2, label='2ª ordem')
ax[1].axhline(ctrl_step_teor, color='gray', ls='--', lw=1, label=f'Δf/Kv = {ctrl_step_teor:.2f} V')
ax[1].set_xlabel('t (ms)'); ax[1].set_ylabel('v_ctrl (V)')
ax[1].grid(True); ax[1].legend(loc='right')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'teste_A_rampa.png'), dpi=130)
plt.close()

# ---- Fig 2: quadratica, 2a ordem ----
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(t3*1e3, terr3, label='2ª ordem')
ax[0].axhline(err_2a_quad_teor, color='gray', ls='--', lw=1,
              label=f'teor regime ≈ {err_2a_quad_teor:.3f} rad')
ax[0].axhline(0, color='k', lw=0.5)
ax[0].set_ylabel(r'Erro de fase $\theta_e$ (rad)')
ax[0].set_title(f'Teste B — Fase quadrática α = {alpha:.0f} Hz/s')
ax[0].grid(True); ax[0].legend(loc='right')

ax[1].plot(t3*1e3, ctrl3, label='v_ctrl simulada')
ax[1].plot(t3*1e3, ctrl_ramp_teor(t3), 'k--', lw=1, label=r'$\alpha\,t / K_v$ (esperado)')
ax[1].set_xlabel('t (ms)'); ax[1].set_ylabel('v_ctrl (V)')
ax[1].grid(True); ax[1].legend(loc='right')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'teste_B_quadratica.png'), dpi=130)
plt.close()

print("Resumo numérico:")
print(f"  1ª ordem rampa: terr_final = {terr1[-1]:.4f} rad   |  teorico = {err_1a_teor:.4f}")
print(f"  2ª ordem rampa: terr_final = {terr2[-1]:.4f} rad   |  teorico = 0")
print(f"  2ª ordem quad : terr_final = {terr3[-1]:.4f} rad   |  teorico regime = {err_2a_quad_teor:.4f}")
print("Figuras salvas em ../figuras/")
