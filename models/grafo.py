from typing import Dict, List, Any

class Grafo:
    '''
    Classe to TAD Grafo para sistema de triagem;
    '''
    
    def __init__(self):
        self._grafo: Dict[Any, Dict[Any, float]] = {}
        self._peso_node: Dict[Any, float] = {} # Peso dos nós;
        
    def add_ponto(self, ponto: Any, peso: float = 0.0) -> None:
        '''
        Adiciona um ponto ao grafo com um peso opcional;
        '''
        if ponto not in self._grafo:
            self._grafo[ponto] = {}
            self._peso_node[ponto] = peso
    
    def add_ponto_conexao(self, u: Any, v: Any, peso: float = 1.0) -> None:
        '''
        Adiciona uma conexão entre os pontos u e v com um peso opcional;
        '''
        self.add_ponto(u)
        self.add_ponto(v)
        
        self._grafo[u][v] = peso
        self._grafo[v][u] = peso  # Para grafos não direcionados
        
    def get_peso_node(self, node: Any) -> float:
        '''
        Retorna o peso base de um nó;
        '''
        
        return self. _peso_node.get(node, 0.0)
    
    def get_vizinhos(self, ponto: Any) -> List[Any]:
        '''
        Retorna os vizinhos de um ponto;
        '''
        
        if ponto in self._grafo:
            return list(self._grafo[ponto].keys())
        return []
    
    def get_pontos(self) -> List[Any]:
        '''
        Retorna todos os pontos do grafo;
        '''
        
        return list(self._grafo.keys())
    
    def __len__(self) -> int:
        '''
        Retorna o número de pontos no grafo;
        '''
        
        return len(self._grafo)
    
    def __contains__(self, ponto: Any) -> bool:
        '''
        Verifica se o ponnto está no gráfico;
        '''
        
        return ponto in self._grafo