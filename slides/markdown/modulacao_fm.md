---
marp: true
theme: gaia
color: #000
paginate: true
footer: 'Lab.Princípios de Comunicação para Engenharia '
header: '![h:60px](../../Figs/UNBS-300x150.png)'
---

<style>
    section {
          width: 1280px;
          font-size: 30px;
          padding: 40px;
          background-color: #ffffff;
    }
    section::after {
        content: 'Page ' attr(data-marpit-pagination) ' / ' attr(data-marpit-pagination-total);
        color: #000080
    }

    h1 {
       font-size: 60px ;
       color: #306030
    }

    h2 {
       font-size: 40px ;
       color: #306030
    }

    header {
        left: 29cm;
        height: 2cm;
    }

    header {
        top: 5px;
        color: #000080
    }

    footer {
     bottom: 10px;
    }

    </style>
<!-- _class: lead -->


# Modulação FM
Prof. Daniel Costa Araújo

---
<!-- _class: lead -->
# Modelo de Sinal

---
## O que é frequência ?

Em uma definição geral, a frequência é taxa de variação com que a fase do sinal varia ao longo do tempo

$$
f_i(t) = f_c + \frac{1}{2\pi}\frac{d}{dt} \phi (t)
$$

--- 

## Conceito 

Considere o sinal de banda-passante

$$
u(t) = A_c \cos (2\pi f_c t + \phi (t))
$$

Há duas maneiras de alteramos a fase do sinal 

1. Modulação PM  $\rightarrow$ $\phi(t) = k_p m(t)$ 
---
2. Modulação FM 
    $$
    \begin{align*}
    f_i(t) - f_c & = k_f m(t) \\
    f_i(t) - f_c & = \frac{1}{2\pi}\frac{d}{dt} \phi (t) \\
    \frac{d}{dt} \phi (t) & = 2\pi k_f m(t) \\ 
    \phi (t) & = 2\pi k_f \int_{-\infty}^{t} m(\tau) d\tau \\ 
    \end{align*}
    $$

---

## Representação em fase e frequência

1. Fase do sinal de banda-passante
   $$
   \phi (t) = \begin{cases}
    k_p m(t), & PM \\
    2\pi k_f \int_{-\infty}^{t} m(\tau) d\tau , & FM \\ 
   \end{cases}
   $$

2. Frequência do sinal de banda passante
   $$
   \frac{1}{2\pi}\frac{d}{dt} \phi (t) = \begin{cases}
    k_p\frac{1}{2\pi} \frac{d}{dt} m(t), & PM \\
    k_f  m(t)  , & FM \\ 
   \end{cases}
   $$

---

## Desvio de fase e frequência

1.  Modulação PM
    1. Desvio máximo de fase $\Delta \phi _{max} = k_p \max {|m(t)|}$
2.  Modulção FM
    1. Desvio máximo de frequência  $\Delta f _{max} = k_p \max {|m(t)|}$


---

## Equivalências

* Modulador FM = Integrador + Modulador PM
* Modulador PM = Derivador + Modulador FM

---

## Índice de Modulação

Considere a mensagem $m(t)$

$$
m(t) = a \cos (2\pi f_m t)
$$

Utilize-a para obter a expressão do sinal modulado em frequência e 

$$
\begin{align*}
\phi (t) &= k_p a \cos (2\pi f_m t), \,\ \text{Sinal PM} \\
\phi (t) &= 2\pi k_f \int_{-\infty}^{t} m(\tau)  d\tau =  \frac{a k_f }{f_m}\sin (2\pi f_m t), \,\ \text{Sinal FM} \\
\end{align*}
$$

---


* O índice de modulação para o sinal FM é 
    $$
    \beta _p = k_p a
    $$


* O índice de modulação para o sinal PM é 
    $$
    \begin{align*}
    \beta _f &=  \frac{a k_f }{f_m}  \\
            &=  \frac{\Delta f_{max} }{f_m}  \\  
    \end{align*}
    $$

---
## Modulação de banda-estreita

$$
\begin{align*}
    u(t) & = A_c \cos(2\pi f_c t) \cos \phi(t) -  A_c \sin(2\pi f_c t) \sin \phi(t)  \\
         & \approx A_c \cos(2\pi f_c t) - A_c \phi(t) \sin 2\pi f_c t
\end{align*}
$$

![bg auto w:70%](Fig/vetor_am.png)
![bg auto w:70%](Fig/vetor_fm.png)

---
## Exemplo

Considere o sinal $m(t)$ usado para modular em frequência. Encontre a relação entre $k_p$ e $k_f$, tal que o máximo desvio de fase de ambos o sinais sejam iguais. Se $k_p = k_f = 1$qual a máxima frequência instantânea em cada caso?


---
<!-- _class: lead -->
# Caracterização Espectral

---
## Modulação em fase (frequência) com sinal senoidais

Considere um sinal modulado em fase:

$$
\begin{align*}
u(t) & = A_c \cos(2\pi f_ct + \beta 2\pi f_m t)    
\end{align*}
$$