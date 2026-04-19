import sys
import os
from typing import List, Dict, Any
from models.paciente import Paciente
from engine.motor_inferencia import MotorInferencia
from engine.empate_breaker import EmpateBreaker

# Adiciona o diretório atual ao path para importações;
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SistemaTriagem:
    '''
    Sistema de Triagem Inteligente para UPA - SUS Brasil;
    '''
    
    def __init__(self): 
        self.motor = MotorInferencia()
        self.empate_breaker = EmpateBreaker()
        self.paciente: List[Paciente] = []
        
    def add_paciente(self, paciente_dado: Dict[str, Any]):
        '''
        Adiciona um novo paciente ao sistema e executa a triagem inicial;
        '''
        
        # Extrai leituras iniciais para processar uma a uma;
        leituras_iniciais = paciente_dado.get('leituras', [])
        paciente_dado['leituras'] = [] # Limpa para o construtor
        
        p = Paciente(paciente_dado)
        self.paciente.append(p)
        
        if not leituras_iniciais:
            self.motor.rodar_inferencia(p)
        else:
            for leitura in leituras_iniciais:
                
                p.add_leitura(leitura)
                self.motor.rodar_inferencia(p)
        
        return p
    
    def atualizar_sinais_vitais(self, paciente_id: str, nova_leitura: Dict[str, Any]):
        '''
        Atualiza os sinais vitais de um paciente e reavalia a triagem;
        '''
        
        for p in self.paciente:
            
            if p.id == paciente_id:
                p.add_leitura(nova_leitura)
                self.motor.rodar_inferencia(p)
                return p
            
        return None
    
    def get_fila(self) -> List[Paciente]:
        '''
        Retorna a fila de atendimento ordenada por prioridade e desempate;
        '''
        
        #Agrupa por nível de prioridade;
        levels = {i: [] for i in range(1, 6)}
        
        for p in self.paciente:
            
            levels[p.prioridade_atual].append(p)
            
        # Ordena cada nível usando o critério de desempate;
        fila_ordenada = []
        
        for i in range(1, 6):
            if levels[i]:
                fila_ordenada.extend(self.empate_breaker.resolve_empate(levels[i]))
        
        return fila_ordenada
    
    def exibe_fila(self):
        '''
        Exibe a fila de atendimento formatada;
        '''
        
        fila = self.get_fila()
        print('\n' + '='*60)
        print(' FILA DE ATENDIMENTO - UPA SUS BRASIL '.center(60, '='))
        print('='*60)
        print(f'{"ID":<15} | {"NÍVEL":<10} | {"COR":<10} | {"VULN":<5} | {"ESPERA"}')
        print('-' * 60)
        
        colors = {1: 'Vermelho', 2: 'Laranja', 3: 'Amarelo', 4: 'Verde', 5: 'Azul'}
        
        for p in fila:
            
            vulneravel = 'Sim' if p.vuleravel else 'Não'
            print(f'{p.id:<15} | {p.prioridade_atual:<10} | {colors[p.prioridade_atual]:<10} | {vulneravel:<5} | {p.hora_entrada}')
            
        print('='*60 + '\n')
        
    def exibe_log(self):
        '''
        Exibe os logs de inferência;
        '''
        
        print('\n' + '='*60)
        print(' LOGS DE INFERÊNCIA (AUDITÁVEL)'.center(60, '='))
        print('='*60)
        
        for log in self.motor.logs:
            
            print(f'[{log["hora"]}] Paciente: {log["paciente"]} | Regra: {log["regra"]}')
            print(f'  Conclusão: {log["conclusao"]}')
            print(f'  Detalhes: {log["detalhes"]}')
            print('-' * 60)