import gymnasium as gym
from ambiente_escalonador import EscalonadorEnv
from stable_baselines3 import PPO

print("--- Iniciando o Treinamento Avançado da IA ---")

# 1. Instancia o ambiente
env = EscalonadorEnv(max_visibilidade_fila=10)

print("Construindo o cérebro com alta taxa de exploração...")

# 2. Configurações avançadas do PPO
modelo = PPO(
    "MlpPolicy", 
    env, 
    verbose=1, 
    learning_rate=0.0003,
    ent_coef=0.05,       # <- O SEGREDO AQUI: 5% das decisões serão puramente exploratórias
    gamma=0.99,          # Foca na recompensa de longo prazo
    batch_size=128       # Aprende com lotes maiores de experiência por vez
)

# 3. Executa o Treinamento Extenso (Pode demorar uns 5 a 10 minutos)
passos_treinamento = 500000 
print(f"\nIniciando o treinamento por {passos_treinamento} passos.")
modelo.learn(total_timesteps=passos_treinamento)

# 4. Salva o conhecimento com um novo nome para não sobrescrever o antigo
nome_arquivo = "modelo_escalonador_avancado"
modelo.save(nome_arquivo)
print(f"\n✅ Treinamento concluído! Pesos salvos em: '{nome_arquivo}.zip'")