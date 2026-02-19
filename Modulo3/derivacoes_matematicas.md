
# Módulo 3: Conversão Analógico-Digital

**Professor:** GitHub Copilot
**Data:** 19 de fevereiro de 2026
**Bibliografia Principal:**
1. Proakis, J. G., & Salehi, M. (2008). *Communication Systems Engineering*. Pearson. (Capítulo 7)
2. Lathi, B. P., & Ding, Z. (2009). *Modern Digital and Analog Communication Systems*. Oxford University Press. (Capítulo 5)

---

## Introdução

Olá, turma!

Neste módulo, vamos mergulhar em um dos conceitos mais fundamentais das comunicações modernas: a conversão de sinais analógicos para o formato digital (ADC - Analog-to-Digital Conversion). Todo sistema de comunicação digital, seja seu smartphone, um satélite ou a rede de internet, depende desse processo para representar informações do mundo real (que são inerentemente analógicas, como a nossa voz) em um formato que os computadores possam processar e transmitir.

O processo de ADC pode ser dividido em três etapas principais:

1.  **Amostragem (Sampling):** Converte um sinal contínuo no tempo em um sinal discreto no tempo.
2.  **Quantização (Quantization):** Converte um sinal de amplitude contínua em um sinal de amplitude discreta.
3.  **Codificação (Encoding):** Atribui uma palavra de código binária a cada nível de quantização.

Vamos explorar a matemática e a intuição por trás de cada uma dessas etapas.

---

## 1. Amostragem (Sampling)

A amostragem é a ponte entre o mundo analógico e o digital. A grande questão que a teoria da amostragem responde é: "Com que frequência precisamos 'olhar' para um sinal analógico para capturar toda a sua informação?" A resposta é dada pelo famoso **Teorema da Amostragem de Nyquist-Shannon**.

### 1.1. O Teorema da Amostragem

**Conceito:** Um sinal passa-baixas (band-limited) $g(t)$, cujo espectro de frequências $G(f)$ é zero para todas as frequências $|f| \ge W$, pode ser completamente reconstruído a partir de suas amostras se a taxa de amostragem, $f_s$, for maior que o dobro da sua maior frequência, $W$.

$$
f_s > 2W
$$

Essa taxa mínima, $2W$, é conhecida como a **taxa de Nyquist**.

### 1.2. Derivação Matemática do Teorema da Amostragem (Passo a Passo)

Vamos entender por que isso funciona, quebrando a matemática em etapas.

**Passo 1: Modelando o Sinal Amostrado no Tempo**

O processo de amostragem ideal pode ser modelado como a multiplicação do sinal analógico contínuo $g(t)$ por um "pente de impulsos" (ou trem de impulsos) $\delta_{T_s}(t)$. Este pente é uma sequência infinita de funções delta de Dirac espaçadas pelo período de amostragem $T_s$.

$$
\delta_{T_s}(t) = \sum_{n=-\infty}^{\infty} \delta(t - nT_s)
$$

O sinal amostrado, $g_s(t)$, é o produto desses dois:

$$
g_s(t) = g(t) \cdot \delta_{T_s}(t) = g(t) \cdot \sum_{n=-\infty}^{\infty} \delta(t - nT_s)
$$

Agora, usamos uma propriedade fundamental da função delta, a propriedade de "filtragem" ou "amostragem": $x(t) \cdot \delta(t - t_0) = x(t_0) \cdot \delta(t - t_0)$. Isso significa que o produto de uma função por um impulso deslocado é um impulso no mesmo local, mas com sua "área" (ou peso) escalada pelo valor da função naquele ponto. Aplicando isso a cada termo do somatório:

$$
g_s(t) = \sum_{n=-\infty}^{\infty} g(t) \cdot \delta(t - nT_s) = \sum_{n=-\infty}^{\infty} g(nT_s) \delta(t - nT_s)
$$

Esta equação nos diz que o sinal amostrado não é mais uma função contínua, mas uma série de impulsos ponderados. O peso de cada impulso é exatamente o valor do sinal original no instante da amostragem.

**Passo 2: Indo para o Domínio da Frequência**

Para ver o que acontece com o espectro, aplicamos a Transformada de Fourier. A propriedade da convolução nos diz que a multiplicação no domínio do tempo corresponde à convolução no domínio da frequência.

$$
G_s(f) = \mathcal{F}\{g_s(t)\} = \mathcal{F}\{g(t) \cdot \delta_{T_s}(t)\} = G(f) * \mathcal{F}\{\delta_{T_s}(t)\}
$$

Onde $G(f)$ é a transformada de $g(t)$ e $*$ denota a convolução.

**Passo 3: A Transformada de Fourier do Trem de Impulsos**

Um resultado padrão da análise de Fourier (derivado da teoria das Séries de Fourier) é que a transformada de um trem de impulsos no tempo é outro trem de impulsos na frequência. A separação entre os impulsos no tempo ($T_s$) se inverte para se tornar a separação na frequência ($f_s = 1/T_s$).

$$
\mathcal{F}\{\delta_{T_s}(t)\} = \mathcal{F}\left\{ \sum_{n=-\infty}^{\infty} \delta(t - nT_s) \right\} = f_s \sum_{n=-\infty}^{\infty} \delta(f - n f_s)
$$

**Passo 4: A Convolução Final**

Agora, substituímos o resultado do Passo 3 na equação do Passo 2:

$$
G_s(f) = G(f) * \left( f_s \sum_{n=-\infty}^{\infty} \delta(f - n f_s) \right)
$$

Usando a propriedade distributiva da convolução, podemos levar a convolução para dentro do somatório:

$$
G_s(f) = f_s \sum_{n=-\infty}^{\infty} G(f) * \delta(f - n f_s)
$$

Finalmente, usamos outra propriedade fundamental da convolução: a convolução de qualquer função $X(f)$ com um impulso deslocado $\delta(f - f_0)$ simplesmente desloca a função original para a posição do impulso, ou seja, $X(f) * \delta(f - f_0) = X(f - f_0)$. Aplicando isso:

$$
G_s(f) = f_s \sum_{n=-\infty}^{\infty} G(f - n f_s)
$$

**Conclusão da Derivação:** Esta equação é o resultado central. Ela mostra que o espectro do sinal amostrado, $G_s(f)$, é composto por infinitas cópias do espectro do sinal original, $G(f)$, cada uma escalada por $f_s$ e centrada em um múltiplo da frequência de amostragem ($0, \pm f_s, \pm 2f_s, \dots$).

**Visualizando o Espectro:**

*   O espectro original, $G(f)$, é limitado a $[-W, W]$.
*   O espectro do sinal amostrado, $G_s(f)$, consiste em cópias de $G(f)$ repetidas a cada $f_s$. Cada cópia tem largura $2W$.

**A Condição de Nyquist:**

Para que possamos reconstruir o sinal original, as réplicas do espectro não podem se sobrepor. A réplica centrada em $f=0$ termina em $W$. A próxima réplica, centrada em $f=f_s$, começa em $f_s - W$. Para evitar a sobreposição (aliasing), precisamos que:

$$
f_s - W > W \implies f_s > 2W
$$

Se essa condição for satisfeita, podemos recuperar o espectro original $G(f)$ simplesmente passando o sinal amostrado $g_s(t)$ por um **filtro passa-baixas ideal** com frequência de corte $W$.

### 1.3. Aliasing

O que acontece se $f_s < 2W$? As réplicas do espectro se sobrepõem. A parte do espectro de uma réplica que invade a banda da outra é chamada de **aliasing**. Isso causa uma distorção irrecuperável, pois as componentes de alta frequência do sinal original "se disfarçam" de componentes de baixa frequência após a amostragem. É por isso que, na prática, sempre usamos um **filtro anti-aliasing** (um filtro passa-baixas) antes do amostrador para garantir que o sinal seja estritamente limitado em banda.

---

## 2. Quantização

Após a amostragem, temos um sinal discreto no tempo, mas a amplitude de cada amostra ainda pode ter qualquer valor dentro de um intervalo contínuo. A quantização resolve isso, mapeando um grande conjunto de valores de amplitude para um conjunto menor e finito de níveis de quantização.

### 2.1. Quantização Uniforme

A forma mais simples de quantização é a uniforme, onde o intervalo de amplitudes do sinal é dividido em $L$ níveis, cada um com o mesmo tamanho de passo, $\Delta$.

Se o sinal $g(nT_s)$ tem uma faixa de amplitude de $V_{min}$ a $V_{max}$, a faixa total é $V_{pp} = V_{max} - V_{min}$. O tamanho do passo de quantização é:

$$
\Delta = \frac{V_{pp}}{L}
$$

Cada amostra $g(nT_s)$ é então mapeada para o nível de quantização mais próximo. Seja $\hat{g}(nT_s)$ a amostra quantizada.

### 2.2. Erro de Quantização e Ruído

A quantização é um processo com perdas. A diferença entre a amostra original e a amostra quantizada é o **erro de quantização**, $e_q$.

$$
e_q = \hat{g}(nT_s) - g(nT_s)
$$

Para um quantizador uniforme, o erro para qualquer amostra está no intervalo:

$$
-\frac{\Delta}{2} \le e_q \le \frac{\Delta}{2}
$$

**Modelando o Erro como Ruído:**

Se o número de níveis de quantização $L$ é grande e o sinal varia rapidamente entre eles, podemos modelar o erro de quantização como um **ruído branco uniforme**. Ou seja, tratamos $e_q$ como uma variável aleatória com uma densidade de probabilidade (PDF) uniforme no intervalo $[-\Delta/2, \Delta/2]$.

$$
p(e_q) = \begin{cases} \frac{1}{\Delta} & \text{se } -\frac{\Delta}{2} \le e_q \le \frac{\Delta}{2} \\ 0 & \text{caso contrário} \end{cases}
$$

### 2.3. Potência do Ruído de Quantização (Passo a Passo)

A potência média do ruído de quantização, $P_q$, é o valor esperado (a média) do quadrado do erro, $E[e_q^2]$. Para uma variável aleatória contínua, isso é calculado integrando $e_q^2$ ponderado pela sua função de densidade de probabilidade (PDF), $p(e_q)$.

**Passo 1: Definir a Integral da Potência**

A definição formal da potência média (ou variância, já que a média do erro é zero) é:

$$
P_q = E[e_q^2] = \int_{-\infty}^{\infty} e_q^2 p(e_q) de_q
$$

**Passo 2: Substituir a PDF do Erro de Quantização**

Como modelamos o erro como uma variável aleatória com distribuição uniforme no intervalo $[-\Delta/2, \Delta/2]$, sua PDF é $p(e_q) = 1/\Delta$ dentro desse intervalo e zero fora dele. Portanto, podemos mudar os limites da integral para corresponder a este intervalo e substituir o valor da PDF.

$$
P_q = \int_{-\Delta/2}^{\Delta/2} e_q^2 \left( \frac{1}{\Delta} \right) de_q
$$

**Passo 3: Resolver a Integral**

Agora, resolvemos a integral. A constante $1/\Delta$ pode ser movida para fora.

$$
P_q = \frac{1}{\Delta} \int_{-\Delta/2}^{\Delta/2} e_q^2 de_q
$$

A integral de $x^2$ é $x^3/3$. Aplicando isso:

$$
P_q = \frac{1}{\Delta} \left[ \frac{e_q^3}{3} \right]_{-\Delta/2}^{\Delta/2}
$$

Agora, avaliamos a expressão nos limites de integração (o limite superior menos o limite inferior).

$$
P_q = \frac{1}{\Delta} \left( \frac{(\Delta/2)^3}{3} - \frac{(-\Delta/2)^3}{3} \right)
$$

**Passo 4: Simplificar a Expressão**

Vamos simplificar os termos dentro dos parênteses.

$$
(\Delta/2)^3 = \frac{\Delta^3}{8}
$$
$$
(-\Delta/2)^3 = -\frac{\Delta^3}{8}
$$

Substituindo de volta:

$$
P_q = \frac{1}{\Delta} \left( \frac{\Delta^3/8}{3} - \left( -\frac{\Delta^3/8}{3} \right) \right) = \frac{1}{\Delta} \left( \frac{\Delta^3}{24} + \frac{\Delta^3}{24} \right)
$$

Somando as frações:

$$
P_q = \frac{1}{\Delta} \left( \frac{2\Delta^3}{24} \right) = \frac{1}{\Delta} \left( \frac{\Delta^3}{12} \right)
$$

Finalmente, cancelando um $\Delta$:

$$
P_q = \frac{\Delta^2}{12}
$$

**Conclusão da Derivação:** Chegamos à fórmula fundamental para a potência do ruído de quantização. Ela mostra que o ruído não depende do sinal em si, mas apenas do quadrado do tamanho do passo de quantização. Para diminuir o ruído, precisamos de um $\Delta$ menor.

Esta é uma fórmula fundamental. Ela nos diz que a potência do ruído de quantização é diretamente proporcional ao quadrado do tamanho do passo. Para reduzir o ruído, precisamos de passos menores, ou seja, mais níveis de quantização.

---

## 3. Codificação e Relação Sinal-Ruído (SNR)

A última etapa é a codificação. Se temos $L$ níveis de quantização, precisamos de $n$ bits para representar cada nível, onde $L \le 2^n$. Geralmente, escolhemos $L = 2^n$.

$$
L = 2^n \implies n = \log_2(L)
$$

### 3.1. Relação Sinal-Ruído de Quantização (SQNR) (Passo a Passo)

A qualidade de um sistema de quantização é medida pela **Relação Sinal-Ruído de Quantização (SQNR)**. É a razão entre a potência do sinal, $P_s$, e a potência do ruído de quantização, $P_q$.

**Passo 1: Definição Base do SQNR**

A definição é simples:

$$
\text{SQNR} = \frac{\text{Potência do Sinal}}{\text{Potência do Ruído}} = \frac{P_s}{P_q}
$$

Usando o resultado que acabamos de derivar para a potência do ruído ($P_q = \Delta^2/12$):

$$
\text{SQNR} = \frac{P_s}{\Delta^2 / 12} = \frac{12 P_s}{\Delta^2}
$$

**Passo 2: Expressar o SQNR em Termos do Número de Bits (n)**

Esta forma não é muito prática. Queremos relacionar o SQNR com o número de bits, $n$, que usamos na codificação, pois isso é um parâmetro de projeto.

Primeiro, relacionamos o tamanho do passo $\Delta$ com o número de bits. Se um sinal tem uma faixa de pico a pico $V_{pp}$ e usamos $L$ níveis de quantização:

$$
\Delta = \frac{V_{pp}}{L}
$$

Se estamos usando $n$ bits, podemos ter $L = 2^n$ níveis.

$$
\Delta = \frac{V_{pp}}{2^n}
$$

Agora, substituímos essa expressão de $\Delta$ na equação do SQNR:

$$
\text{SQNR} = \frac{12 P_s}{(V_{pp}/2^n)^2} = \frac{12 P_s \cdot (2^n)^2}{V_{pp}^2} = \frac{12 P_s}{V_{pp}^2} \cdot 2^{2n}
$$

**Passo 3: Analisar um Caso Específico (Sinal Senoidal)**

Para ter uma ideia mais concreta, vamos analisar o caso de um sinal de entrada senoidal que ocupa toda a faixa do quantizador. Seja o sinal $g(t) = A \cos(\omega t)$.

*   A amplitude máxima é $A$. A amplitude mínima é $-A$.
*   A faixa de pico a pico é $V_{pp} = A - (-A) = 2A$.
*   A potência média de um sinal senoidal $A \cos(\omega t)$ é $P_s = A^2/2$.

Vamos substituir $V_{pp} = 2A$ e $P_s = A^2/2$ na nossa fórmula geral do SQNR:

$$
\text{SQNR} = \frac{12 (A^2/2)}{(2A)^2} \cdot 2^{2n} = \frac{6 A^2}{4 A^2} \cdot 2^{2n}
$$

Cancelando o termo $A^2$:

$$
\text{SQNR} = \frac{6}{4} \cdot 2^{2n} = 1.5 \cdot 2^{2n}
$$

**Passo 4: Converter para Decibéis (dB)**

Engenheiros adoram decibéis! A conversão para dB é $X_{dB} = 10 \log_{10}(X)$.

$$
\text{SQNR (dB)} = 10 \log_{10}(1.5 \cdot 2^{2n})
$$

Usando a propriedade do logaritmo $\log(a \cdot b) = \log(a) + \log(b)$:

$$
\text{SQNR (dB)} = 10 \log_{10}(1.5) + 10 \log_{10}(2^{2n})
$$

Usando outra propriedade, $\log(a^b) = b \cdot \log(a)$:

$$
\text{SQNR (dB)} = 10 \log_{10}(1.5) + 2n \cdot 10 \log_{10}(2)
$$

Agora, calculamos os valores dos logaritmos:
*   $10 \log_{10}(1.5) \approx 1.76$ dB
*   $10 \log_{10}(2) \approx 3.01$ dB

Substituindo esses valores:

$$
\text{SQNR (dB)} \approx 1.76 + 2n \cdot (3.01) = 1.76 + 6.02n
$$

**Conclusão da Derivação:** Chegamos à famosa **"regra dos 6 dB"**. Para um sinal senoidal, o SQNR máximo que podemos obter é aproximadamente $1.76 + 6.02n$ dB. Isso nos dá uma regra prática poderosa: cada bit que adicionamos ao nosso quantizador aumenta a qualidade do sinal (o SQNR) em cerca de 6 dB.

### 3.2. Quantização Não-Uniforme (Companding)

Sinais como a voz humana têm uma característica interessante: pequenas amplitudes são muito mais prováveis de ocorrer do que grandes amplitudes. Em um quantizador uniforme, isso significa que a maioria das amostras usará apenas uma pequena fração dos níveis de quantização disponíveis, o que é ineficiente.

A solução é a **quantização não-uniforme**, onde usamos passos de quantização menores para amplitudes pequenas e passos maiores para amplitudes grandes. Isso melhora o SQNR para sinais de baixa potência.

Na prática, isso é implementado através de um processo chamado **companding**:

1.  **Compressão:** O sinal passa por um compressor não-linear que amplifica as partes de baixa amplitude.
2.  **Quantização Uniforme:** O sinal comprimido é então quantizado uniformemente.
3.  **Expansão:** No receptor, um expansor com a característica inversa do compressor é usado para restaurar as amplitudes originais do sinal.

As duas leis de compressão mais usadas são a **μ-law** (usada na América do Norte e Japão) e a **A-law** (usada na Europa e no resto do mundo).

---

Este resumo cobre os conceitos matemáticos essenciais da conversão analógico-digital. Ele servirá de base para a criação dos slides e para as nossas discussões em aula. Estudem este material com atenção!
