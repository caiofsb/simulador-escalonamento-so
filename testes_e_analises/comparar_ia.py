import json
import numpy as np
import os
import sys
from stable_baselines3 import PPO


# 1. Blindagem de caminhos (Acha as pastas independente de onde o terminal rodar)
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.abspath(os.path.join(diretorio_atual, ".."))
sys.path.insert(0, diretorio_raiz)
sys.path.insert(0, os.path.join(diretorio_raiz, "src_cpp"))
import motor_simulacao

print("--- ARENA DE TESTES: INTELIGÊNCIA ARTIFICIAL (MARATONISTA) ---")

caminho_json = os.path.join(diretorio_atual, "..", "dados", "teste_edf_simples.json")
caminho_modelo = os.path.join(diretorio_atual, "..", "inteligencia_artificial", "modelo_ia_maratonista")

with open(caminho_json, 'r') as arquivo:
    dados = json.load(arquivo)

sobrecarga = dados.get("sobrecarga_contexto", 0)
print(f"Arquivo '{os.path.basename(caminho_json)}' carregado. Sobrecarga: {sobrecarga}")

# 2. Prepara o Motor e a IA Maratonista
try:
    modelo = PPO.load(caminho_modelo)
    print("Cérebro 'modelo_ia_maratonista' carregado com sucesso!\n")
except Exception as e:
    print(f"Erro ao carregar modelo: {e}")
    exit()

motor = motor_simulacao.MotorSimulacao()
motor.configurar_sobrecarga(sobrecarga)

# 3. Injeta os processos do JSON no motor C++
for p_dados in dados["processos"]:
    id_numerico = hash(p_dados["id"]) % 10000 
    motor.adicionar_processo(id_numerico, p_dados["chegada"], p_dados["execucao"])

motor.preparar_simulacao()

# 4. Loop Principal de Escalonamento da IA
rodando = True
while rodando:
    if motor.precisa_de_decisao():
        estado_cxx = motor.obter_estado_fila()
        
        obs = np.zeros((10, 3), dtype=np.float32)
        for i in range(min(len(estado_cxx), 10)):
            obs[i][0] = estado_cxx[i].burst_total
            obs[i][1] = estado_cxx[i].tempo_restante
            obs[i][2] = estado_cxx[i].tempo_espera_atual
        
        obs_flat = obs.flatten()
        
        acao, _ = modelo.predict(obs_flat, deterministic=True)
        acao = int(acao)
        
        if acao < len(estado_cxx):
            motor.aplicar_acao(acao)
        else:
            motor.aplicar_acao(0) 
            
    rodando = motor.avancar_clock()

# 5. Geração da Tabela de Métricas Finais
concluidos = motor.obter_concluidos()

print("--- RESUMO DE MÉTRICAS IA (TABELA FINAL) ---")
print(f"{'ID Num':<8} | {'Chegada':<8} | {'Término':<8} | {'Turnaround':<11} | {'Espera':<7}")
print("-" * 55)

soma_turnaround = 0
soma_espera = 0

for p in sorted(concluidos, key=lambda x: x.id):
    soma_turnaround += p.tempo_turnaround
    soma_espera += p.tempo_espera
    
    print(f"{p.id:<8} | {p.tempo_chegada:<8} | {p.tempo_conclusao:<8} | {p.tempo_turnaround:<11} | {p.tempo_espera:<7}")

quantidade = len(concluidos)
if quantidade > 0:
    print("-" * 55)
    print(f"Tempo Médio de Turnaround: {(soma_turnaround / quantidade):.2f}")
    print(f"Tempo Médio de Espera: {(soma_espera / quantidade):.2f}")
    print("--------------------------------------------\n")