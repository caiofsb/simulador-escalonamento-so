import gymnasium as gym
from gymnasium import spaces
import numpy as np
import motor_simulacao
import random

class EscalonadorEnv(gym.Env):
    """
    Ambiente Customizado de Escalonamento de CPU que segue a interface do Gymnasium.
    """
    def __init__(self, max_visibilidade_fila=10):
        super(EscalonadorEnv, self).__init__()
        
        self.motor = None
        self.max_fila = max_visibilidade_fila
        self.clock_limite = 1000 # Prevenção contra loops infinitos
        
        # --- ESPAÇO DE AÇÃO ---
        # A IA retorna um número inteiro de 0 até (max_fila - 1)
        self.action_space = spaces.Discrete(self.max_fila)
        
        # --- ESPAÇO DE OBSERVAÇÃO (ESTADO) ---
        # Matriz: [max_fila] linhas por [3] colunas. 
        # Colunas: 1. Burst Total, 2. Tempo Restante, 3. Tempo de Espera Atual
        self.observation_space = spaces.Box(
            low=0, 
            high=1000, # Valor máximo arbitrário para as métricas
            shape=(self.max_fila *3,), 
            dtype=np.float32
        )

    def _gerar_workload(self):
        """Gera uma carga aleatória de processos para cada episódio de treinamento."""
        num_processos = random.randint(10, 30)
        for i in range(num_processos):
            # Processos chegam em momentos variados
            chegada = random.randint(0, 50) 
            # Processos têm tamanhos variados (simulando IO-bound e CPU-bound)
            burst = random.randint(1, 20)   
            self.motor.adicionar_processo(i + 1, chegada, burst)

    def _obter_estado_formatado(self):
        """Transforma a lista dinâmica do C++ em uma matriz estática para a Rede Neural."""
        estado_cxx = self.motor.obter_estado_fila()
        obs = np.zeros((self.max_fila, 3), dtype=np.float32)
        
        for i in range(min(len(estado_cxx), self.max_fila)):
            obs[i][0] = estado_cxx[i].burst_total
            obs[i][1] = estado_cxx[i].tempo_restante
            obs[i][2] = estado_cxx[i].tempo_espera_atual
            
        return obs.flatten()  # Retorna como vetor 1D para a rede neural

    def _avancar_ate_decisao(self):
        """Roda o relógio do C++ no modo 'fast-forward' até a CPU ficar ociosa."""
        rodando = True
        while rodando and not self.motor.precisa_de_decisao():
            rodando = self.motor.avancar_clock()
            
            # Trava de segurança para não rodar para sempre se houver bug no C++
            if self.motor.obter_clock_atual() > self.clock_limite:
                return False 
        return rodando

    def reset(self, seed=None, options=None):
        """Reinicia o simulador para um novo episódio de treinamento."""
        super().reset(seed=seed)
        
        # Instancia um motor C++ totalmente novo e limpo
        self.motor = motor_simulacao.MotorSimulacao()
        self._gerar_workload()
        self.motor.preparar_simulacao()
        
        self._avancar_ate_decisao()
        
        return self._obter_estado_formatado(), {}

    def step(self, action):
        """Aplica a escolha da IA e avança no tempo."""
        estado_cxx = self.motor.obter_estado_fila()
        recompensa_extra = 0.0
        
        # Validação: A IA escolheu um índice vazio (padding)?
        if action >= len(estado_cxx):
            # Punição severa: a IA tentou escalonar um fantasma!
            recompensa_extra = -10.0 
            # Para o simulador não travar, forçamos a execução do primeiro processo (FIFO)
            self.motor.aplicar_acao(0)
        else:
            self.motor.aplicar_acao(int(action))
            
        # Coleta a recompensa gerada lá no C++
        recompensa_cxx = self.motor.obter_recompensa()
        reward = recompensa_cxx + recompensa_extra
        
        # Roda a simulação até a próxima decisão
        ainda_tem_processo = self._avancar_ate_decisao()
        terminou = not ainda_tem_processo
        
        novo_estado = self._obter_estado_formatado()
        
        return novo_estado, reward, terminou, False, {}