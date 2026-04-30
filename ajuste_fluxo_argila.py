import sys
import os

# =====================================================================
# PAINEL DE CONTROLE QUÁDRUPLO
# =====================================================================

# ----------------- LIMITES DE CAMADAS (Valores Absolutos) -----------------
# Exemplo de configuração:
# Camada 1: Base
# Camadas 2 a 3: Intermediário 1 (2 camadas de duração)
# Camadas 4 a 9: Intermediário 2 (6 camadas de duração)
# Camada 10 em diante: Geral

LIMITE_CAMADAS_BASE = 1
LIMITE_CAMADAS_INTERMEDIARIAS_1 = 3  
LIMITE_CAMADAS_INTERMEDIARIAS_2 = 20  


# ----------------- DICIONÁRIOS DE FLUXO -----------------

# 1. Configurações para a BASE
FLOW_SETTINGS_BASE = {
    ";TYPE:External perimeter": 75,
    ";TYPE:Perimeter": 75,
    ";TYPE:Internal infill": 80,
    ";TYPE:Solid infill": 75,
    ";TYPE:Top solid infill": 70,
    ";TYPE:Skirt/Brim": 100
}

# 2. Configurações para o INTERMEDIÁRIO 1 (Primeira transição)
FLOW_SETTINGS_INTERMEDIARIO_1 = {
    ";TYPE:External perimeter": 75,
    ";TYPE:Perimeter": 65,
    ";TYPE:Internal infill": 60,
    ";TYPE:Solid infill": 60,
    ";TYPE:Top solid infill": 60,
    ";TYPE:Skirt/Brim": 100
}

# 3. Configurações para o INTERMEDIÁRIO 2 (Segunda transição)
FLOW_SETTINGS_INTERMEDIARIO_2 = {
    ";TYPE:External perimeter": 150,
    ";TYPE:Perimeter": 85,
    ";TYPE:Internal infill": 90,
    ";TYPE:Solid infill": 85,
    ";TYPE:Top solid infill": 80,
    ";TYPE:Skirt/Brim": 95
}

# 4. Configurações GERAIS (Restante da peça)
FLOW_SETTINGS_GERAL = {
    ";TYPE:External perimeter": 85,
    ";TYPE:Perimeter": 90,
    ";TYPE:Internal infill": 100,
    ";TYPE:Solid infill": 95,
    ";TYPE:Top solid infill": 85,
    ";TYPE:Skirt/Brim": 100
}

# =====================================================================
# LÓGICA PRINCIPAL DO PROGRAMA
# =====================================================================

def process_gcode(file_path):
    """
    Função que processa o G-code, conta as camadas e decide qual 
    dos QUATRO dicionários de fluxo usar através de uma cascata de decisão.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()

    new_lines = []
    camada_atual = 0
    
    for line in lines:
        new_lines.append(line)
        clean_line = line.strip()
        
        # Conta a mudança de camadas
        if clean_line == ";LAYER_CHANGE":
            camada_atual += 1

        # Lógica em Cascata (if / elif / elif / else)
        if camada_atual <= LIMITE_CAMADAS_BASE:
            dicionario_ativo = FLOW_SETTINGS_BASE
            nome_fase = f"BASE (Camada {camada_atual})"
            
        elif camada_atual <= LIMITE_CAMADAS_INTERMEDIARIAS_1:
            dicionario_ativo = FLOW_SETTINGS_INTERMEDIARIO_1
            nome_fase = f"INTERMEDIARIO_1 (Camada {camada_atual})"
            
        elif camada_atual <= LIMITE_CAMADAS_INTERMEDIARIAS_2:
            dicionario_ativo = FLOW_SETTINGS_INTERMEDIARIO_2
            nome_fase = f"INTERMEDIARIO_2 (Camada {camada_atual})"
            
        else:
            dicionario_ativo = FLOW_SETTINGS_GERAL
            nome_fase = "GERAL"

        # Aplica o fluxo se encontrar a linha correspondente
        if clean_line in dicionario_ativo:
            flow_value = dicionario_ativo[clean_line]
            
            # Injeta o comando M221 no G-code
            comando = f"M221 S{flow_value} ; --- FLUXO {nome_fase}: {flow_value}% ---\n"
            new_lines.append(comando)

    # Sobrescreve o arquivo com os novos dados
    with open(file_path, "w") as file:
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
