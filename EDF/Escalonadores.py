import json
from processo import Processo

# ==============================================================================
# 1. ALGORITMO ORIGINAL: EARLIEST DEADLINE FIRST (EDF)
# ==============================================================================
def escalonamento_edf(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO EDF ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            fila_prontos.append(novo)
            print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} chegou no sistema.")

        if tempo_sobrecarga > 0:
            print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue

        if fila_prontos:
            fila_prontos.sort(key=lambda p: (p.deadline, p.prioridade, p.chegada))
            
            if processo_atual is None or fila_prontos[0].deadline < processo_atual.deadline:
                
                if processo_atual is not None:
                    print(f"[Tempo {tempo_atual}] PREEMPÇÃO: {processo_atual.id} interrompido por {fila_prontos[0].id}.")
                    fila_prontos.append(processo_atual)
                    fila_prontos.sort(key=lambda p: (p.deadline, p.prioridade, p.chegada))
                
                proximo_processo = fila_prontos.pop(0)
                
                if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                    tempo_sobrecarga = sobrecarga_contexto
                    processo_atual = proximo_processo
        
                    if tempo_sobrecarga > 0:
                        print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                        tempo_sobrecarga -= 1
                        tempo_atual += 1
                        continue
                
                processo_atual = proximo_processo
                if processo_atual.inicio == -1:
                    processo_atual.inicio = tempo_atual

        if processo_atual is not None:
            print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante}, deadline: {processo_atual.deadline})")
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
         
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou sua execução.")
                processo_atual = None
        else:
            print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    print("\n--- SIMULAÇÃO EDF CONCLUÍDA ---")
    
    print("\n--- RESUMO DE MÉTRICAS (TABELA FINAL) ---")
    soma_turnaround = 0
    soma_espera = 0
    
    print(f"{'ID':<5} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7} | {'Deadline OK?':<12}")
    print("-" * 65)

    for p in sorted(lista_processos, key=lambda x: x.id):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        estourou = p.termino > p.deadline
        status_deadline = "ESTOUROU" if estourou else "OK"
        
        soma_turnaround += turnaround
        soma_espera += espera

        print(f"{p.id:<5} | {p.chegada:<8} | {p.termino:<8} | {turnaround:<11} | {espera:<7} | {status_deadline:<12}")

    quantidade = len(lista_processos)
    media_turnaround = soma_turnaround / quantidade
    media_espera = soma_espera / quantidade
    
    print("-" * 65)
    print(f"Tempo Médio de Turnaround: {media_turnaround:.2f}")
    print(f"Tempo Médio de Espera: {media_espera:.2f}")
    print("-----------------------------------------\n")


# ==============================================================================
# 2. ALGORITMO ORIGINAL: COMPLETELY FAIR SCHEDULER SIMPLIFICADO (CFS-SIM)
# ==============================================================================
def escalonamento_cfs(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO CFS-SIM ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    for p in lista_processos:
        p.vruntime = 0.0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            novo.vruntime = float(tempo_atual)
            fila_prontos.append(novo)
            print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} entrou na fila com vruntime inicial: {novo.vruntime:.2f}")

        if tempo_sobrecarga > 0:
            print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue

        if fila_prontos:
            fila_prontos.sort(key=lambda p: (p.vruntime, p.prioridade, p.chegada))
            
            if processo_atual is None or fila_prontos[0].vruntime < processo_atual.vruntime:
                
                if processo_atual is not None:
                    print(f"[Tempo {tempo_atual}] PREEMPÇÃO: {processo_atual.id} (vruntime {processo_atual.vruntime:.2f}) interrompido por {fila_prontos[0].id} (vruntime {fila_prontos[0].vruntime:.2f}).")
                    fila_prontos.append(processo_atual)
                    fila_prontos.sort(key=lambda p: (p.vruntime, p.prioridade, p.chegada))
                
                proximo_processo = fila_prontos.pop(0)
                
                if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                    tempo_sobrecarga = sobrecarga_contexto
                    processo_atual = proximo_processo
                    
                    if tempo_sobrecarga > 0:
                        print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                        tempo_sobrecarga -= 1
                        tempo_atual += 1
                        continue
                
                processo_atual = proximo_processo
                if processo_atual.inicio == -1:
                    processo_atual.inicio = tempo_atual

        if processo_atual is not None:
            peso = 1.25 ** (processo_atual.prioridade - 1)
            print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante}, vruntime: {processo_atual.vruntime:.2f})")
            
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            processo_atual.vruntime += (1 * peso)
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou (vruntime final: {processo_atual.vruntime:.2f}).")
                processo_atual = None
        else:
            print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    print("\n--- SIMULAÇÃO CONCLUÍDA ---")
    
    print("\n--- RESUMO DE MÉTRICAS CFS-SIM ---")
    soma_turnaround = 0
    soma_espera = 0
    
    print(f"{'ID':<5} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7} | {'Deadline OK?':<12}")
    print("-" * 65)

    for p in sorted(lista_processos, key=lambda x: x.id):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        estourou = p.termino > p.deadline
        status_deadline = "ESTOUROU" if estourou else "OK"
        
        soma_turnaround += turnaround
        soma_espera += espera

        print(f"{p.id:<5} | {p.chegada:<8} | {p.termino:<8} | {turnaround:<11} | {espera:<7} | {status_deadline:<12}")

    quantidade = len(lista_processos)
    media_turnaround = soma_turnaround / quantidade
    media_espera = soma_espera / quantidade
    
    print("-" * 65)
    print(f"Tempo Médio de Turnaround: {media_turnaround:.2f}")
    print(f"Tempo Médio de Espera: {media_espera:.2f}")
    print("-----------------------------------------\n")


# ==============================================================================
# 3. NOVO: FIRST COME, FIRST SERVED (FIFO / FCFS) - NÃO PREEMPTIVO
# ==============================================================================
def escalonamento_fifo(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO FIFO/FCFS ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            fila_prontos.append(novo)
            print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} chegou no sistema.")

        if tempo_sobrecarga > 0:
            print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue 

        if processo_atual is None and fila_prontos:
            proximo_processo = fila_prontos.pop(0)
            
            if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                tempo_sobrecarga = sobrecarga_contexto
                processo_atual = proximo_processo
                
                if tempo_sobrecarga > 0:
                    print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                    tempo_sobrecarga -= 1
                    tempo_atual += 1
                    continue
            
            processo_atual = proximo_processo
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual

        if processo_atual is not None:
            print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante})")
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou sua execução.")
                processo_atual = None
        else:
            print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    print("\n--- SIMULAÇÃO FIFO/FCFS CONCLUÍDA ---")
    
    print("\n--- RESUMO DE MÉTRICAS FIFO/FCFS ---")
    soma_turnaround = 0
    soma_espera = 0
    print(f"{'ID':<5} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7} | {'Deadline OK?':<12}")
    print("-" * 65)
    for p in sorted(lista_processos, key=lambda x: x.id):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        estourou = p.termino > p.deadline
        status_deadline = "ESTOUROU" if estourou else "OK"
        soma_turnaround += turnaround
        soma_espera += espera
        print(f"{p.id:<5} | {p.chegada:<8} | {p.termino:<8} | {turnaround:<11} | {espera:<7} | {status_deadline:<12}")

    quantidade = len(lista_processos)
    media_turnaround = soma_turnaround / quantidade if quantidade > 0 else 0
    media_espera = soma_espera / quantidade if quantidade > 0 else 0
    print("-" * 65)
    print(f"Tempo Médio de Turnaround: {media_turnaround:.2f}")
    print(f"Tempo Médio de Espera: {media_espera:.2f}")
    print("-----------------------------------------\n")


# ==============================================================================
# 4. NOVO: SHORTEST JOB FIRST (SJF) - NÃO PREEMPTIVO
# ==============================================================================
def escalonamento_sjf(lista_processos, sobrecarga_contexto):
    print("--- INICIANDO SIMULAÇÃO SJF ---")
    print(f"Sobrecarga de Contexto configurada: {sobrecarga_contexto}\n")
    
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            fila_prontos.append(novo)
            print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} chegou no sistema.")

        if tempo_sobrecarga > 0:
            print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue 

        if processo_atual is None and fila_prontos:
            fila_prontos.sort(key=lambda p: (p.execucao, p.chegada))
            proximo_processo = fila_prontos.pop(0)
            
            if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                tempo_sobrecarga = sobrecarga_contexto
                processo_atual = proximo_processo
                
                if tempo_sobrecarga > 0:
                    print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                    tempo_sobrecarga -= 1
                    tempo_atual += 1
                    continue
            
            processo_atual = proximo_processo
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual

        if processo_atual is not None:
            print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante})")
            processo_atual.restante -= 1
            ultimo_processo_id = processo_atual.id
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou sua execução.")
                processo_atual = None
        else:
            print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    print("\n--- SIMULAÇÃO SJF CONCLUÍDA ---")
    
    print("\n--- RESUMO DE MÉTRICAS SJF ---")
    soma_turnaround = 0
    soma_espera = 0
    print(f"{'ID':<5} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7} | {'Deadline OK?':<12}")
    print("-" * 65)
    for p in sorted(lista_processos, key=lambda x: x.id):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        estourou = p.termino > p.deadline
        status_deadline = "ESTOUROU" if estourou else "OK"
        soma_turnaround += turnaround
        soma_espera += espera
        print(f"{p.id:<5} | {p.chegada:<8} | {p.termino:<8} | {turnaround:<11} | {espera:<7} | {status_deadline:<12}")

    quantidade = len(lista_processos)
    media_turnaround = soma_turnaround / quantidade if quantidade > 0 else 0
    media_espera = soma_espera / quantidade if quantidade > 0 else 0
    print("-" * 65)
    print(f"Tempo Médio de Turnaround: {media_turnaround:.2f}")
    print(f"Tempo Médio de Espera: {media_espera:.2f}")
    print("-----------------------------------------\n")


# ==============================================================================
# 5. NOVO: ROUND-ROBIN (RR) - PREEMPTIVO POR QUANTUM FIXO
# ==============================================================================
def escalonamento_rr(lista_processos, sobrecarga_contexto, quantum):
    print("--- INICIANDO SIMULAÇÃO ROUND-ROBIN ---")
    print(f"Sobrecarga de Contexto: {sobrecarga_contexto} | Quantum: {quantum}\n")
    
    tempo_atual = 0
    fila_prontos = []
    processos_nao_chegados = sorted(lista_processos, key=lambda p: p.chegada)
    
    processo_atual = None
    ultimo_processo_id = None
    tempo_sobrecarga = 0
    quantum_restante = 0

    print("--- INICIANDO LOG DE EXECUÇÃO ---")
    
    while processos_nao_chegados or fila_prontos or processo_atual or tempo_sobrecarga > 0:
        
        while processos_nao_chegados and processos_nao_chegados[0].chegada == tempo_atual:
            novo = processos_nao_chegados.pop(0)
            fila_prontos.append(novo)
            print(f"[Tempo {tempo_atual}] CHEGADA: {novo.id} chegou no sistema.")

        if processo_atual is not None and quantum_restante == 0 and processo_atual.restante > 0:
            print(f"[Tempo {tempo_atual}] PREEMPÇÃO: {processo_atual.id} esgotou seu quantum.")
            fila_prontos.append(processo_atual)
            processo_atual = None

        if tempo_sobrecarga > 0:
            print(f"[Tempo {tempo_atual}] SOBRECARGA: CPU realizando troca de contexto...")
            tempo_sobrecarga -= 1
            tempo_atual += 1
            continue 

        if processo_atual is None and fila_prontos:
            proximo_processo = fila_prontos.pop(0)
            
            if ultimo_processo_id is not None and proximo_processo.id != ultimo_processo_id:
                tempo_sobrecarga = sobrecarga_contexto
                processo_atual = proximo_processo
                quantum_restante = quantum 
                
                if tempo_sobrecarga > 0:
                    print(f"[Tempo {tempo_atual}] INÍCIO SOBRECARGA: Preparando entrada de {processo_atual.id}")
                    tempo_sobrecarga -= 1
                    tempo_atual += 1
                    continue
            
            processo_atual = proximo_processo
            quantum_restante = quantum 
            if processo_atual.inicio == -1:
                processo_atual.inicio = tempo_atual

        if processo_atual is not None:
            print(f"[Tempo {tempo_atual}] EXECUÇÃO: {processo_atual.id} rodando (restante: {processo_atual.restante}, quantum restante: {quantum_restante})")
            processo_atual.restante -= 1
            quantum_restante -= 1
            ultimo_processo_id = processo_atual.id
            
            if processo_atual.restante == 0:
                processo_atual.termino = tempo_atual + 1
                print(f"[Tempo {tempo_atual + 1}] TÉRMINO: {processo_atual.id} finalizou sua execução.")
                processo_atual = None
        else:
            print(f"[Tempo {tempo_atual}] OCIOSA: Nenhuma atividade na CPU.")
            ultimo_processo_id = None
            
        tempo_atual += 1
        
    print("\n--- SIMULAÇÃO ROUND-ROBIN CONCLUÍDA ---")
    
    print("\n--- RESUMO DE MÉTRICAS ROUND-ROBIN ---")
    soma_turnaround = 0
    soma_espera = 0
    print(f"{'ID':<5} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7} | {'Deadline OK?':<12}")
    print("-" * 65)
    for p in sorted(lista_processos, key=lambda x: x.id):
        turnaround = p.termino - p.chegada
        espera = turnaround - p.execucao
        estourou = p.termino > p.deadline
        status_deadline = "ESTOUROU" if estourou else "OK"
        soma_turnaround += turnaround
        soma_espera += espera
        print(f"{p.id:<5} | {p.chegada:<8} | {p.termino:<8} | {turnaround:<11} | {espera:<7} | {status_deadline:<12}")

    quantidade = len(lista_processos)
    media_turnaround = soma_turnaround / quantidade if quantidade > 0 else 0
    media_espera = soma_espera / quantidade if quantidade > 0 else 0
    print("-" * 65)
    print(f"Tempo Médio de Turnaround: {media_turnaround:.2f}")
    print(f"Tempo Médio de Espera: {media_espera:.2f}")
    print("-----------------------------------------\n")