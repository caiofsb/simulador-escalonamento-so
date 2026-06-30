import numpy as np
from stable_baselines3 import PPO
import motor_simulacao

print("--- Teste de Sanidade: O que a IA aprendeu? ---")

# 1. Carrega os pesos treinados
try:
    modelo = PPO.load("modelo_escalonador_avancado")
    print("Modelo carregado com sucesso!\n")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

# 2. Instancia um motor C++ limpo
motor = motor_simulacao.MotorSimulacao()

# 3. Criamos uma "pegadinha" para a IA: 3 processos chegam juntos no tempo 0.
# Processo 1 é demorado (10 ticks). Processo 2 é rápido (2 ticks). Processo 3 é médio (5 ticks).
motor.adicionar_processo(1, 0, 10)
motor.adicionar_processo(2, 0, 2)
motor.adicionar_processo(3, 0, 5)
motor.preparar_simulacao()

print("Cenário: 3 Processos aguardando na fila.")
print(" -> ID 1: 10 de Burst")
print(" -> ID 2: 2 de Burst")
print(" -> ID 3: 5 de Burst\n")
print("Iniciando o relógio...\n")

rodando = True
while rodando:
    if motor.precisa_de_decisao():
        estado_cxx = motor.obter_estado_fila()
        
        # Formata a matriz exatamente como fizemos no ambiente de treinamento
        obs = np.zeros((10, 3), dtype=np.float32)
        for i in range(min(len(estado_cxx), 10)):
            obs[i][0] = estado_cxx[i].burst_total
            obs[i][1] = estado_cxx[i].tempo_restante
            obs[i][2] = estado_cxx[i].tempo_espera_atual
        
        # Achata para 1D
        obs_flat = obs.flatten()
        
        # A IA toma a decisão (deterministic=True remove a aleatoriedade)
        acao, _ = modelo.predict(obs_flat, deterministic=True)
        acao = int(acao)
        
        if acao < len(estado_cxx):
            escolhido = estado_cxx[acao]
            print(f"[Clock {motor.obter_clock_atual()}] A IA escolheu o Processo ID {escolhido.id} (Burst Restante: {escolhido.tempo_restante})")
            motor.aplicar_acao(acao)
        else:
            print(f"[Clock {motor.obter_clock_atual()}] ⚠️ A IA fez uma escolha inválida (índice {acao}). Forçando índice 0.")
            motor.aplicar_acao(0)
            
    rodando = motor.avancar_clock()

print("\n--- Avaliação Concluída ---")