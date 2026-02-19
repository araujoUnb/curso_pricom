# Template de Slides LaTeX - UnB/LabTelecom

Template padrão para apresentações em LaTeX (Beamer) com a identidade visual da Universidade de Brasília e do Laboratório de Telecomunicações.

## Estrutura do Projeto

```
template_slides_latex/
├── main.tex                    # Arquivo principal (template)
├── template/
│   └── beamertheme-unb.sty     # Tema personalizado UnB
├── figures_global/
│   ├── unb.png                 # Logo da UnB
│   └── labtelecom.png          # Logo do LabTelecom
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md
```

---

## Instalação

### Método 1: Usar como Template do GitHub (Mais Fácil)

1. No GitHub, clique no botão **"Use this template"** → **"Create a new repository"**
2. Escolha um nome para seu novo repositório (ex: `slides-minha-apresentacao`)
3. Clone o novo repositório:

```bash
git clone https://github.com/seu-usuario/slides-minha-apresentacao.git
cd slides-minha-apresentacao
```

> ✅ **Vantagem**: Cria um repositório independente, sem histórico do template original.

---

### Método 2: Fork do Repositório

1. No GitHub, clique em **"Fork"** no canto superior direito
2. Clone o seu fork:

```bash
git clone https://github.com/seu-usuario/template_slides_latex.git
cd template_slides_latex
```

> ✅ **Vantagem**: Permite contribuir de volta ao template original via Pull Requests.

---

### Método 3: Clone Direto

Para uma cópia simples e rápida:

```bash
git clone https://github.com/SEU-USUARIO/template_slides_latex.git minha_apresentacao
cd minha_apresentacao

# Opcional: remover histórico do git e começar do zero
rm -rf .git
git init
git add .
git commit -m "Início da apresentação"
```

> ✅ **Vantagem**: Simples e direto.

---

### Método 4: Download ZIP (Sem Git)

1. No GitHub, clique em **"Code"** → **"Download ZIP"**
2. Extraia o arquivo no local desejado
3. Edite os arquivos normalmente

> ✅ **Vantagem**: Não requer Git instalado.

---

### Método 5: Submodule (Para Projetos Maiores)

Ideal quando você tem um repositório de projeto e quer incluir os slides:

```bash
# No seu repositório principal
cd seu_projeto

# Adicionar o template como submodule na pasta 'slides'
git submodule add https://github.com/SEU-USUARIO/template_slides_latex.git slides

# Commitar
git commit -m "Adiciona template de slides como submodule"
```

Para clonar um repositório que já tem o submodule:

```bash
# Opção A: Clonar com submodules
git clone --recurse-submodules https://github.com/seu-usuario/seu_projeto.git

# Opção B: Se já clonou sem --recurse-submodules
git submodule init
git submodule update
```

Para atualizar o template para a versão mais recente:

```bash
cd slides
git pull origin main
cd ..
git add slides
git commit -m "Atualiza template de slides"
```

Estrutura resultante:

```
seu_projeto/
├── codigo/
├── dados/
├── slides/                     # <-- Submodule do template
│   ├── main.tex
│   ├── template/
│   └── figures_global/
└── README.md
```

> ✅ **Vantagem**: Mantém o template atualizado e separado do projeto principal.

---

## Requisitos

Antes de usar, certifique-se de ter instalado:

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install texlive-full latexmk
```

### Linux (Fedora)

```bash
sudo dnf install texlive-scheme-full latexmk
```

### macOS

```bash
# Via Homebrew
brew install --cask mactex

# Ou baixe o instalador em: https://www.tug.org/mactex/
```

### Windows

1. Baixe e instale o [MiKTeX](https://miktex.org/download)
2. Ou instale o [TeX Live](https://www.tug.org/texlive/windows.html)

### Overleaf (Online)

1. Faça upload de todos os arquivos para um novo projeto no [Overleaf](https://www.overleaf.com/)
2. Compile diretamente no navegador

---

## Como Funciona

### Sistema de Variáveis

O template usa um sistema de variáveis para facilitar a personalização. Todas as variáveis ficam no início do arquivo `main.tex`:

```latex
% --- Informações do Autor ---
\newcommand{\autorNome}{Prof. Daniel Costa Araújo}
\newcommand{\autorEmail}{daniel.araujo@unb.br}

% --- Título e Subtítulo ---
\newcommand{\tituloApresentacao}{Título da Apresentação}
\newcommand{\subtituloApresentacao}{Subtítulo ou Tema}

% --- Idioma: 'pt' para Português ou 'en' para Inglês ---
\newcommand{\idioma}{pt}
```

### Suporte a Múltiplos Idiomas

O template suporta **Português** e **Inglês**. Para trocar o idioma, altere a variável `\idioma`:

```latex
% Para português:
\newcommand{\idioma}{pt}

% Para inglês:
\newcommand{\idioma}{en}
```

O idioma afeta automaticamente:
- Nome da universidade no **header**
- Texto do slide de **Agradecimentos/Acknowledgments**
- Nome do **instituto** no slide de título

### Variáveis de Instituição

Você pode personalizar os nomes em ambos os idiomas:

```latex
% --- Instituição (Português) ---
\newcommand{\universidadePT}{Universidade de Brasília}
\newcommand{\departamentoPT}{Faculdade de Ciências e Tecnologia em Engenharias}
\newcommand{\laboratorioPT}{Laboratório de Telecomunicações}

% --- Instituição (Inglês) ---
\newcommand{\universidadeEN}{University of Brasília}
\newcommand{\departamentoEN}{Faculty of Sciences and Technology in Engineering}
\newcommand{\laboratorioEN}{Telecommunications Laboratory}
```

---

## Compilação

### Compilar o PDF

```bash
pdflatex main.tex
```

### Se usar referências bibliográficas

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Usando latexmk (recomendado)

```bash
latexmk -pdf main.tex
```

---

## Exemplos de Slides

### Slide com Blocos

```latex
\begin{frame}{Título do Slide}
\begin{block}{Título do Bloco}
    Conteúdo do bloco.
\end{block}
\end{frame}
```

### Slide com Duas Colunas

```latex
\begin{frame}{Duas Colunas}
\begin{columns}[t]
    \column{0.5\textwidth}
    Conteúdo da esquerda
    
    \column{0.5\textwidth}
    Conteúdo da direita
\end{columns}
\end{frame}
```

### Slide com Revelação Progressiva

```latex
\begin{frame}{Animação}
\begin{itemize}
    \item<1-> Aparece primeiro
    \item<2-> Aparece segundo
    \item<3-> Aparece terceiro
\end{itemize}
\end{frame}
```

### Slide com Figura

```latex
\begin{frame}{Figura}
\begin{figure}
    \centering
    \includegraphics[width=0.6\linewidth]{figures/sua_figura.png}
    \caption{Legenda da figura.}
\end{figure}
\end{frame}
```

### Slide com Equação

```latex
\begin{frame}{Equação}
\begin{equation}
    \mathbf{y} = \mathbf{H}\mathbf{x} + \mathbf{n}
\end{equation}
\end{frame}
```

---

## Cores do Tema

O tema utiliza as cores oficiais da UnB:

| Cor | RGB | Hex | Uso |
|-----|-----|-----|-----|
| Primária (azul) | (0, 59, 92) | #003B5C | Títulos, estrutura |
| Secundária (verde) | (0, 102, 51) | #006633 | Subtítulos |
| Destaque (dourado) | (242, 169, 0) | #F2A900 | Acentos |

---

## Personalização do Tema

Para personalizar o tema, edite o arquivo `template/beamertheme-unb.sty`:

- **Cores**: Modifique os valores em `\definecolor`
- **Header**: Ajuste o template `headline`
- **Footer**: Ajuste o template `footline`
- **Logos**: Substitua as imagens em `figures_global/`

---

## Licença

Uso livre para membros da UnB e LabTelecom.
