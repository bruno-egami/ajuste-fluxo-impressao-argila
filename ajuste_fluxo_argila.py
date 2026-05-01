import sys

# =====================================================================
# PAINEL DE CONTROLE QUÁDRUPLO — FLUXO (M221) + VELOCIDADE (M220)
# =====================================================================

# ----------------- LIMITES DE CAMADAS (Valores Absolutos) -----------------
LIMITE_CAMADAS_BASE             = 1
LIMITE_CAMADAS_INTERMEDIARIAS_1 = 3
LIMITE_CAMADAS_INTERMEDIARIAS_2 = 20


# ======================================================
# VELOCIDADE POR FASE — M220 (% da velocidade configurada)
# Um único valor aplicado a toda a fase no LAYER_CHANGE
# ======================================================

SPEED_BASE             = 50
SPEED_INTERMEDIARIO_1  = 60
SPEED_INTERMEDIARIO_2  = 80
SPEED_GERAL            = 100


# ======================================================
# DICIONÁRIOS DE FLUXO — M221 (% do fluxo configurado)
# Controle individual por tipo de segmento em cada fase
# ======================================================

FLOW_SETTINGS_BASE = {
    ";TYPE:External perimeter": 75,
    ";TYPE:Perimeter":          75,
    ";TYPE:Internal infill":    80,
    ";TYPE:Solid infill":       75,
    ";TYPE:Top solid infill":   70,
    ";TYPE:Skirt/Brim":        100
}

FLOW_SETTINGS_INTERMEDIARIO_1 = {
    ";TYPE:External perimeter": 75,
    ";TYPE:Perimeter":          65,
    ";TYPE:Internal infill":    60,
    ";TYPE:Solid infill":       60,
    ";TYPE:Top solid infill":   60,
    ";TYPE:Skirt/Brim":        100
}

FLOW_SETTINGS_INTERMEDIARIO_2 = {
    ";TYPE:External perimeter": 150,
    ";TYPE:Perimeter":           85,
    ";TYPE:Internal infill":     90,
    ";TYPE:Solid infill":        85,
    ";TYPE:Top solid infill":    80,
    ";TYPE:Skirt/Brim":          95
}

FLOW_SETTINGS_GERAL = {
    ";TYPE:External perimeter":  85,
    ";TYPE:Perimeter":           90,
    ";TYPE:Internal infill":    100,
    ";TYPE:Solid infill":        95,
    ";TYPE:Top solid infill":    85,
    ";TYPE:Skirt/Brim":         100
}


# =====================================================================
# LÓGICA PRINCIPAL DO PROGRAMA
# =====================================================================

FASES = [
    (LIMITE_CAMADAS_BASE,              FLOW_SETTINGS_BASE,            SPEED_BASE,            "BASE"),
    (LIMITE_CAMADAS_INTERMEDIARIAS_1,  FLOW_SETTINGS_INTERMEDIARIO_1, SPEED_INTERMEDIARIO_1, "INTERMEDIARIO_1"),
    (LIMITE_CAMADAS_INTERMEDIARIAS_2,  FLOW_SETTINGS_INTERMEDIARIO_2, SPEED_INTERMEDIARIO_2, "INTERMEDIARIO_2"),
]


def get_configuracoes(camada_atual):
    for limite, flow_dict, speed, nome in FASES:
        if camada_atual <= limite:
            return flow_dict, speed, f"{nome} (Camada {camada_atual})"
    return FLOW_SETTINGS_GERAL, SPEED_GERAL, "GERAL"


def process_gcode(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    new_lines = []
    camada_atual = 0

    for line in lines:
        new_lines.append(line)
        clean_line = line.strip()

        # Mudança de camada: injeta velocidade + fallback de fluxo (vase mode)
        if clean_line == ";LAYER_CHANGE":
            camada_atual += 1
            flow_dict, speed_valor, nome_fase = get_configuracoes(camada_atual)

            new_lines.append(
                f"M220 S{speed_valor} ; --- VELOCIDADE {nome_fase}: {speed_valor}% ---\n"
            )
            flow_padrao = flow_dict.get(";TYPE:External perimeter")
            if flow_padrao is not None:
                new_lines.append(
                    f"M221 S{flow_padrao} ; --- FLUXO {nome_fase} [layer fallback]: {flow_padrao}% ---\n"
                )
            continue

        # Injeção precisa de fluxo por tipo de segmento
        flow_dict, _, nome_fase = get_configuracoes(camada_atual)

        if clean_line in flow_dict:
            flow_value = flow_dict[clean_line]
            new_lines.append(
                f"M221 S{flow_value} ; --- FLUXO {nome_fase}: {flow_value}% ---\n"
            )

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(new_lines)

    print(f"Sucesso: Fluxo e velocidade em 4 níveis aplicados em {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho do arquivo G-code.")
        sys.exit(1)

    caminho_do_gcode = sys.argv[1]
    process_gcode(caminho_do_gcode)
