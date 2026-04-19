from typing import Any, Dict, List
from datetime import datetime

from models.paciente import Paciente
from .base_conhecimento import SLA_TEMPOS

class EmpateBreaker:
    '''
    Classe que implemente o critério de desempate
    para pacientes no mesmo nível de prioridade;
    '''
    
    def __init__(self):
        pass
    
    def resolve_empate(self, pacientes: List[Paciente]) -> List[Paciente]:
        '''
        Ordena uma lista de pacientes no mesmo nível de prioridade;
        Critério: Score de Instavilidade (SI)
        SI = (Peso do Grado) * (Tempo de Espera) * (Fator de Tendência)
        '''
        
        if not pacientes:
            return []
        
        # Ordenna por prioridade (1 é mais urgente) e depois pelo scorre de desempate;
        # Como o método recebe pacientes do mesmo nível, focamos no score (Ponto);
        
        pontuacao_paciente = []
        for p in pacientes:
            ponto = self._calcular_pontuacao_instabilidade(p)
            pontuacao_paciente.append((p, ponto))
            
        # Ordena por pontuação (maior pontuação = mais urgente);
        pontuacao_paciente.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, s in pontuacao_paciente]
    
    def _calcular_pontuacao_instabilidade(self, paciente: Paciente) -> float:
        '''
        Calcula o score de instabvilidade para desempate;
        '''
        
        # 1. Fator de Tempo de Espera (minutos desde a entrada);
        # Para fins de simulação, usamos a diferença entre a hora da última leitura e a entrada;
        # Se não houver leitura, usamos a hora atual;
        
        try:
            h_entrada = datetime.strptime(paciente.hora_entrada, '%H:%M')
            h_atual = datetime.strptime(paciente.get_ultima_leitura()['hora'], '%H:%M') if paciente.get_ultima_leitura() else h_entrada 
            espera = (h_atual - h_entrada).total_seconds() / 60  # Tempo de espera em minutos
        except:
            espera = 0
            
        # 2. Fator de Tendência (piora clínica);
        
        tendencia = 1.0
        if len(paciente.leituras) >= 2:
            l1 = paciente.get_ultima_leitura()
            l2 = paciente.get_penultima_leitura()
            # Se sinais vitais pioram, aumenta o fator
            if l2.get('spo2', 100) < l1.get('spo2', 100): tendencia += 0.5
            if l2.get('escala_dor', 0) > l1.get('escala_dor', 0): tendencia += 0.3
            if l2.get('glasgow', 15) < l1.get('glasgow', 15): tendencia += 0.4
            
        # 3. Fator de Vulnerabilidade;
        vulnetabilidade = 1.2 if paciente.vuleravel else 1.0
        
        # Score Final (Quando maior o score, maior a prioridade de desempate);
        return (espera + 1) * tendencia * vulnetabilidade  # +1 para evitar multiplicação por zero
    
    def get_audit_log(self, p1: Paciente, p2: Paciente) -> str:
        '''
        Gera uma explicação legível para o desempate
        '''
        
        s1 = self._calcular_pontuacao_instabilidade(p1)
        s2 = self._calcular_pontuacao_instabilidade(p2)
        
        vencedor = p1.id if s1 > s2 else p2.id
        motivo = ''
        
        if p1.vuleravel != p2.vuleravel:
            motivo = 'Devido à condição de vulnerabilidade (Idade / Gestação / Deficiência)'
        elif len(p1.leituras) != len(p2.leituras) or s1 != s2:
            motivo = 'Devido à maior instabilidade clínica detectada nas últimas leituras'
        else:
            motivo = 'Devido a maior tempo de espera na unidade'
            
        return f'Paciente {vencedor} priorizado sobre o outro no Níivel {p1.prioridade_atual} - {motivo}'
        