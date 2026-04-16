"""
Validação numérica do PLL analógico — referência teórica do gabarito.

Parâmetros de projeto:
  fc = 2 kHz (portadora)
  Kv = 500 Hz/V         => Kvco = 2*pi*500 rad/s/V
  Kd = 0.5 V/rad        (multiplicador com sinais de amplitude unitária)
  fn = 50 Hz            => omega_n = 2*pi*50 rad/s
  zeta = 0.707
  Filtro de malha ativo PI: F(s) = Kp + Ki/s

Testes:
  A) Rampa de fase : entrada cos(2*pi*fc*t + 2*pi*df*t) com df = 50 Hz
  B) Fase quadrática: cos(2*pi*fc*t + pi*alpha*t**2) com alpha = 1000 Hz/s
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Parâmetros ---
fc    = 2_000.0
Kv    = 500.0
Kvco  = 2*np.pi*Kv
Kd    = 0.5
fn    = 50.0
wn    = 2*np.pi*fn
zeta  = 0.707
Ki    = wn**2 / (Kvco*Kd)
Kp    = 2*zeta*wn / (Kvco*Kd)

print(f"Kp = {Kp:.4f}, Ki = {Ki:.4f} 1/s")
print(f"K (1a ordem equivalente) = Kvco*Kd = {Kvco*Kd:.2f} 1/s")

# --- Discretização ---
fs = 200_000.0          # 100 amostras por ciclo de portadora
T  = 0.30
t  = np.arange(0, T, 1/fs)
dt = 1/fs

def simulate(phi_in, order=2):
    """PLL passa-banda com PD multiplicador, LPF e filtro de malha PI/proporcional."""
    rx = np.cos(2*np.pi*fc*t + phi_in)
    vco = np.zeros_like(t)
    pd_lpf = 0.0
    integ = 0.0
    phase_vco = 0.0
    ctrl = 0.0
    # LPF de 1a ordem para remover componente em 2*fc
    f_lpf = 5*fn          # bem acima da BW de malha, abaixo de 2*fc
    alpha_lpf = dt*2*np.pi*f_lpf / (1 + dt*2*np.pi*f_lpf)
    err = np.zeros_like(t)
    ctrl_log = np.zeros_like(t)
    for k in range(len(t)):
        vco_k = -2*np.sin(2*np.pi*fc*t[k] + phase_vco)   # quadratura
        pd = rx[k] * vco_k
        pd_lpf = pd_lpf + alpha_lpf*(pd - pd_lpf)
        if order == 2:
            integ += Ki*pd_lpf*dt
            ctrl = Kp*pd_lpf + integ
        else:  # 1a ordem: F(s)=1, apenas ganho proporcional
            ctrl = Kp*pd_lpf
        phase_vco += Kvco*ctrl*dt
        err[k] = pd_lpf
        ctrl_log[k] = ctrl
    # Erro de fase verdadeiro (referência - estimativa)
    theta_e = phi_in - 2*np.pi*np.cumsum(np.full_like(t, 0))  # placeholder
    # reconstrói a fase do VCO integrando ctrl
    phase_vco_t = np.cumsum(Kvco*ctrl_log)*dt
    theta_e = phi_in - phase_vco_t
    return ctrl_log, theta_e

# --- Teste A: rampa de fase (frequency step) ---
df = 50.0
phi_A = 2*np.pi*df*t
ctrl_A2, te_A2 = simulate(phi_A, order=2)
ctrl_A1, te_A1 = simulate(phi_A, order=1)

# --- Teste B: fase quadrática (frequency ramp) ---
alpha = 1000.0
phi_B = np.pi*alpha*t**2
ctrl_B2, te_B2 = simulate(phi_B, order=2)

# --- Erros teóricos em regime ---
err_A1_teor = 2*np.pi*df / (Kvco*Kd*Kp)   # ~ Δω/K para 1a ordem
err_B2_teor = 2*np.pi*alpha / wn**2
print(f"\nA) Rampa Δf={df} Hz")
print(f"   1a ordem: erro simulado (final) = {te_A1[-1]:.4f} rad  | teor ≈ {err_A1_teor:.4f}")
print(f"   2a ordem: erro simulado (final) = {te_A2[-1]:.4f} rad  (esperado 0)")
print(f"\nB) Quadrática α={alpha} Hz/s")
print(f"   2a ordem: erro simulado (final) = {te_B2[-1]:.4f} rad  | teor ≈ {err_B2_teor:.4f}")
print(f"   2a ordem: erro em graus = {np.degrees(te_B2[-1]):.2f}°")

# --- Figuras ---
fig, ax = plt.subplots(2, 2, figsize=(11, 7))

ax[0,0].plot(t*1e3, te_A1, label='1ª ordem')
ax[0,0].plot(t*1e3, te_A2, label='2ª ordem')
ax[0,0].axhline(err_A1_teor, color='k', ls='--', lw=0.8, label='teoria 1ª')
ax[0,0].set_title(f'A) Rampa de fase  Δf={df} Hz — erro de fase')
ax[0,0].set_xlabel('t (ms)'); ax[0,0].set_ylabel(r'$\theta_e$ (rad)')
ax[0,0].grid(True); ax[0,0].legend()

ax[0,1].plot(t*1e3, ctrl_A1, label='1ª ordem')
ax[0,1].plot(t*1e3, ctrl_A2, label='2ª ordem')
ax[0,1].axhline(df/Kv, color='k', ls='--', lw=0.8, label=f'Δf/Kv = {df/Kv:.2f} V')
ax[0,1].set_title('A) Tensão de controle do VCO')
ax[0,1].set_xlabel('t (ms)'); ax[0,1].set_ylabel('v_ctrl (V)')
ax[0,1].grid(True); ax[0,1].legend()

ax[1,0].plot(t*1e3, te_B2, label='2ª ordem')
ax[1,0].axhline(err_B2_teor, color='k', ls='--', lw=0.8, label='teoria 2ª')
ax[1,0].set_title(f'B) Fase quadrática α={alpha} Hz/s — erro de fase')
ax[1,0].set_xlabel('t (ms)'); ax[1,0].set_ylabel(r'$\theta_e$ (rad)')
ax[1,0].grid(True); ax[1,0].legend()

# ctrl deve crescer linearmente em B (rampa em freq)
ax[1,1].plot(t*1e3, ctrl_B2)
ax[1,1].plot(t*1e3, alpha*t/Kv, 'k--', lw=0.8, label=r'$\alpha t / Kv$')
ax[1,1].set_title('B) Tensão de controle (deve ser rampa)')
ax[1,1].set_xlabel('t (ms)'); ax[1,1].set_ylabel('v_ctrl (V)')
ax[1,1].grid(True); ax[1,1].legend()

plt.tight_layout()
plt.savefig('../figuras/python_referencia.png', dpi=120)
print("\nFigura salva em figuras/python_referencia.png")
