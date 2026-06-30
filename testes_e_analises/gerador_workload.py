import json
import random
import os

def gerar_json_estresse(nome_arquivo="workload_estresse.json", num_processos=50):
    # Calcula o caminho absoluto para a pasta 'dados'
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_salvamento = os.path.join(diretorio_atual, "..", "dados", nome_arquivo)

    random.seed(42) # Semente fixa para garantir reprodutibilidade
    
    dados = {
        "quantum": 4,               
        "sobrecarga_contexto": 1,   
        "custo_disco": 3,           
        "seed": 42,
        "processos": []
    }
    
    for i in range(1, num_processos + 1):
        # Distribuição de chegada: muitos no início, alguns retardatários
        chegada = random.randint(0, 80)
        
        # Simulação de IO-bound (curtos, 1-5) e CPU-bound (longos, 10-25)
        is_cpu_bound = random.random() > 0.7 
        execucao = random.randint(10, 25) if is_cpu_bound else random.randint(1, 5)
        
        # Deadline factível, mas apertado para processos longos
        margem = random.randint(5, 15)
        deadline = chegada + execucao + margem
        
        # Prioridades de 1 (Alta) a 5 (Baixa)
        prioridade = random.randint(1, 5)
        
        processo = {
            "id": f"P{i}",
            "chegada": chegada,
            "execucao": execucao,
            "deadline": deadline,
            "prioridade": prioridade
        }
        dados["processos"].append(processo)
        
    # Salva o arquivo diretamente na pasta 'dados/'
    with open(caminho_salvamento, 'w') as f:
        json.dump(dados, f, indent=4)
        
    print(f"✅ Arquivo gerado com sucesso em: {caminho_salvamento}")

if __name__ == "__main__":
    gerar_json_estresse()