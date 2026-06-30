import gymnasium as gym
from ambiente_escalonador import EscalonadorEnv
from stable_baselines3 import PPO

print("--- INICIANDO TREINAMENTO DE ELITE (MARATONA) ---")

env = EscalonadorEnv(max_visibilidade_fila=10)

# Vamos criar um cérebro novo, com hiperparâmetros focados em longo prazo
modelo = PPO(
    "MlpPolicy", 
    env, 
    verbose=1, 
    learning_rate=0.0001,  # Taxa menor para aprendizado microscópico e profundo
    ent_coef=0.03,         # 3% de exploração contínua para evitar vícios
    gamma=0.995,           # Visão de futuro ainda mais longa
    batch_size=256,        # Lotes de memória maiores
    n_steps=4096           # Coleta mais dados antes de atualizar os pesos
)

# 2.000.000 de passos (Deve levar de 15 a 20 minutos no seu hardware)
passos_treinamento = 2000000 
print(f"\nIniciando corrida de {passos_treinamento} passos...")
modelo.learn(total_timesteps=passos_treinamento)

nome_arquivo = "modelo_ia_maratonista"
modelo.save(nome_arquivo)
print(f"\n✅ Treinamento concluído! Pesos salvos em: '{nome_arquivo}.zip'")