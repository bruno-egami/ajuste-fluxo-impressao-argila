import sys

# =====================================================================
# PAINEL DE CONTROLE QUÁDRUPLO
# =====================================================================

# ----------------- LIMITES DE CAMADAS (Valores Absolutos) -----------------
# Exemplo de configuração:
# Camada 1: Base
# Camadas 2 a 3: Intermediário 1 (2 camadas de duração)
# Camadas 4 a 20: Intermediário 2 (17 camadas de duração)
# Camada 21 em diante: Geral

LIMITE_CAMADAS_BASE = 1
LIMITE_CAMADAS_INTERMEDIARIAS_1 = 3
LIMITE_CAMADAS_INTERMEDIARIAS_2 = 4


# ----------------- DICIONÁRIOS DE FLUXO -----------------

# 1. Configurações para a BASE
FLOW_SETTINGS_BASE = {
    ";TYPE:External perimeter": 100,
    ";TYPE:Perimeter": 75,
    ";TYPE:Internal infill": 80,
    ";TYPE:Solid infill": 75,
    ";TYPE:Top solid infill": 70,
    ";TYPE:Skirt/Brim": 100
}

# 2. Configurações para o INTERMEDIÁRIO 1 (Primeira transição)
FLOW_SETTINGS_INTERMEDIARIO_1 = {
    ";TYPE:External perimeter": 80,
    ";TYPE:Perimeter": 65,
    ";TYPE:Internal infill": 65,
    ";TYPE:Solid infill": 65,
    ";TYPE:Top solid infill": 65,
    ";TYPE:Skirt/Brim": 100
}

# 3. Configurações para o INTERMEDIÁRIO 2 (Segunda transição)
FLOW_SETTINGS_INTERMEDIARIO_2 = {
    ";TYPE:External perimeter": 75,
    ";TYPE:Perimeter": 85,
    ";TYPE:Internal infill": 90,
    ";TYPE:Solid infill": 85,
    ";TYPE:Top solid infill": 80,
    ";TYPE:Skirt/Brim": 95
}

# 4. Configurações GERAIS (Restante da peça)
FLOW_SETTINGS_GERAL = {
    ";TYPE:External perimeter": 150,
    ";TYPE:Perimeter": 150,
    ";TYPE:Internal infill": 100,
    ";TYPE:Solid infill": 95,
    ";TYPE:Top solid infill": 85,
    ";TYPE:Skirt/Brim": 100
}

# =====================================================================
# LÓGICA PRINCIPAL DO PROGRAMA
# =====================================================================

def get_dicionario_e_fase(camada_atual):
    """Retorna o dicionário ativo e o nome da fase para a camada atual."""
    if camada_atual <= LIMITE_CAMADAS_BASE:
        return FLOW_SETTINGS_BASE, f"BASE (Camada {camada_atual})"
    elif camada_atual <= LIMITE_CAMADAS_INTERMEDIARIAS_1:
        return FLOW_SETTINGS_INTERMEDIARIO_1, f"INTERMEDIARIO_1 (Camada {camada_atual})"
    elif camada_atual <= LIMITE_CAMADAS_INTERMEDIARIAS_2:
        return FLOW_SETTINGS_INTERMEDIARIO_2, f"INTERMEDIARIO_2 (Camada {camada_atual})"
    else:
        return FLOW_SETTINGS_GERAL, "GERAL"


def process_gcode(file_path):
    """
    Função que processa o G-code, conta as camadas e decide qual
    dos QUATRO dicionários de fluxo usar através de uma cascata de decisão.

    Suporta tanto impressão normal (com comentários ;TYPE:) quanto
    vase mode / espiral contínua, injetando M221 também em cada
    ;LAYER_CHANGE como fallback para camadas sem marcadores de tipo.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    new_lines = []
    camada_atual = 0

    for line in lines:
        new_lines.append(line)
        clean_line = line.strip()

        # --- Mudança de camada: injeta M221 como fallback para vase mode ---
        # Em vase mode, não existem comentários ;TYPE: após as camadas iniciais.
        # Injetar aqui garante que o fluxo correto seja aplicado em toda camada,
        # independente do modo de impressão. Em impressão normal, o bloco
        # ;TYPE: abaixo sobrescreve este comando com maior precisão.
        if clean_line == ";LAYER_CHANGE":
            camada_atual += 1
            dicionario_ativo, nome_fase = get_dicionario_e_fase(camada_atual)
            flow_padrao = dicionario_ativo.get(";TYPE:External perimeter")
            if flow_padrao is not None:
                comando = f"M221 S{flow_padrao} ; --- FLUXO {nome_fase} [layer fallback]: {flow_padrao}% ---\n"
                new_lines.append(comando)
            continue

        # --- Injeção precisa por tipo de segmento (impressão normal) ---
        # Detecta os comentários ;TYPE: do PrusaSlicer e sobrescreve o fluxo
        # com o valor específico para aquele tipo de geometria.
        dicionario_ativo, nome_fase = get_dicionario_e_fase(camada_atual)

        if clean_line in dicionario_ativo:
            flow_value = dicionario_ativo[clean_line]
            comando = f"M221 S{flow_value} ; --- FLUXO {nome_fase}: {flow_value}% ---\n"
            new_lines.append(comando)

    # Sobrescreve o arquivo com os novos dados
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(new_lines)

    print(f"Sucesso: Fluxos em 4 níveis aplicados em {file_path}")


# =====================================================================
# INÍCIO DA EXECUÇÃO
# =====================================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho do arquivo G-code.")
        sys.exit(1)

    caminho_do_gcode = sys.argv[1]
    process_gcode(caminho_do_gcode)
