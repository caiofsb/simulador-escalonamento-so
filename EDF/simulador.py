import json
from processo import Processo
from Escalonadores import escalonamento_edf, escalonamento_cfs

def testar_algoritmo(caminho_arquivo, algoritmo):
    with open(caminho_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)

    sobrecarga = dados.get("sobrecarga_contexto", 0)
    
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
    if algoritmo == "EDF":
        escalonamento_edf(processos_instanciados, sobrecarga)
    elif algoritmo == "CFS":
        escalonamento_cfs(processos_instanciados, sobrecarga)
    else:
        print("Algoritmo não reconhecido.")

# ==========================================
# GATILHO DE EXECUÇÃO CORRIGIDO
# ==========================================
if __name__ == "__main__":
    # Para testar o CFS, basta passar "CFS" como segundo parâmetro
    #testar_algoritmo("teste_edf_simples.json", "EDF")
    testar_algoritmo("teste_edf_simples.json", "CFS")
    
    # Quando quiser testar o EDF, basta comentar a linha acima e descomentar a abaixo:
    # testar_algoritmo("teste_edf_simples.json", "EDF")