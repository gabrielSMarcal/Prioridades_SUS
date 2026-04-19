from src.sistema_triagem import SistemaTriagem
import sys
import os

# Adiciona o diretório atual ao path para importações;
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    sistema = SistemaTriagem()
    
    # Exemplo de uso baseado na documentação
    paciente_exemplo = {
        'id': 'PAC-2026-001',
        'idade': 67,
        'gestante': False,
        'deficiencia': False,
        'hora_entrada': '14:00',
        'leituras': [
            {
                'hora': '14:00',
                'consciente': True,
                'glasgow': 15,
                'spo2': 95,
                'frequencia_cardiaca': 88,
                'temperatura': 37.2,
                'escala_dor': 3,
                'vomitos_por_hora': 0,
                'pulso_presente': True,
                'respirando': True
            }
        ]
    }
    
    print('Iniciando Sistema de Triagem Inteligente...')
    p1 = sistema.add_paciente(paciente_exemplo)
    print(f'Paciente {p1.id} triado inicialmente como Nível {p1.prioridade_atual}')
    
    # Atualização com piora clínica
    nova_leitura = {
        'hora': '14:25',
        'glasgow': 14,
        'spo2': 89,
        'frequencia_cardiaca': 122,
        'temperatura': 38.6,
        'escala_dor': 7,
        'vomitos_por_hora': 2
    }
    sistema.atualizar_sinais_vitais(p1.id, nova_leitura)
    
    sistema.exibe_fila()
    sistema.exibe_log()

if __name__ == '__main__':
    main()