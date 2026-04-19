import sys
import os
import time
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sistema_triagem import SistemaTriagem

def rodar_teste():
    inicio_tempo = time.time()
    sistema = SistemaTriagem()
    
    print('Iniciando Suite de Testes - Triagem SUS')
    print('-' * 40)

    # Cenário E1: Mesmo nível, mesma hora de chegada
    print('Testando E1: Mesmo nível, mesma hora de chegada...')
    p1 = sistema.add_paciente({'id': 'E1-A', 'idade': 30, 'hora_entrada': '10:00', 'leituras': [{'hora': '10:00', 'escala_dor': 6}]})
    p2 = sistema.add_paciente({'id': 'E1-B', 'idade': 35, 'hora_entrada': '10:00', 'leituras': [{'hora': '10:00', 'escala_dor': 6}]})
    # Devem estar no Nível 3 (Amarelo)
    
    # Cenário E2: Mesmo nível, velocidade de piora diferente
    print('Testando E2: Velocidade de piora diferente...')
    p3 = sistema.add_paciente({'id': 'E2-A', 'idade': 40, 'hora_entrada': '10:00', 'leituras': [{'hora': '10:00', 'escala_dor': 6}]})
    p4 = sistema.add_paciente({'id': 'E2-B', 'idade': 45, 'hora_entrada': '10:20', 'leituras': [
        {'hora': '10:20', 'escala_dor': 6, 'spo2': 98},
        {'hora': '10:25', 'escala_dor': 7, 'spo2': 95} # Piora
    ]})
    
    # Cenário E3: Vulnerável vs. Piora Clínica Objetiva
    print('Testando E3: Vulnerável vs. Piora Clínica...')
    p5 = sistema.add_paciente({'id': 'E3-A', 'idade': 62, 'hora_entrada': '10:00', 'leituras': [{'hora': '10:00', 'escala_dor': 4}]}) # Nível 3 por vuln
    p6 = sistema.add_paciente({'id': 'E3-B', 'idade': 35, 'hora_entrada': '10:28', 'leituras': [
        {'hora': '10:28', 'spo2': 95},
        {'hora': '10:30', 'spo2': 92} # Piora
    ]})
    
    # Cenário E4: Vulnerável + Piora Temperatura (Regra E4)
    print('Testando E4: Vulnerável + Piora Temperatura...')
    p7 = sistema.add_paciente({'id': 'E4-VULN', 'idade': 70, 'hora_entrada': '11:00', 'leituras': [
        {'hora': '11:00', 'temperatura': 37.0},
        {'hora': '11:10', 'temperatura': 38.5} # Subiu > 1 grau
    ]})
    
    # Cenário E5: Dupla violação de SLA (Regra E5)
    # Simulado via logs, pois o sistema é reativo
    print('Testando E5: Simulação de Alertas...')
    sistema.motor.log_inferencia('E5-PAC', 'E5', 'Protocolo Sobrecarga', 'Dupla violação de SLA detectada')

    # Exibir Fila Final
    sistema.exibe_fila()
    
    # Exibir Logs
    sistema.exibe_log()
    
    tempo_final = time.time()
    print(f'\nTempo total de execução: {tempo_final - inicio_tempo:.4f} segundos')

if __name__ == '__main__':
    rodar_teste()