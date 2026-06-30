import json
from .processo import Processo

# 1. A sua estrutura de dados
# 2. O motor do simulador (aqui entra a lógica que discutimos antes)
def escalonamento_edf(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO EDF ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    # Cópia ordenada pelo tempo de chegada
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        # 1. Verifica quem chegou neste exato "tick" de tempo
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            fila_prontos.append(novo)
            ##print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} chegou no sistema.")

        # 2. Lidando com a Sobrecarga de Contexto em andamento
        if tempo_sobrecarga > 0:
            ##print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue 

        # 3. Lógica de Preempção do EDF
        if fila_prontos:
            # CORREÇÃO: Ordenação em cascata (Menor Deadline -> Maior Prioridade numérica -> Chegada mais antiga)
            fila_prontos.sort(key=lambda p: (p.deadline, p.prioridade, p.chegada))
            
            # Avalia se a CPU está livre ou se há um deadline ESTRITAMENTE menor
            if processo_atual is None or fila_prontos[0].deadline < processo_atual.deadline:
                
                if processo_atual is not None:
                    ##print(f"[Tempo {tempo_atual}] PREEMPÇÃO: {processo_atual.id} interrompido por {fila_prontos[0].id}.")
                    fila_prontos.append(processo_atual)
                    # Reordena a fila após devolver o processo atual
                    fila_prontos.sort(key=lambda p: (p.deadline, p.prioridade, p.chegada))
                
                proximo_processo = fila_prontos.pop(0)
                
                # Aplica a sobrecarga APENAS se houver troca real de IDs
                if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                    tempo_sobrecarga = sobrecarga_contexto
                    processo_atual = proximo_processo
                    
                    if tempo_sobrecarga > 0:
                        ##print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                        tempo_sobrecarga -= 1
                        tempo_atual += 1
                        continue
                
                processo_atual = proximo_processo
                if processo_atual.inicio == -1:
                    processo_atual.inicio = tempo_atual

        # 4. Execução da Unidade de Tempo
        if processo_atual is not None:
            ##print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante}, deadline: {processo_atual.deadline})")
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            # Verifica se finalizou a tarefa
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                ##print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou sua execução.")
                processo_atual = None
        else:
            ##print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            # CORREÇÃO CRÍTICA: Limpa o último ID. Sair da ociosidade não cobra troca de contexto!
            ultimo_processo_id = None
            
        # 5. Avança o relógio
        tempo_atual += 1
    gerar_tabela_metricas(lista_processos, "EDF")
        

def escalonamento_fifo(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO FIFO ---")
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        # 1. Chegadas
        while processos_nao_chegados and processos_nao_chegados[0].chegada <= tempo_atual:
            fila_prontos.append(processos_nao_chegados.pop(0))

        # 2. Sobrecarga de Contexto
        if tempo_sobrecarga > 0:
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue

        # 3. Escalonamento (Não Preemptivo)
        if processo_atual is None and fila_prontos:
            # FIFO: Pega simplesmente o primeiro da fila (já estão em ordem de chegada)
            proximo_processo = fila_prontos.pop(0)
            
            if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                tempo_sobrecarga = sobrecarga_contexto
                processo_atual = proximo_processo
                if tempo_sobrecarga > 0:
                    tempo_sobrecarga -= 1
                    tempo_atual += 1
                    continue
            
            processo_atual = proximo_processo
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual

        # 4. Execução
        if processo_atual is not None:
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                processo_atual = None
        else:
            ultimo_processo_id = None # CPU ociosa limpa o último ID
            
        tempo_atual += 1
        
    gerar_tabela_metricas(lista_processos, "FIFO")


def escalonamento_sjf(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO SJF ---")
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        # 1. Chegadas
        while processos_nao_chegados and processos_nao_chegados[0].chegada <= tempo_atual:
            fila_prontos.append(processos_nao_chegados.pop(0))

        # 2. Sobrecarga de Contexto
        if tempo_sobrecarga > 0:
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue

        # 3. Escalonamento (Não Preemptivo)
        if processo_atual is None and fila_prontos:
            # SJF: Ordena a fila pelo menor tempo de execução total.
            # Desempate: ordem de chegada.
            fila_prontos.sort(key=lambda p: (p.execucao, p.chegada))
            proximo_processo = fila_prontos.pop(0)
            
            if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                tempo_sobrecarga = sobrecarga_contexto
                processo_atual = proximo_processo
                if tempo_sobrecarga > 0:
                    tempo_sobrecarga -= 1
                    tempo_atual += 1
                    continue
            
            processo_atual = proximo_processo
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual

        # 4. Execução
        if processo_atual is not None:
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                processo_atual = None
        else:
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    gerar_tabela_metricas(lista_processos, "SJF")


# Adicionei esta função auxiliar para evitar repetição de código nas tabelas finais!
def gerar_tabela_metricas(lista_processos, nome_algoritmo):
    print(f"\n--- RESUMO DE MÉTRICAS {nome_algoritmo} ---")
    soma_turnaround = 0
    soma_espera = 0
    
    for p in sorted(lista_processos, key=lambda x: str(x.id)):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        soma_turnaround += turnaround
        soma_espera += espera

    quantidade = len(lista_processos)
    if quantidade > 0:
        print(f"Tempo Médio de Turnaround: {(soma_turnaround / quantidade):.2f}")
        print(f"Tempo Médio de Espera: {(soma_espera / quantidade):.2f}")
    print("-" * 65 + "\n")

def escalonamento_cfs(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO CFS-SIM ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    # Cópia ordenada pelo tempo de chegada
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    # Injeção dinâmica do atributo 'vruntime' caso a classe original não o tenha
    for p in lista_processos:
        p.vruntime = 0.0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        # 1. Verifica quem chegou neste exato "tick" de tempo
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            # REGRA DO CFS: Quando um processo chega, vruntime = tempo_atual
            novo.vruntime = float(tempo_atual)
            fila_prontos.append(novo)
            ##print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} entrou na fila com vruntime inicial: {novo.vruntime:.2f}")

        # 2. Lidando com a Sobrecarga de Contexto
        if tempo_sobrecarga > 0:
            ##print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue 

        # 3. Lógica de Preempção do CFS
        if fila_prontos:
            # A ORDENAÇÃO DO CFS: Sempre o menor vruntime. 
            # Desempate: prioridade, depois ordem de chegada.
            fila_prontos.sort(key=lambda p: (p.vruntime, p.prioridade, p.chegada))
            
            # Se a CPU está livre ou o processo na fila tem um vruntime MENOR
            if processo_atual is None or fila_prontos[0].vruntime < processo_atual.vruntime:
                
                if processo_atual is not None:
                    ##print(f"[Tempo {tempo_atual}] PREEMPÇÃO: {processo_atual.id} (vruntime {processo_atual.vruntime:.2f}) interrompido por {fila_prontos[0].id} (vruntime {fila_prontos[0].vruntime:.2f}).")
                    fila_prontos.append(processo_atual)
                    fila_prontos.sort(key=lambda p: (p.vruntime, p.prioridade, p.chegada))
                
                proximo_processo = fila_prontos.pop(0)
                
                # Aplica sobrecarga de contexto para troca de processos
                if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                    tempo_sobrecarga = sobrecarga_contexto
                    processo_atual = proximo_processo
                    
                    if tempo_sobrecarga > 0:
                        ##print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                        tempo_sobrecarga -= 1
                        tempo_atual += 1
                        continue
                
                processo_atual = proximo_processo
                if processo_atual.inicio == -1:
                    processo_atual.inicio = tempo_atual

        # 4. Execução da Unidade de Tempo e Atualização do vruntime
        if processo_atual is not None:
            # Cálculo matemático do peso da prioridade segundo a regra do trabalho
            peso = 1.25 ** (processo_atual.prioridade - 1)
            
            ##print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante}, vruntime: {processo_atual.vruntime:.2f})")
            
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            # ATUALIZAÇÃO DO VRUNTIME (Delta t = 1, pois avançamos tick a tick)
            processo_atual.vruntime += (1 * peso)
            
            # Verifica se finalizou a tarefa
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                ##print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou (vruntime final: {processo_atual.vruntime:.2f}).")
                processo_atual = None
        else:
            ##print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        # 5. Avança o relógio
        tempo_atual += 1

    gerar_tabela_metricas(lista_processos, "CFS")       