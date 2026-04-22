import sys
import os
from datetime import datetime, timedelta
from src.sistema_triagem import SistemaTriagem
from src.interface_usuario import (
    acao_cadastrar_paciente, 
    acao_atualizar_vituais, 
    acao_exibir_fila, 
    acao_exibir_logs
)

# Adiciona o diretório atual ao path para importações;
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    '''
    Ponto de entrada do sistema com menu Switch Case e pacientes iniciais;
    '''
    sistema = SistemaTriagem()
    horario_base = datetime.now() - timedelta(minutes=30)
    horario_p1 = horario_base.strftime('%H:%M')
    horario_p2 = (horario_base + timedelta(minutes=15)).strftime('%H:%M')
    horario_p3 = (horario_base + timedelta(minutes=30)).strftime('%H:%M')
    
    # 1. Dados dos Pacientes Iniciais (Regra de Negócio)
    pacientes_iniciais = [
        {
            'id': 'João Silva Oliveira',
            'idade': 72, # Vulnerável (Idoso)
            'gestante': False,
            'deficiencia': False,
            'hora_entrada': horario_p1,
            'leituras': [{'hora': horario_p1, 'spo2': 96, 'frequencia_cardiaca': 75, 'temperatura': 36.6, 'escala_dor': 2}]
        },
        {
            'id': 'Maria Souza Santos',
            'idade': 28,
            'gestante': True, # Vulnerável (Gestante)
            'deficiencia': False,
            'hora_entrada': horario_p2,
            'leituras': [{'hora': horario_p2, 'spo2': 98, 'frequencia_cardiaca': 82, 'temperatura': 37.0, 'escala_dor': 5}]
        },
        {
            'id': 'Carlos Eduardo Lima',
            'idade': 45,
            'gestante': False,
            'deficiencia': False,
            'hora_entrada': horario_p3,
            'leituras': [{'hora': horario_p3, 'spo2': 88, 'frequencia_cardiaca': 110, 'temperatura': 38.2, 'escala_dor': 8}]
        }
    ]
    
    # Cadastra os pacientes iniciais no sistema;
    for p_data in pacientes_iniciais:
        sistema.add_paciente(p_data)

    # 2. Estrutura do Menu (Switch Case)
    while True:
        print("\n" + "="*60)
        print(" MENU DE TRIAGEM INTELIGENTE - UPA SUS ".center(60, "="))
        print("="*60)
        print(" 1. Visualizar Fila de Atendimento")
        print(" 2. Cadastrar Novo Paciente")
        print(" 3. Atualizar Sinais Vitais de um Paciente")
        print(" 4. Ver Logs de Inferência")
        print(" 0. Sair")
        print("="*60)
        
        opcao = input("Escolha uma opção: ")
        
        # Simulação de Switch Case em Python;
        if opcao == '1':
            acao_exibir_fila(sistema)
        
        elif opcao == '2':
            acao_cadastrar_paciente(sistema)

        elif opcao == '3':
            acao_atualizar_vituais(sistema)

        elif opcao == '4':
            acao_exibir_logs(sistema)
            
        elif opcao == '0':
            print("\nEncerrando sistema de triagem...")
            break
        
        else:
            print("\nOpção inválida. Por favor, escolha um número do menu.")

if __name__ == '__main__':
    main()
