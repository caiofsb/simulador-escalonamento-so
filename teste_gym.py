from ambiente_escalonador import EscalonadorEnv

print("--- Testando o Ambiente Gymnasium ---")
env = EscalonadorEnv()

# O reset deve retornar uma matriz cheia de zeros ou com os dados dos processos
estado_inicial, info = env.reset()
print("\nFormato do Estado Inicial (Matriz da IA):")
print(estado_inicial)

terminou = False
passos = 0

while not terminou:
    # Escolhe uma ação totalmente aleatória para simular uma IA que não sabe de nada ainda
    acao_aleatoria = env.action_space.sample() 
    
    estado, recompensa, terminou, _, _ = env.step(acao_aleatoria)
    passos += 1

print(f"\n✅ Simulação concluída com sucesso em {passos} passos de decisão!")
print("O ambiente está pronto para receber o cérebro (Stable Baselines3).")