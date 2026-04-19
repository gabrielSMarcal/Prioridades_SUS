from typing import Any, Dict, List, Optional
from datetime import datetime

from models.paciente import Paciente
from models.grafo import Grafo
from base_conhecimento import REGRAS_PRIMARIAS, REGRAS_SECUNDARIAS, GRAFO_URGENCIAS, SLA_TEMPOS

class MotorInferencia:
    '''
    Motor de inferência por encadeamento progressivo;
    '''
    
    def __init__(self):
        self.grafo = self._build_grafo_urgencias()
        self.logs = []
        
    def _build_grafo_urgencias(self) -> Grafo:
        '''
        Constrói o grado de urgência baseado na configuração;
        '''
        
        g = Grafo()
        
        for node, peso in GRAFO_URGENCIAS['nodes'].items():
            g.add_ponto(node, peso)
        for u, v, peso in GRAFO_URGENCIAS['edges']:
            g.add_ponto_conexao(u, v, peso)
            
        return g
    
    def log_inferencia(self, paciente_id: str, regra_id: str, conclusao: str, detalhes: str):
        '''
        Registra uma inferência no log auditável;
        '''
        
        self.logs.append({
            'hora': datetime.now().strftime('%H:%M:%S'),
            'paciente': paciente_id,
            'regra': regra_id,
            'conclusao': conclusao,
            'detalhes': detalhes
        })
        
    def rodar_inferencia(self, paciente: Paciente):
        '''
        Executa o ciclo de inferência para um paciente;
        '''
        
        #1. Avaliar regras primárias;
        self._validar_regras_primarias(paciente)
        
        #2. Avaliar regras secundárias (reclassificação);
        self._validar_regras_secundarias(paciente)
        
        #3. Aplicar Regra de Grupos Vulneráveis;
        self._aplicar_regra_vulneravel(paciente)
        
    def _validar_regras_primarias(self, paciente: Paciente):
        '''
        Avalia as regras primárias baseadas nos sinais vitais;
        '''
        
        leitura = paciente.get_ultima_leitura()
        
        if not leitura:
            return
        
        for regra in REGRAS_PRIMARIAS:
            
            match = self._condicoes_regras_check(leitura, regra)
            
            if match:
                paciente.atualizar_prioridade(regra['nivel'], regra['descricao'])
                self.log_inferencia(paciente.id, regra['id'], f'Nível {regra['nível']}', regra['descricao'])
                break  # Aplica a primeira regra que casar (maior prioridade)
            
    def _condicoes_regras_check(self, leitura: Dict[str, Any], regra: Dict[str, Any]) -> bool:
        '''
        Verifica se as condições de uma regra são atendidas;
        '''
        
        resultados = []
        for cond in regra['condicoes']:
            
            valor_paciente = leitura.get(cond['campo'])
            
            if valor_paciente is None:
                resultados.append(False)
                continue
            
            op = cond['op']
            valor_regra = cond['valor']
            
            # Aplicando valores operacionais (Apenas os que foram construidos)
            if op == '==':
                resultados.append(valor_paciente == valor_regra)
            elif op == '<':
                resultados.append(valor_paciente < valor_regra)
            elif op == '>':
                resultados.append(valor_paciente > valor_regra)
            elif op == '>=':
                resultados.append(valor_paciente >= valor_regra)
            elif op == 'range':
                resultados.append(valor_regra[0] <= valor_paciente <= valor_regra[1])
                
        if regra['operador_logico'] == 'OR':
            return any(resultados)
        
        return all(resultados)
    
    def _validar_regras_secundarias(self, paciente: Paciente):
        '''
        Avalia as regras de regras secundárias (Encadeamento);
        '''
        
        # E1: Reclassifgicação rápida de 3 para 2;
        if len(paciente.historico_classificacoes) >= 2:
            h = paciente.historico_classificacoes
            if h[-1]['nivel'] == 2 and h[-2]['nivel'] == 3:
                self.log_inferencia(paciente.id, 'E1', 'Evento Crítico', 'Reclassificação 3 -> 2 em curto intervalo')
                
                
        # E2: Piora simultânea de dois ou mais sinais vitais;
        if paciente.get_penultima_leitura():
            piora_cont = self._contagem_clinica_piora(paciente)
            if piora_cont >= 2:
                paciente.atualizar_prioridade(max(1, paciente.prioridade_atual - 1), 'Piora clínica simultânea')
                self.log_inferencia(paciente.id, 'E2', 'Elevação Prioridade', f'{piora_cont} sinais vitais em piora')
                
        # E4: Vulnerável + Temperatura subiu > 1ºC;
        if paciente.vuleravel and paciente.get_penultima_leitura():
            t_atual = paciente.get_ultima_leitura().get('temperatura', 0)
            t_anterior = paciente.get_penultima_leitura().get('temperatura', 0)
            if t_atual - t_anterior > 1.0:
                paciente.atualizar_prioridade(2, 'Vulnerável com febre súbita')
                self.log_inferencia(paciente.id, 'E4', 'Nível 2 Dirteto', 'Vulnerável com aumento de temperatura > 1ºC')
                
    def _contagem_clinica_piora(self, paciente: Paciente) -> int:
        '''
        Conta quantos sinais vitais pioraram entre as duas últimas leituras;
        '''
        
        l1 = paciente.get_ultima_leitura()
        l2 = paciente.get_penultima_leitura()
        cont = 0
        
        # SpO2 caiu
        if l2.get('spo2', 100) < l1.get('spo2', 100): cont += 1
        # Glasgow caiu
        if l2.get('glasgow', 15) < l1.get('glasgow', 15): cont += 1
        # Dor aumentou
        if l2.get('escala_dor', 0) > l1.get('escala_dor', 0): cont += 1
        # Temperatura subiu
        if l2.get('temperatura', 36) > l1.get('temperatura', 36): cont += 1
        
        return cont
        
        
    def _aplicar_regra_vulneravel(self, paciente: Paciente):
        '''
        Aplica a regra de grupos vulneráveis (Eleva 1 nível);
        '''
        
        if paciente.vuleravel and paciente.prioridade_atual > 1:
            # Eleva apenas se ainnda não foi elevado por essa regra ou a base cl´pinica mudou;
            paciente.atualizar_prioridade(paciente.prioridade_atual - 1, 'Grupo Vulnerável (Idade/Gestação/Deficiência)')
            self.log_inferencia(paciente.id, 'VULN', f'Nível {paciente.prioridade_atual}', 'Elevação por prioridade')
        