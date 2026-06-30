class Processo:
    def __init__(self, id, chegada, execucao, deadline, prioridade):
        self.id = id
        self.chegada = chegada
        self.execucao = execucao
        self.restante = execucao
        self.deadline = deadline
        self.prioridade = prioridade
    
        
        # Para as métricas do trabalho
        self.inicio = -1
        self.termino = -1

    # Facilita a visualização do processo no terminal
    def __repr__(self):
        return f"[{self.id}] Chegada: {self.chegada}, Exec: {self.execucao}, Deadline: {self.deadline}"
