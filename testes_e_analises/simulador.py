import json
import sys
import os

# Adiciona a raiz do projeto ao caminho do Python para ele achar todas as pastas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Agora usamos a notação de ponto para importar de outras pastas
from algoritmos_classicos.processo import Processo
from algoritmos_classicos.Escalonadores import (
    escalonamento_cfs,
    escalonamento_edf,
    escalonamento_fifo,
    escalonamento_prioridades,
    escalonamento_rr,
    escalonamento_sjf,
)
def testar_algoritmo(caminho_arquivo, algoritmo):
    with open(caminho_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)

    sobrecarga = dados.get("sobrecarga_contexto", 0)
    quantum = dados.get("quantum", 2)
    
    # Converte os dados brutos do JSON para objetos da classe Processo
    processos_instanciados = []
    for p_dados in dados["processos"]:
        novo_processo = Processo(
            id=p_dados["id"],
            chegada=p_dados["chegada"],
            execucao=p_dados["execucao"],
            deadline=p_dados["deadline"],
            prioridade=p_dados.get("prioridade", 1) # Padrão 1 caso não exista
        )
        processos_instanciados.append(novo_processo)

    # Injeta os dados no simulador escolhido
    algoritmo = algoritmo.upper()

    if algoritmo == "FIFO":
        escalonamento_fifo(processos_instanciados, sobrecarga)
    elif algoritmo == "SJF":
        escalonamento_sjf(processos_instanciados, sobrecarga)
    elif algoritmo == "RR":
        escalonamento_rr(processos_instanciados, sobrecarga, quantum)
    elif algoritmo == "PRIORIDADES":
        escalonamento_prioridades(processos_instanciados, sobrecarga)
    elif algoritmo == "EDF":
        escalonamento_edf(processos_instanciados, sobrecarga)
    elif algoritmo == "CFS":
        escalonamento_cfs(processos_instanciados, sobrecarga)
    else:
        print("Algoritmo não reconhecido.")

# ==========================================
# GATILHO DE EXECUÇÃO CORRIGIDO
# ==========================================
if __name__ == "__main__":
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "..", "dados", "teste_edf_simples.json")
    # Para testar o CFS, basta passar "CFS" como segundo parâmetro
    #testar_algoritmo("teste_edf_simples.json", "EDF")
    algoritmo = sys.argv[1] if len(sys.argv) > 1 else "EDF"
    testar_algoritmo(caminho_json, algoritmo)
    
    # Quando quiser testar o EDF, basta comentar a linha acima e descomentar a abaixo:
    # testar_algoritmo("teste_edf_simples.json", "EDF")
