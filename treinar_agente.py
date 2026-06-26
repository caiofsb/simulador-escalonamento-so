import gymnasium as gym
from ambiente_escalonador import EscalonadorEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

print("--- Iniciando a Fase 5: Treinamento do Agente de IA ---")

# 1. Instancia o nosso simulador C++ envelopado no Gymnasium
env = EscalonadorEnv(max_visibilidade_fila=10)

# (Garantia de Qualidade) Verifica se o ambiente segue as regras matemáticas estritas do Gymnasium
print("Validando a integridade do ambiente...")
check_env(env)
print("Ambiente validado com sucesso!\n")

# 2. Cria a Rede Neural (O Modelo PPO)
# "MlpPolicy" significa Multilayer Perceptron. Usamos isso porque nosso estado é uma matriz de números (não imagens).
# verbose=1 fará com que o terminal imprima os logs de progresso do treinamento.
print("Construindo o cérebro da IA...")
modelo = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)

# 3. Executa o Treinamento
# 100.000 passos (timesteps) é um ótimo ponto de partida. O agente vai rodar milhares
# de simulações do seu motor C++, errar, receber penalidades e ajustar seus pesos.
passos_treinamento = 100000
print(f"\nIniciando o treinamento por {passos_treinamento} passos.")
print("Isso pode levar alguns minutos dependendo do seu processador...")
modelo.learn(total_timesteps=passos_treinamento)

# 4. Salva o conhecimento adquirido
nome_arquivo = "modelo_escalonador"
modelo.save(nome_arquivo)
print(f"\n✅ Treinamento concluído! Pesos da rede neural salvos no arquivo: '{nome_arquivo}.zip'")

# 5. Teste Rápido de Execução Pós-Treino
print("\n--- Rodando uma simulação com a IA já treinada ---")
estado, info = env.reset()
terminou = False
passos_teste = 0

while not terminou:
    # predict(deterministic=True) força a IA a usar a melhor escolha que aprendeu, 
    # sem explorar opções aleatórias (o que ela faz durante o treinamento).
    acao_escolhida, _estados_ocultos = modelo.predict(estado, deterministic=True)
    
    estado, recompensa, terminou, truncado, info = env.step(acao_escolhida)
    passos_teste += 1

print(f"Simulação concluída magistralmente pela IA tomando {passos_teste} decisões precisas.")