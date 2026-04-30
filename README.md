# Ajuste Dinâmico de Fluxo para Extrusão de Argila 🏺

Este é um script de pós-processamento em Python para o PrusaSlicer, desenvolvido para otimizar o controle de extrusão na impressão 3D de argila e cerâmica (sistemas baseados em Marlin).

## 🎯 O Problema
Na impressão de argila com bicos de grande diâmetro (ex: 3mm), alterar a "Largura da Linha" (Line Width) diretamente no fatiador faz com que o software recalcule toda a trajetória da ferramenta (toolpath). Isso pode gerar deformações e instabilidades de pressão nas quinas. O método ideal é manter a trajetória original intacta e alterar dinamicamente apenas a **quantidade de material depositado** de acordo com a parte da peça que está a ser impressa (perímetros, preenchimentos, etc.).

## 🚀 A Solução
Este script atua de forma invisível logo após o fatiamento. Ele lê o arquivo G-code gerado pelo PrusaSlicer, conta as camadas e injeta comandos nativos do Marlin (`M221 S...` - Flow Rate) baseados em regras lógicas predefinidas.

### ✨ Funcionalidades Principais
1. **Trava de Segurança da Base (First Layer Lock):** Mantém um fluxo reduzido e constante (ex: 70%) durante as primeiras camadas (ex: camadas 1 a 3). Isso garante uma base sólida sem que o bico esmague ou arraste a argila molhada.
2. **Fluxo Dinâmico por Geometria:** A partir da 4ª camada, o script lê os comentários do fatiador e aplica percentuais de fluxo específicos para:
   * `External perimeter` (Perímetros Externos)
   * `Perimeter` (Perímetros Internos)
   * `Internal infill` (Preenchimento Interno)
   * `Solid infill` & `Top solid infill` (Preenchimento Sólido e de Topo)
   * `Skirt/Brim`

## 🛠️ Pré-requisitos
* [Python 3.x](https://www.python.org/) instalado e adicionado ao PATH do sistema.
* PrusaSlicer.
* Impressora 3D com firmware Marlin configurada para leitura do comando M221.

## ⚙️ Instalação e Uso (Ambiente Windows)

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/bknegami/extrusora-argila.git](https://github.com/bknegami/extrusora-argila.git)
