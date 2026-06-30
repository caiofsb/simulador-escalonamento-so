import json
from processo import Processo
from Escalonadores import (
    escalonamento_edf, 
    escalonamento_cfs, 
    escalonamento_fifo, 
    escalonamento_sjf, 
    escalonamento_rr
)

def carregar_processos(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Extrai os parâmetros globais do JSON
    sobrecarga = dados.get("sobrecarga_contexto", 0)
    quantum = dados.get("quantum", 2)
    
    lista_processos = []
    # Cria os objetos Processo com base no JSON
    for p_data in dados.get("processos", []):
        processo = Processo(
            id=p_data["id"],
            chegada=p_data["chegada"],
            execucao=p_data["execucao"],
            deadline=p_data["deadline"],
            prioridade=p_data["prioridade"]
        )
        lista_processos.append(processo)
        
    return lista_processos, sobrecarga, quantum

if __name__ == "__main__":
    
    arquivo_json = "teste_edf_simples.json"
    
    # Carrega os dados
    lista, sobrecarga, quantum = carregar_processos(arquivo_json)
    
    
    
    #escalonamento_fifo(lista, sobrecarga)
    
    # escalonamento_sjf(lista, sobrecarga)
    #escalonamento_rr(lista, sobrecarga, quantum)
    # escalonamento_edf(lista, sobrecarga)
    # escalonamento_cfs(lista, sobrecarga)