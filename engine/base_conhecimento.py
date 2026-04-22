
# Regras primárias de classificação de pacientes, baseadas em sinais vitais e sintomas;
REGRAS_PRIMARIAS = [
    {
        'id': 'R1',
        'nivel': 1,
        'condicoes': [
            {'campo': 'pulso_presente', 'op': '==', 'valor': False},
            {'campo': 'respirando', 'op': '==', 'valor': False}
        ],
        'operador_logico': 'OR',
        'descricao': 'Emergencia: Parada cardiorrespiratória ou apneia',
        'sintoma_grafo': 'PARADA'
    },
    {
        'id': 'R2',
        'nivel': 2,
        'condicoes': [
            {'campo': 'spo2', 'op': '<', 'valor': 90},
            {'campo': 'escala_dor', 'op': '>=', 'valor': 8},
            {'campo': 'glasgow', 'op': '<', 'valor': 14},
            {'campo': 'frequencia_cardiaca', 'op': '>', 'valor': 150},
            {'campo': 'frequencia_cardiaca', 'op': '<', 'valor': 40}
        ],
        'operador_logico': 'OR',
        'descricao': 'Muito urgente: Sinais vitais críticos',
        'sintoma_grafo': ['SPO2_CRITICO', 'DOR_INTENSA', 'GLASGOW_BAIXO', 'FC_CRITICA']
    },
    {
        'id': 'R3',
        'nivel': 3,
        'condicoes': [
            {'campo': 'temperatura', 'op': '>', 'valor': 39},
            {'campo': 'escala_dor', 'op': 'range', 'valor': [5,7]},
            {'campo': 'vomitos_por_hora', 'op': '>=', 'valor': 3},
            {'campo': 'frequencia_cardiaca', 'op': 'range', 'valor': [120, 150]},
            {'campo': 'frequencia_cardiaca', 'op': 'range', 'valor': [40, 50]}
        ],
        'operador_logico': 'OR',
        'descricao': 'Urgente: Febre alta, dor moderada ou vômitos',
        'sintoma_grafo': ['FEBRE_ALTA', 'DOR_MODERADA', 'VOMITOS', 'FC_ALTERADA']
    },
    {
        'id': 'R4',
        'nivel': 4,
        'condicoes': [
            {'campo': 'escala_dor', 'op': 'range', 'valor': [1, 4]}
        ],        'operador_logico': 'OR',
        'descricao': 'Baixa Prioridade: Dor leve ou queixa estável',
        'sintoma_grafo': 'DOR_LEVE'
    }
]

# Regras de segunda orgem;
REGRAS_SECUNDARIAS = [
    {
        'id': 'E1',
        'descricao': 'Reclassificação rápida de 3 para 2',
        'tipo': 'temporal'
    },
    {
        'id': 'E2',
        'descricao': 'Piora simultânea de dois ou mais sinais vitais',
        'tipo': 'piora_clinica'
    },
    {
        'id': 'E3',
        'descricao': 'Violação de  SLA do nível atual',
        'tipo': 'sla'
    },
    {
        'id': 'E4',
        'descricao': 'Vulnerável com aumento de temperatua > 1ºC',
        'tipo': 'vulneravel_piora'
    },
    {
        'id': 'E5',
        'descricao': 'Dupla violação de SLA',
        'tipo': 'sobrecarga'
    }
]

#Configuração do grafo para Urgências
GRAFO_URGENCIAS = {
    'nodes': {
        'PARADA': 1.0,
        'SPO2_CRITICO': 2.0,
        'DOR_INTENSA': 2.1,
        'GLASGOW_BAIXO': 2.2,
        'FC_CRITICA': 2.3,
        'FEBRE_ALTA': 3.0,
        'DOR_MODERADA': 3.1,
        'VOMITOS': 3.2,
        'FC_ALTERADA': 3.3,
        'DOR_LEVE': 4.0,
        'VULNERAVEL': -0.5 # Reduz o valor numérico (aumenta prioridade)
    },
    'edges': [
        ('SPO2_CRITICO', 'FC_CRITICA', 0.5), # Conexão aumenta urgência
        ('FEBRE_ALTA', 'VOMITOS', 0.3)
    ]
}

# SLAs do sistema de triagem (em minutos);
SLA_TEMPOS = {
    1: 0,
    2: 10,
    3: 30,
    4: 60,
    5: 120
}