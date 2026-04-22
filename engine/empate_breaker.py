from typing import List
from datetime import datetime
from models.paciente import Paciente
from .base_conhecimento import SLA_TEMPOS

class EmpateBreaker:
    '''
    Classe que implementa o critério de desempate para pacientes no mesmo nível;
    '''
    
    def resolve_empate(self, pacientes: List[Paciente]) -> List[Paciente]:
        '''
        Ordena uma lista de pacientes no mesmo nível de prioridade;
        '''
        if not pacientes:
            return []
        
        pontuacao_paciente = []
        for p in pacientes:
            ponto = self._calcular_pontuacao_instabilidade(p)
            pontuacao_paciente.append((p, ponto))
            
        # Ordena por pontuação (maior pontuação = mais urgente);
        pontuacao_paciente.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, s in pontuacao_paciente]
    
    def _calcular_pontuacao_instabilidade(self, paciente: Paciente) -> float:
        '''
        Calcula o score de instabilidade (SI) para desempate;
        SI = (Fator de Espera) * (Fator de Tendência) * (Fator de Vulnerabilidade)
        '''
        
        # 1. Fator de Espera (Relativo ao SLA do nível);
        try:
            h_entrada = datetime.strptime(paciente.hora_entrada, '%H:%M')
            h_atual = datetime.strptime(paciente.get_ultima_leitura()['hora'], '%H:%M') if paciente.get_ultima_leitura() else h_entrada 
            espera = (h_atual - h_entrada).total_seconds() / 60
            
            # Obtém o SLA do nível atual do paciente;
            sla_limite = SLA_TEMPOS.get(paciente.prioridade_atual, 120)
            
            # Fator de espera é a razão entre o tempo esperado e o SLA permitido;
            # Se sla_limite for 0 (Vermelho), usamos 1 para evitar divisão por zero;
            fator_espera = (espera + 1) / (sla_limite if sla_limite > 0 else 1)
        except:
            fator_espera = 1.0
            
        # 2. Fator de Tendência (Piora clínica);
        tendencia = 1.0
        if len(paciente.leituras) >= 2:
            l1 = paciente.get_penultima_leitura()
            l2 = paciente.get_ultima_leitura()
            
            # Se sinais vitais pioram, aumenta o fator;
            if l2.get('spo2', 100) < l1.get('spo2', 100): tendencia += 0.5
            if l2.get('escala_dor', 0) > l1.get('escala_dor', 0): tendencia += 0.3
            if l2.get('glasgow', 15) < l1.get('glasgow', 15): tendencia += 0.4
            
        # 3. Fator de Vulnerabilidade;
        vulnerabilidade = 1.2 if paciente.vuleravel else 1.0
        
        # Score Final;
        return fator_espera * tendencia * vulnerabilidade
    
    def get_audit_log(self, p1: Paciente, p2: Paciente) -> str:
        '''
        Gera uma explicação legível para o desempate entre dois pacientes;
        '''
        s1 = self._calcular_pontuacao_instabilidade(p1)
        s2 = self._calcular_pontuacao_instabilidade(p2)
        
        vencedor = p1.id if s1 > s2 else p2.id
        
        # Lógica simplificada para o motivo no log;
        if p1.vuleravel != p2.vuleravel:
            motivo = 'Prioridade legal (Vulnerabilidade)'
        elif s1 != s2:
            motivo = 'Maior instabilidade clínica ou tempo de espera excedido'
        else:
            motivo = 'Critério de desempate técnico'
            
        return f'Paciente {vencedor} priorizado no Nível {p1.prioridade_atual} - {motivo}'
