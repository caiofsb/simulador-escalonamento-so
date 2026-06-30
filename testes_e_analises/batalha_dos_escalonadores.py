import json
import os
import sys
import copy
import numpy as np
from stable_baselines3 import PPO

# 1. Blindagem Absoluta de Caminhos
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.abspath(os.path.join(diretorio_atual, ".."))

sys.path.insert(0, diretorio_raiz)
sys.path.insert(0, os.path.join(diretorio_raiz, "src_cpp"))

from algoritmos_classicos.processo import Processo
from algoritmos_classicos.Escalonadores import escalonamento_edf, escalonamento_cfs

# Verifica se você adicionou o FIFO e o SJF no seu arquivo de Escalonadores
try:
    from algoritmos_classicos.Escalonadores import escalonamento_fifo, escalonamento_sjf
    tem_fifo_sjf = True
except ImportError:
    tem_fifo_sjf = False

import motor_simulacao

print("="*65)
print("🏆 O GRANDE TORNEIO DOS ESCALONADORES DE PROCESSOS 🏆")
print("="*65)

# 2. Carrega o Cenário de Estresse
caminho_json = os.path.join(diretorio_raiz, "dados", "workload_estresse.json")
try:
    with open(caminho_json, 'r') as f:
        dados = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado em {caminho_json}")
    print("Você rodou o 'gerador_workload.py' primeiro?")
    exit()

sobrecarga = dados.get("sobrecarga_contexto", 1)
processos_brutos = dados["processos"]

print(f"Cenário carregado: {len(processos_brutos)} processos simultâneos.")
print(f"Sobrecarga de contexto configurada: {sobrecarga}\n")

# 3. Instancia os objetos Python para os algoritmos clássicos
processos_python = []
for p in processos_brutos:
    processos_python.append(Processo(
        id=p["id"],
        chegada=p["chegada"],
        execucao=p["execucao"],
        deadline=p["deadline"],
        prioridade=p.get("prioridade", 1)
    ))

# 4. Arena Clássica (Usa deepcopy para que um algoritmo não suje os dados do outro)
if tem_fifo_sjf:
    escalonamento_fifo(copy.deepcopy(processos_python), sobrecarga)
    escalonamento_sjf(copy.deepcopy(processos_python), sobrecarga)

escalonamento_edf(copy.deepcopy(processos_python), sobrecarga)
escalonamento_cfs(copy.deepcopy(processos_python), sobrecarga)

# 5. Arena C++ (A Inteligência Artificial)
print("--- INICIANDO SIMULAÇÃO IA (PPO + C++) ---")
caminho_modelo = os.path.join(diretorio_raiz, "inteligencia_artificial", "modelo_ia_maratonista")

try:
    modelo = PPO.load(caminho_modelo)
except Exception as e:
    print(f"Erro ao carregar modelo da IA: {e}")
    exit()

motor = motor_simulacao.MotorSimulacao()
motor.configurar_sobrecarga(sobrecarga)

for p in processos_brutos:
    # Garante um ID numérico limpo para o C++
    id_num = hash(p["id"]) % 10000 
    motor.adicionar_processo(id_num, p["chegada"], p["execucao"])

motor.preparar_simulacao()

rodando = True
while rodando:
    if motor.precisa_de_decisao():
        estado = motor.obter_estado_fila()
        obs = np.zeros((10, 3), dtype=np.float32)
        for i in range(min(len(estado), 10)):
            obs[i][0] = estado[i].burst_total
            obs[i][1] = estado[i].tempo_restante
            obs[i][2] = estado[i].tempo_espera_atual
        
        acao, _ = modelo.predict(obs.flatten(), deterministic=True)
        acao = int(acao)
        
        if acao < len(estado):
            motor.aplicar_acao(acao)
        else:
            motor.aplicar_acao(0)
            
    rodando = motor.avancar_clock()

concluidos = motor.obter_concluidos()
soma_turn = sum(p.tempo_turnaround for p in concluidos)
soma_esp = sum(p.tempo_espera for p in concluidos)
qtd = len(concluidos)

print("\n--- RESUMO DE MÉTRICAS IA ---")
if qtd > 0:
    print(f"Tempo Médio de Turnaround: {(soma_turn / qtd):.2f}")
    print(f"Tempo Médio de Espera: {(soma_esp / qtd):.2f}")
print("-" * 65 + "\n")

print("="*65)
print("🏁 TORNEIO FINALIZADO! Role o terminal para cima para comparar.")
print("="*65)