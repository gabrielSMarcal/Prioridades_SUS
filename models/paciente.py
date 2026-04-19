from typing import Any, Dict, List, Optional
from datetime import datetime

class Paciente:
    '''
    Classe de um paciente no sistema de triagem do SUS;
    '''
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', 'Desconecido')
        self.idade = data.get('idade', 0)
        self.gestante = data.get('gestante', False)
        self.deficiencia = data.get('deficiencia', False)
        self.hora_entrada = data.get('hora_entrada', datetime.now().strftime('%H:%M'))
        self.leituras = data.get('leituras', [])
        
        # Estado de classificação;
        self.prioridade_atual = 5  # Prioridade inicial (5 - Baixa, 1 - Alta)
        self.historico_classificacoes = []
        self.alertas = []
        self.vuleravel = self.idade >= 60 or self.gestante or self.deficiencia
        self.violacoes_sla = 0
        self.ultima_reclassificacao = None
    
    def get_ultima_leitura(self) -> Optional[Dict[str, Any]]:
        '''
        Retorna a leitura de sinais vitais mais recente;
        '''
        
        return self.leituras[-1] if self.leituras else None
    
    def get_penultima_leitura(self) -> Optional[Dict[str, Any]]:
        '''
        Retorna a penúltima leitura de sinais vitais;
        '''
        
        return self.leituras[-2] if len(self.leituras) >= 2 else None
    
    def add_leitura(self, leitura: Dict[str, Any]):
        '''
        Adiciona uma nova leitura de sinais vitais;
        '''
        
        self.leituras.append(leitura)
        
    def atualizar_prioridade(self, novo_nivel: int, motivo: str):
        '''
        Atualiza o nível de prioridade (Apenas elevação permitida automaticamente);
        '''
        
        if novo_nivel < self.prioridade_atual:
            self.prioridade_atual = novo_nivel
            self.ultima_reclassificacao = datetime.now().strftime('%H:%M')
            self.historico_classificacoes.append({
                'hora': self.ultima_reclassificacao,
                'nivel': novo_nivel,
                'motivo': motivo
            })
            
    def __repr__(self):
        return f'Paciente({self.id}), Prioridade: {self.prioridade_atual}, Vuleravel: {self.vuleravel})'
        
                
        
        
    