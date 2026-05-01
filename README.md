# 🏺 Ajuste Dinâmico de Fluxo para Extrusão de Argila

Este é um script de pós-processamento em Python para o **PrusaSlicer**, desenvolvido para otimizar o controle de extrusão na impressão 3D de argila e cerâmica em sistemas baseados no firmware **Marlin**.

---

## 🎯 O Problema

Na impressão 3D de argila, utilizamos bicos com diâmetros maiores (ex: 3mm). Quando tentamos ajustar o fluxo de material alterando a "Largura da Linha" (*Line Width*) diretamente no fatiador para diferentes partes da peça, o software recalcula toda a trajetória (*toolpath*). Isso pode gerar deformações indesejadas, acúmulo de material ou arrastar a massa úmida nas mudanças de direção.

---

## 🚀 A Solução

A solução ideal é manter a trajetória original calculada pelo fatiador intacta e alterar dinamicamente apenas a **quantidade de material depositado** (*Flow Rate*).

Este script atua de forma invisível logo após o fatiamento. Ele lê o arquivo G-code gerado pelo PrusaSlicer e injeta comandos nativos do Marlin (`M221 S...`) baseados numa cascata de regras lógicas.

---

## ✨ Funcionalidades Principais

O script é um sistema de **Controle de Fluxo em 4 Estágios**, permitindo precisão no ajuste de fluxo em cada elemento na estrutura da peça:

- **Camadas de Base:** Fluxo otimizado para garantir a adesão inicial na mesa.
- **Intermediário 1 (Primeira Transição):** Ajuste para criar os pilares de suporte iniciais sem esmagar a base mole.
- **Intermediário 2 (Segunda Transição):** Ajuste para o corpo médio da peça.
- **Camadas Gerais (Topo/Restante):** Fluxo focado no acabamento e construção final.

Além disso, em cada um destes 4 estágios, você pode definir percentuais individuais para perímetros externos, preenchimentos, contornos, etc.

---

## 🛠️ Pré-requisitos

- [Python 3.x](https://www.python.org/) instalado e adicionado ao PATH do sistema operacional.
- PrusaSlicer.
- Impressora 3D com firmware Marlin.

---

## ⚙️ Instalação e Uso (Ambiente Windows)

### 1. Clone o repositório

```bash
git clone https://github.com/bknegami/extrusora-argila.git
```

### 2. Personalize as Variáveis de Controle

Abra o arquivo `ajuste_fluxo_argila.py` em um editor de texto e defina os limites absolutos de transição de cada fase, bem como os fluxos desejados.

> **Nota sobre a contagem:** Os limites utilizam valores de camada **absolutos**. Por exemplo, para 1 camada de base, 3 do intermediário 1 e 5 do intermediário 2, os limites devem ser **1**, **4** (1+3) e **9** (4+5).

```python
# Definindo os limites de transição
LIMITE_CAMADAS_BASE = 1
LIMITE_CAMADAS_INTERMEDIARIAS_1 = 4
LIMITE_CAMADAS_INTERMEDIARIAS_2 = 9

# Exemplo do Dicionário de Base
FLOW_SETTINGS_BASE = {
    ";TYPE:External perimeter": 70,
    ";TYPE:Perimeter": 75,
    ";TYPE:Internal infill": 80,
    ";TYPE:Solid infill": 75,
    ";TYPE:Top solid infill": 70,
    ";TYPE:Skirt/Brim": 85
}

# (Configure também os dicionários INTERMEDIARIO_1, INTERMEDIARIO_2 e GERAL no código)
```

### 3. Configure a Ponte de Execução (`.bat`)

O PrusaSlicer no Windows exige um arquivo intermediário para executar scripts Python de forma confiável. Certifique-se de que o arquivo `executar_fluxo.bat` possui o caminho correto apontando para onde você salvou o script `.py`.

Exemplo do conteúdo dentro do arquivo `.bat`:

```bat
@echo off
python "D:\Documentos\modelagens\extrusora-argila\ajuste_fluxo_argila.py" %*
if %errorlevel% neq 0 (
    echo Ocorreu um erro no Python!
    pause
    exit /b %errorlevel%
)
```

### 4. Configuração no PrusaSlicer

- Vá em **Print Settings** (Configurações de Impressão) > **Output options** (Opções de saída).
- No campo **Post-processing scripts** (Scripts de pós-processamento), insira o caminho completo do arquivo `.bat` entre aspas duplas.
- Exemplo: `"D:\Documentos\modelagens\extrusora-argila\executar_fluxo.bat"`

---

## 💡 Como Funciona na Prática

Ao clicar em "Export G-code" no PrusaSlicer, o arquivo `.bat` é acionado. Ele passa o G-code gerado para o script Python, que:

1. Faz a leitura do arquivo linha por linha;
2. Avalia em qual dos 4 estágios de altura a máquina está;
3. Injeta o comando `M221` correspondente àquele estágio/geometria;
4. Sobrescreve o arquivo instantaneamente.

---

*Script desenvolvido para otimização de manufatura aditiva em materiais cerâmicos.*
