from datetime import datetime
from typing import Dict, Any, Optional
from .sistema_triagem import SistemaTriagem

def exibir_referencias():
    '''
    Exibe os parâmetros médicos de referência para auxiliar a entrada de dados;
    '''
    print("\n" + "-"*45)
    print(" PARÂMETROS MÉDICOS DE REFERÊNCIA ".center(45, "-"))
    print(" Glasgow: 15 (Normal) | < 14 (Crítico)")
    print(" SpO2: 95-100% (Normal) | < 90% (Crítico)")
    print(" FC: 60-100 bpm (Normal) | > 150 ou < 40 (Crítico)")
    print(" Temperatura: 36.5°C (Normal) | > 39°C (Febre Alta)")
    print(" Escala de Dor: 0 (Sem dor) | 10 (Máxima)")
    print("-" * 45)

def obter_leitura_manual() -> Optional[Dict[str, Any]]:
    '''
    Coleta os sinais vitais do usuário via terminal com guias de referência;
    '''
    exibir_referencias()
    hora = datetime.now().strftime("%H:%M")
    print(f"Horário da leitura: {hora}")
    
    try:
        glasgow = int(input("Escala de Glasgow (Média: 15): ") or 15)
        spo2 = int(input("Saturação SpO2 % (Média: 98): ") or 98)
        fc = int(input("Frequência Cardíaca bpm (Média: 80): ") or 80)
        temp = float(input("Temperatura °C (Média: 36.5): ") or 36.5)
        dor = int(input("Escala de Dor 0-10 (Média: 0): ") or 0)
        vomitos = int(input("Vômitos por hora (Média: 0): ") or 0)
        
        return {
            'hora': hora,
            'glasgow': glasgow,
            'spo2': spo2,
            'frequencia_cardiaca': fc,
            'temperatura': temp,
            'escala_dor': dor,
            'vomitos_por_hora': vomitos,
            'pulso_presente': True,
            'respirando': True
        }
    except ValueError:
        print("\nErro: Insira valores numéricos válidos.")
        return None

def acao_cadastrar_paciente(sistema: SistemaTriagem):
    '''
    Executa o fluxo de cadastro de um novo paciente;
    '''
    print("\n" + "-"*30)
    print(" CADASTRO DE NOVO PACIENTE ".center(30, "-"))
    nome = input("Nome Completo: ")
    if not nome:
        print("Erro: Nome é obrigatório.")
        return

    try:
        idade = int(input("Idade: "))
        gestante = input("Gestante? (s/n): ").lower() == 's'
        pcd = input("Pessoa com Deficiência? (s/n): ").lower() == 's'
        
        leitura = obter_leitura_manual()
        if leitura:
            paciente_data = {
                'id': nome,
                'idade': idade,
                'gestante': gestante,
                'deficiencia': pcd,
                'hora_entrada': datetime.now().strftime("%H:%M"),
                'leituras': [leitura]
            }
            sistema.add_paciente(paciente_data)
            print(f"\nSucesso: Paciente '{nome}' cadastrado e triado.")
    except ValueError:
        print("\nErro: Idade deve ser um número.")

def acao_atualizar_vituais(sistema: SistemaTriagem):
    '''
    Executa o fluxo de atualização de sinais vitais de um paciente existente;
    '''
    print("\n" + "-"*30)
    print(" ATUALIZAR SINAIS VITAIS ".center(30, "-"))
    nome_busca = input("Digite o nome completo do paciente: ")
    
    leitura = obter_leitura_manual()
    if leitura:
        resultado = sistema.atualizar_sinais_vitais(nome_busca, leitura)
        if resultado:
            print(f"\nSucesso: Sinais vitais de '{nome_busca}' atualizados.")
        else:
            print(f"\nErro: Paciente '{nome_busca}' não encontrado no sistema.")

def acao_exibir_fila(sistema: SistemaTriagem):
    '''
    Chama a exibição da fila de atendimento;
    '''
    sistema.exibe_fila()

def acao_exibir_logs(sistema: SistemaTriagem):
    '''
    Chama a exibição dos logs de inferência;
    '''
    sistema.exibe_log()
