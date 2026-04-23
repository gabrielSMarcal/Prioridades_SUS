import sys
import os
import time

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sistema_triagem import SistemaTriagem


def adicionar_paciente(sistema, nome, idade, hora_entrada, leituras):
    """Cadastro padronizado para deixar os cenários mais legíveis."""
    return sistema.add_paciente({
        'id': nome,
        'idade': idade,
        'hora_entrada': hora_entrada,
        'leituras': leituras
    })


def rodar_teste():
    inicio_tempo = time.time()
    sistema = SistemaTriagem()
    
    print('Iniciando Suite de Testes - Triagem SUS')
    print('-' * 40)

    # Cenário E1: Mesmo nível, mesma hora de chegada
    print('\n[E1] Mesmo nível, mesma hora de chegada')
    adicionar_paciente(sistema, 'Ana Costa', 30, '10:00', [{'hora': '10:00', 'escala_dor': 6}])
    adicionar_paciente(sistema, 'Bruno Lima', 35, '10:00', [{'hora': '10:00', 'escala_dor': 6}])
    # Devem estar no Nível 3 (Amarelo)
    
    # Cenário E2: Mesmo nível, velocidade de piora diferente
    print('[E2] Velocidade de piora diferente')
    adicionar_paciente(sistema, 'Carlos Souza', 40, '10:00', [{'hora': '10:00', 'escala_dor': 6}])
    adicionar_paciente(sistema, 'Daniela Rocha', 45, '10:20', [
        {'hora': '10:20', 'escala_dor': 6, 'spo2': 98},
        {'hora': '10:25', 'escala_dor': 7, 'spo2': 95} # Piora
    ])
    
    # Cenário E3: Vulnerável vs. Piora Clínica Objetiva
    print('[E3] Vulnerável vs. Piora clínica')
    adicionar_paciente(sistema, 'Elisa Martins', 62, '10:00', [{'hora': '10:00', 'escala_dor': 4}]) # Nível 3 por vuln
    adicionar_paciente(sistema, 'Felipe Almeida', 35, '10:28', [
        {'hora': '10:28', 'spo2': 95},
        {'hora': '10:30', 'spo2': 92} # Piora
    ])
    
    # Cenário E4: Vulnerável + Piora Temperatura (Regra E4)
    print('[E4] Vulnerável + Piora de temperatura')
    adicionar_paciente(sistema, 'Geraldo Nunes', 70, '11:00', [
        {'hora': '11:00', 'temperatura': 37.0},
        {'hora': '11:10', 'temperatura': 38.5} # Subiu > 1 grau
    ])
    
    # Cenário E5: Dupla violação de SLA (Regra E5)
    print('[E5] Dupla violação de SLA')
    adicionar_paciente(sistema, 'Helena Prado', 30, '10:00', [
        {'hora': '10:40', 'escala_dor': 6}, # Nível 3, espera 40 min (SLA 30) -> 1ª violação
        {'hora': '11:10', 'escala_dor': 6}  # Nível 3, espera 70 min (SLA 30) -> 2ª violação
    ])

    # Exibir Fila Final
    sistema.exibe_fila()
    
    # Exibir Logs
    sistema.exibe_log()
    
    tempo_final = time.time()
    print(f'\nTempo total de execução: {tempo_final - inicio_tempo:.4f} segundos')

if __name__ == '__main__':
    rodar_teste()