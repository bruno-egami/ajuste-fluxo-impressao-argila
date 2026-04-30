import sys
import os

# =====================================================================
# CONFIGURAÇÕES GERAIS
# =====================================================================
# Dicionário de fluxo por tipo de linha (Usado após as camadas iniciais)
FLOW_SETTINGS = {
    ";TYPE:External perimeter": 150,
    ";TYPE:Perimeter": 90,
    ";TYPE:Internal infill": 100,
    ";TYPE:Solid infill": 95,
    ";TYPE:Top solid infill": 85,
    ";TYPE:Skirt/Brim": 100
}

# Configurações para as primeiras camadas
LIMITE_PRIMEIRAS_CAMADAS = 3
FLUXO_PRIMEIRAS_CAMADAS = 80

def process_gcode(file_path):
    """
    Função que processa o G-code, contando as camadas e aplicando
    a regra de fluxo correta com base na altura da impressão.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()

    new_lines = []
    camada_atual = 0  # Inicia o contador de camadas
    
    for line in lines:
        new_lines.append(line) # Mantém a linha original
        clean_line = line.strip()
        
        # 1. Identifica a mudança de camada e atualiza o contador
        if clean_line == ";LAYER_CHANGE":
            camada_atual += 1

        # 2. Verifica se a linha atual é um marcador de tipo de extrusão
        if clean_line in FLOW_SETTINGS:
            
            # 3. Lógica Condicional: É uma das primeiras camadas?
            if camada_atual <= LIMITE_PRIMEIRAS_CAMADAS:
                # Força o fluxo para 70% e avisa no código
                comando = f"M221 S{FLUXO_PRIMEIRAS_CAMADAS} ; --- FORCADO {FLUXO_PRIMEIRAS_CAMADAS}% (CAMADA {camada_atual}) ---\n"
                new_lines.append(comando)
                
            else:
                # Usa os valores individuais do dicionário
                flow_value = FLOW_SETTINGS[clean_line]
                comando = f"M221 S{flow_value} ; --- FLUXO DINAMICO APLICADO ({flow_value}%) ---\n"
                new_lines.append(comando)

    # Salva o arquivo modificado
    with open(file_path, "w") as file:
        file.writelines(new_lines)
    
    print(f"Sucesso: Fluxos dinâmicos e controle de base aplicados em {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho do arquivo G-code.")
        sys.exit(1)
        
    caminho_do_gcode = sys.argv[1]
    process_gcode(caminho_do_gcode)