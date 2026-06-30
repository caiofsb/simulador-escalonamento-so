import motor_simulacao

print("✅ Importação do motor C++ realizada com sucesso!\n")

# Instancia o motor (o C++ alocando a memória lá no fundo)
motor = motor_simulacao.MotorSimulacao()

# Adiciona processos
motor.adicionar_processo(1, 0, 4)
motor.adicionar_processo(2, 1, 3)
motor.preparar_simulacao()

print(f"🕒 Clock inicial: {motor.obter_clock_atual()}")

# Roda o motor até ele pedir ajuda
rodando = True
while rodando and not motor.precisa_de_decisao():
    rodando = motor.avancar_clock()

if motor.precisa_de_decisao():
    estado = motor.obter_estado_fila()
    print(f"🛑 O motor pausou no clock {motor.obter_clock_atual()} e solicitou uma decisão!")
    print(f"Processos na fila: {len(estado)}")
    
    # Acessando os dados mapeados do C++ perfeitamente no Python
    for proc in estado:
        print(f" -> Processo ID: {proc.id} | Burst Restante: {proc.tempo_restante}")