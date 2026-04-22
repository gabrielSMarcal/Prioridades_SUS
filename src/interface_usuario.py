from datetime import datetime
from typing import Dict, Any, Optional
from .sistema_triagem import SistemaTriagem


def cor_prioridade(nivel: int) -> str:
    '''
    Retorna a cor de prioridade correspondente ao nível de triagem;
    '''
    cores = {
        1: 'Vermelho',
        2: 'Laranja',
        3: 'Amarelo',
        4: 'Verde',
        5: 'Azul'
    }
    return cores.get(nivel, 'Desconhecida')


def obter_leitura_manual() -> Optional[Dict[str, Any]]:
    '''
    Coleta os sinais vitais do usuário via terminal com guias de referência;
    '''
    
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

    if not sistema.paciente:
        print("Nenhum paciente cadastrado para atualização.")
        return

    print("\nPacientes cadastrados:")
    for i, paciente in enumerate(sistema.paciente, start=1):
        cor = cor_prioridade(paciente.prioridade_atual)
        print(f" {i}. {paciente.id} ({cor})")

    try:
        indice = int(input("Escolha o índice do paciente: "))
    except ValueError:
        print("\nErro: Informe um índice numérico válido.")
        return

    if indice < 1 or indice > len(sistema.paciente):
        print("\nErro: Índice fora da faixa de pacientes listados.")
        return

    paciente_selecionado = sistema.paciente[indice - 1]
    nome_busca = paciente_selecionado.id
    
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
