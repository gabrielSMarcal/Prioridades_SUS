from typing import Dict, Any
from datetime import datetime
from models.paciente import Paciente
from .base_conhecimento import REGRAS_PRIMARIAS, REGRAS_SECUNDARIAS, SLA_TEMPOS

class MotorInferencia:
    '''
    Motor de Inferência por Encadeamento Progressivo (Forward Chaining);
    '''
    
    def __init__(self):
        self.logs = []
        # Mapeamento de tipos de regras secundárias para métodos internos;
        self._mapa_regras_secundarias = {
            'temporal': self._regra_temporal_e1,
            'piora_clinica': self._regra_piora_clinica_e2,
            'sla': self._regra_sla_e3,
            'vulneravel_piora': self._regra_vulneravel_piora_e4,
            'sobrecarga': self._regra_sobrecarga_e5
        }
        
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
        Executa o ciclo de inferência completo para um paciente;
        '''
        # 1. Aplica Regras Primárias (Manchester Base);
        self._aplicar_regras_primarias(paciente)
        
        # 2. Aplica Regras Secundárias (Dinamicamente da Base de Conhecimento);
        self._aplicar_regras_secundarias(paciente)
        
        # 3. Aplica Regra de Vulnerabilidade (Elevação por prioridade legal);
        self._aplicar_regra_vulneravel(paciente)
        
    def _aplicar_regras_primarias(self, paciente: Paciente):
        '''
        Avalia as regras primárias baseadas na última leitura;
        '''
        leitura = paciente.get_ultima_leitura()
        if not leitura:
            return
            
        for regra in REGRAS_PRIMARIAS:
            match = self._condicoes_regras_check(leitura, regra)
            
            if match:
                paciente.atualizar_prioridade(regra['nivel'], regra['descricao'])
                self.log_inferencia(paciente.id, regra['id'], f"Nível {regra['nivel']}", regra['descricao'])
                break  # Aplica a primeira regra que casar (maior prioridade)
            
    def _condicoes_regras_check(self, leitura: Dict[str, Any], regra: Dict[str, Any]) -> bool:
        '''
        Valida se as condições de uma regra são atendidas pela leitura;
        '''
        condicoes = regra['condicoes']
        operador = regra.get('operador_logico', 'AND')
        
        resultados = []
        for c in condicoes:
            valor_paciente = leitura.get(c['campo'])
            if valor_paciente is None:
                resultados.append(False)
                continue
                
            res = False
            op = c['op']
            v_ref = c['valor']
            
            if op == '==': res = (valor_paciente == v_ref)
            elif op == '>': res = (valor_paciente > v_ref)
            elif op == '<': res = (valor_paciente < v_ref)
            elif op == '>=': res = (valor_paciente >= v_ref)
            elif op == '<=': res = (valor_paciente <= v_ref)
            elif op == 'range': res = (v_ref[0] <= valor_paciente <= v_ref[1])
            
            resultados.append(res)
            
        if operador == 'AND':
            return all(resultados)
        else:
            return any(resultados)

    def _aplicar_regras_secundarias(self, paciente: Paciente):
        '''
        Percorre as REGRAS_SECUNDARIAS da base de conhecimento e executa seus métodos;
        '''
        for regra in REGRAS_SECUNDARIAS:
            tipo = regra.get('tipo')
            metodo = self._mapa_regras_secundarias.get(tipo)
            if metodo:
                metodo(paciente, regra)

    # --- Implementação dos Métodos de Regras Secundárias ---

    def _regra_temporal_e1(self, paciente: Paciente, regra: Dict[str, Any]):
        '''
        E1: Reclassificação rápida de 3 para 2 se houver instabilidade;
        '''
        if paciente.prioridade_atual == 3 and len(paciente.leituras) >= 2:
            l1 = paciente.get_penultima_leitura()
            l2 = paciente.get_ultima_leitura()
            # Se a dor aumentou significativamente ou SpO2 caiu no nível 3;
            if l2.get('escala_dor', 0) > l1.get('escala_dor', 0) or l2.get('spo2', 100) < l1.get('spo2', 100):
                paciente.atualizar_prioridade(2, regra['descricao'])
                self.log_inferencia(paciente.id, regra['id'], 'Elevação Prioridade', regra['descricao'])

    def _regra_piora_clinica_e2(self, paciente: Paciente, regra: Dict[str, Any]):
        '''
        E2: Piora simultânea de dois ou mais sinais vitais;
        '''
        if len(paciente.leituras) < 2:
            return
            
        l1 = paciente.get_penultima_leitura()
        l2 = paciente.get_ultima_leitura()
        cont = 0
        
        if l2.get('spo2', 100) < l1.get('spo2', 100): cont += 1
        if l2.get('glasgow', 15) < l1.get('glasgow', 15): cont += 1
        if l2.get('escala_dor', 0) > l1.get('escala_dor', 0): cont += 1
        if l2.get('frequencia_cardiaca', 80) != l1.get('frequencia_cardiaca', 80): cont += 1
        
        if cont >= 2:
            paciente.atualizar_prioridade(max(1, paciente.prioridade_atual - 1), regra['descricao'])
            self.log_inferencia(paciente.id, regra['id'], 'Elevação Prioridade', f"{cont} sinais em piora")

    def _regra_sla_e3(self, paciente: Paciente, regra: Dict[str, Any]):
        '''
        E3: Violação de SLA do nível atual;
        '''
        if not paciente.get_ultima_leitura():
            return

        try:
            h_entrada = datetime.strptime(paciente.hora_entrada, '%H:%M')
            h_atual = datetime.strptime(paciente.get_ultima_leitura()['hora'], '%H:%M')
            espera = (h_atual - h_entrada).total_seconds() / 60
            
            sla_maximo = SLA_TEMPOS.get(paciente.prioridade_atual, 120)
            
            if espera > sla_maximo:
                paciente.violacoes_sla += 1
                self.log_inferencia(paciente.id, regra['id'], 'Alerta de Violação', f"Espera: {int(espera)} min (SLA: {sla_maximo} min)")
        except:
            pass

    def _regra_vulneravel_piora_e4(self, paciente: Paciente, regra: Dict[str, Any]):
        '''
        E4: Vulnerável com aumento de temperatura > 1ºC;
        '''
        if paciente.vuleravel and len(paciente.leituras) >= 2:
            l1 = paciente.get_penultima_leitura()
            l2 = paciente.get_ultima_leitura()
            t_atual = l2.get('temperatura', 0)
            t_anterior = l1.get('temperatura', 0)
            
            if t_atual - t_anterior > 1.0:
                paciente.atualizar_prioridade(2, regra['descricao'])
                self.log_inferencia(paciente.id, regra['id'], 'Nível 2 Direto', regra['descricao'])

    def _regra_sobrecarga_e5(self, paciente: Paciente, regra: Dict[str, Any]):
        '''
        E5: Dupla violação de SLA;
        '''
        if paciente.violacoes_sla >= 2:
            self.log_inferencia(paciente.id, regra['id'], 'Protocolo Sobrecarga', regra['descricao'])

    def _aplicar_regra_vulneravel(self, paciente: Paciente):
        '''
        Aplica a regra de grupos vulneráveis (Eleva 1 nível);
        '''
        if paciente.vuleravel and paciente.prioridade_atual > 1:
            paciente.atualizar_prioridade(paciente.prioridade_atual - 1, 'Grupo Vulnerável (Idade/Gestação/Deficiência)')
            self.log_inferencia(paciente.id, 'VULN', f"Nível {paciente.prioridade_atual}", 'Elevação por prioridade legal')
