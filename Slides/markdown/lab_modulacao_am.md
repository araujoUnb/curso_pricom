---
marp: true
theme: gaia
color: #000
paginate: true
footer: 'Lab.Princípios de Comunicação para Engenharia '
header: '![h:60px](../Figs/UNBS-300x150.png)'
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


# Prática 1: Modulação AM
Prof. Daniel Costa Araújo

---

## Objetivo

* **Geral** : Implementar modulador e demodulador AM
* **Específico**:
  * Implmentar transmissor DSB-SC e DSB-FC
  * Analisar o comportamento do sinal no tempo na saída do modulador
  * Comparar o sinal mensagem transmitido com o sinal mensagem após demodulação


## Roteiro: Modulador 

1. Escolha o bloco gerador de sinal para definir sua mensagem
   1. Configurar um sinal mensagem para 5 KHz
2. Escolha o bloco gerador de sinal para definir o oscilador local
   1. Frequência de portadora
   2. 
