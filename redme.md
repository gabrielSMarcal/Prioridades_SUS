```markdown
# DOCUMENTAÇÃO DO SISTEMA DE PRIORIDADES SUS

## MANUS AI

## Resumo

Este documento apresenta uma análise detalhada do sistema de triagem inteligente para Unidades de Pronto Atendimento (UPAs) do Sistema Único de Saúde (SUS) no Brasil. Aborda a arquitetura modular do sistema, composta pelos módulos `models`, `engine` e `src`, e descreve o funcionamento de cada componente, incluindo a representação de pacientes, a estrutura de grafo para avaliação de sintomas, o motor de inferência baseado em regras primárias e secundárias, e o mecanismo de desempate. Além disso, detalha a interface de usuário via terminal, o ponto de entrada principal (`main.py`) com seu menu interativo, e os cenários de teste. Por fim, são fornecidas instruções claras sobre como configurar e executar o programa e seus testes, visando facilitar a compreensão e a utilização por desenvolvedores e usuários finais.

**Palavras-chave**: Triagem, SUS, Prioridade, Sistema de Regras, Python, UPA.

## Sumário

1 INTRODUÇÃO
2 ARQUITETURA DO SISTEMA
  2.1 MÓDULO `models`
    2.1.1 `paciente.py`
    2.1.2 `grafo.py`
  2.2 MÓDULO `engine`
    2.2.1 `base_conhecimento.py`
    2.2.2 `motor_inferencia.py`
    2.2.3 `empate_breaker.py`
  2.3 MÓDULO `src`
    2.3.1 `sistema_triagem.py`
    2.3.2 `interface_usuario.py`
3 PONTO DE ENTRADA (`main.py`)
4 TESTES (`tests`)
5 COMO RODAR O PROGRAMA
  5.1 PRÉ-REQUISITOS
  5.2 EXECUÇÃO DO PROGRAMA PRINCIPAL
  5.3 EXECUÇÃO DOS TESTES
6 FUNCIONAMENTO DO MENU
7 CONCLUSÃO


## 1 INTRODUÇÃO

Este documento detalha a arquitetura, o funcionamento e as instruções de uso do sistema de triagem inteligente para Unidades de Pronto Atendimento (UPAs) do Sistema Único de Saúde (SUS) no Brasil. O sistema visa otimizar a classificação de pacientes com base em sinais vitais, histórico e regras de negócio, utilizando um motor de inferência e critérios de desempate para garantir a priorização adequada.

## 2 ARQUITETURA DO SISTEMA

O sistema é modular, dividido em `models`, `engine` e `src`, com um ponto de entrada principal (`main.py`) e módulos de teste (`tests`).

### 2.1 MÓDULO `models`

O módulo `models` define as estruturas de dados fundamentais para o sistema.

#### 2.1.1 `paciente.py`

Define a classe `Paciente`, que representa um indivíduo no sistema de triagem. Armazena informações como ID, idade, status de gestante ou deficiente, hora de entrada, leituras de sinais vitais, prioridade atual, histórico de classificações e alertas. Inclui métodos para adicionar leituras, obter leituras recentes e atualizar a prioridade do paciente.

#### 2.1.2 `grafo.py`

Implementa um Tipo Abstrato de Dados (TAD) `Grafo`, utilizado pelo motor de inferência para calcular pesos e conexões entre sintomas. Permite adicionar nós (sintomas) com pesos e arestas (conexões) entre eles, facilitando a avaliação complexa de múltiplos fatores.

### 2.2 MÓDULO `engine`

O módulo `engine` contém a lógica central de inferência e desempate.

#### 2.2.1 `base_conhecimento.py`

Armazena as regras de negócio do sistema:

*   **`REGRAS_PRIMARIAS`**: Regras de classificação inicial baseadas nos protocolos de Manchester, associando sinais vitais e sintomas a níveis de prioridade e nós do grafo.
*   **`REGRAS_SECUNDARIAS`**: Regras dinâmicas de segunda ordem que ajustam a prioridade com base em evolução clínica, violação de SLA, e condições específicas de vulnerabilidade.
*   **`GRAFO_URGENCIAS`**: Configuração do grafo com nós (sintomas) e seus pesos, além das arestas (conexões) e seus bônus/penalidades.
*   **`SLA_TEMPOS`**: Tempos máximos de espera permitidos para cada nível de prioridade (SLA - Service Level Agreement).

#### 2.2.2 `motor_inferencia.py`

Implementa o `MotorInferencia`, que utiliza um encadeamento progressivo (Forward Chaining) para aplicar as regras de triagem. Ele executa os seguintes passos:

1.  **Regras Primárias**: Avalia as condições da `REGRAS_PRIMARIAS` com base na última leitura do paciente e calcula a prioridade inicial usando o `Grafo`.
2.  **Regras Secundárias**: Aplica as `REGRAS_SECUNDARIAS` para refinar a prioridade, considerando fatores como piora clínica, tempo de espera e vulnerabilidade.
3.  **Regra de Vulnerabilidade**: Eleva a prioridade de pacientes vulneráveis (idosos, gestantes, pessoas com deficiência) conforme a legislação.

O motor também mantém um log auditável de todas as inferências realizadas.

#### 2.2.3 `empate_breaker.py`

Define a classe `EmpateBreaker`, responsável por resolver empates entre pacientes com o mesmo nível de prioridade. Calcula uma pontuação de instabilidade (SI) para cada paciente, considerando:

*   **Fator de Espera**: Tempo de espera em relação ao SLA do nível.
*   **Fator de Tendência**: Piora de sinais vitais entre leituras.
*   **Fator de Vulnerabilidade**: Multiplicador para pacientes vulneráveis.

Pacientes com maior pontuação de instabilidade são priorizados.

### 2.3 MÓDULO `src`

O módulo `src` contém a lógica de orquestração e a interface com o usuário.

#### 2.3.1 `sistema_triagem.py`

Define a classe `SistemaTriagem`, que atua como o orquestrador principal. Inicializa o `Grafo`, o `MotorInferencia` e o `EmpateBreaker`. Gerencia a lista de pacientes, adiciona novos pacientes, atualiza sinais vitais e aciona o motor de inferência. Possui métodos para obter a fila de atendimento ordenada (`get_fila`) e exibir a fila e os logs de inferência (`exibe_fila`, `exibe_log`).

#### 2.3.2 `interface_usuario.py`

Contém as funções para interação com o usuário via terminal. Inclui:

*   `cor_prioridade`: Mapeia níveis de prioridade para cores (Vermelho, Laranja, Amarelo, etc.).
*   `obter_leitura_manual`: Coleta sinais vitais do paciente (Glasgow, SpO2, FC, Temperatura, Dor, Vômitos).
*   `acao_cadastrar_paciente`: Guia o usuário no cadastro de um novo paciente.
*   `acao_atualizar_vituais`: Permite atualizar os sinais vitais de um paciente existente.
*   `acao_exibir_fila`: Exibe a fila de atendimento atual.
*   `acao_exibir_logs`: Exibe o histórico de inferências.

## 3 PONTO DE ENTRADA (`main.py`)

O arquivo `main.py` é o ponto de entrada do sistema. Ele inicializa o `SistemaTriagem`, cadastra alguns pacientes iniciais com dados de exemplo e apresenta um menu interativo ao usuário. O menu permite:

1.  Visualizar Fila de Atendimento
2.  Cadastrar Novo Paciente
3.  Atualizar Sinais Vitais de um Paciente
4.  Ver Logs de Inferência
0.  Sair

## 4 TESTES (`tests`)

O diretório `tests` contém o arquivo `teste_cenarios.py`, que simula diversos cenários de pacientes para validar o funcionamento do motor de inferência e do desempate. Ele demonstra como as regras primárias e secundárias afetam a prioridade dos pacientes em situações específicas, como piora clínica, vulnerabilidade e violação de SLA.

## 5 COMO RODAR O PROGRAMA

O projeto inclui scripts `.bat` para facilitar a execução em ambientes Windows. Recomenda-se o uso de um ambiente virtual Python.

### 5.1 PRÉ-REQUISITOS

*   Python 3.x instalado.

### 5.2 EXECUÇÃO DO PROGRAMA PRINCIPAL

1.  **Navegue até o diretório do projeto:**
    ```bash
    cd Prioridades_SUS
    ```
2.  **Execute o script `main.bat` (Windows):**
    ```bash
    main.bat
    ```
    Este script irá criar um ambiente virtual (se necessário), instalar as dependências e executar o `main.py`, que iniciará o menu interativo.

3.  **Para outros sistemas operacionais (Linux/macOS) ou execução manual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # Não há dependências externas listadas, mas se houvesse, seriam instaladas aqui
    # pip install -r requirements.txt
    python main.py
    ```

### 5.3 EXECUÇÃO DOS TESTES

1.  **Navegue até o diretório do projeto:**
    ```bash
    cd Prioridades_SUS
    ```
2.  **Execute o script `testes.bat` (Windows):**
    ```bash
    testes.bat
    ```
    Este script fará o mesmo processo de ambiente virtual e executará o `teste_cenarios.py`, mostrando os resultados dos testes.

3.  **Para outros sistemas operacionais (Linux/macOS) ou execução manual:**
    ```bash
    source .venv/bin/activate # Ative o ambiente virtual se ainda não estiver ativo
    python tests/teste_cenarios.py
    ```

## 6 FUNCIONAMENTO DO MENU

Ao iniciar o `main.py`, o usuário será apresentado a um menu de opções:

```
============================================================
           MENU DE TRIAGEM INTELIGENTE - UPA SUS           
============================================================
 1. Visualizar Fila de Atendimento
 2. Cadastrar Novo Paciente
 3. Atualizar Sinais Vitais de um Paciente
 4. Ver Logs de Inferência
 0. Sair
============================================================
Escolha uma opção: 
```

*   **1. Visualizar Fila de Atendimento**: Exibe a lista de pacientes ordenados por prioridade (do mais urgente ao menos urgente). Pacientes com a mesma prioridade são desempatados pelo `EmpateBreaker`.
*   **2. Cadastrar Novo Paciente**: Solicita o nome, idade, se é gestante e se possui deficiência. Em seguida, pede os sinais vitais iniciais. O sistema adiciona o paciente e realiza a triagem automaticamente.
*   **3. Atualizar Sinais Vitais de um Paciente**: Lista os pacientes cadastrados. O usuário seleciona um paciente e insere novos sinais vitais. O sistema reavalia a prioridade do paciente com base nas novas informações.
*   **4. Ver Logs de Inferência**: Mostra um registro detalhado de todas as decisões de triagem tomadas pelo motor de inferência, incluindo qual regra foi aplicada e a conclusão.
*   **0. Sair**: Encerra o programa.

## 7 CONCLUSÃO

O sistema de Prioridades SUS é uma ferramenta robusta para auxiliar na triagem de pacientes em UPAs, combinando regras clínicas, lógica de grafo e critérios de desempate para garantir um atendimento eficiente e justo. Sua modularidade facilita a manutenção e a expansão de suas funcionalidades.
```
