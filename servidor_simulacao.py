import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = "127.0.0.1"
PORT = 8000


def copiar_processos(processos):
    normalizados = []
    for indice, processo in enumerate(processos):
        normalizados.append(
            {
                "id": str(processo.get("id", f"P{indice + 1}")),
                "chegada": int(processo["chegada"]),
                "execucao": int(processo["execucao"]),
                "deadline": int(processo["deadline"]),
                "prioridade": int(processo.get("prioridade", 1)),
                "restante": int(processo["execucao"]),
                "inicio": [],
                "termino": None,
                "vruntime": 0.0,
                "ordem": indice,
            }
        )
    return normalizados


def ordenar_prontos(fila, algoritmo):
    def chegada(processo):
        return (processo["chegada"], processo["ordem"])

    if algoritmo == "FIFO":
        fila.sort(key=chegada)
    elif algoritmo == "SJF":
        fila.sort(key=lambda p: (p["execucao"], p["chegada"], p["ordem"]))
    elif algoritmo == "RR":
        fila.sort(key=chegada)
    elif algoritmo == "PRIORIDADES":
        fila.sort(key=lambda p: (p["prioridade"], p["chegada"], p["ordem"]))
    elif algoritmo == "EDF":
        fila.sort(key=lambda p: (p["deadline"], p["prioridade"], p["chegada"], p["ordem"]))
    elif algoritmo == "CFS":
        fila.sort(key=lambda p: (p["vruntime"], p["prioridade"], p["chegada"], p["ordem"]))
    elif algoritmo == "IA":
        fila.sort(key=lambda p: (p["score_ia"], p["deadline"], p["prioridade"], p["chegada"], p["ordem"]))


def atualizar_scores_ia(fila, tempo):
    for processo in fila:
        espera = max(0, tempo - processo["chegada"])
        folga_deadline = processo["deadline"] - tempo - processo["restante"]
        processo["score_ia"] = (
            folga_deadline * 0.45
            + processo["restante"] * 0.35
            + processo["prioridade"] * 0.25
            - espera * 0.30
        )


def adicionar_chegadas(futuros, prontos, tempo, algoritmo):
    while futuros and futuros[0]["chegada"] <= tempo:
        processo = futuros.pop(0)
        if algoritmo == "CFS":
            processo["vruntime"] = float(tempo)
        prontos.append(processo)


def deve_preemptar(atual, prontos, algoritmo):
    if atual is None or not prontos:
        return False

    ordenar_prontos(prontos, algoritmo)
    melhor = prontos[0]

    if algoritmo == "PRIORIDADES":
        return melhor["prioridade"] < atual["prioridade"]
    if algoritmo == "EDF":
        return melhor["deadline"] < atual["deadline"]
    if algoritmo == "CFS":
        return melhor["vruntime"] < atual["vruntime"]
    if algoritmo == "IA":
        atualizar_scores_ia(prontos + [atual], atual.get("tempo_atual", 0))
        ordenar_prontos(prontos, algoritmo)
        return prontos[0]["score_ia"] < atual["score_ia"] - 0.25
    return False


def nova_fatia(timeline, processo_id, tempo):
    if not timeline:
        return True
    anterior = timeline[-1]
    return (
        anterior["tipo"] != "execucao"
        or anterior.get("processo_id") != processo_id
        or anterior["fim"] != tempo
    )


def simular(payload):
    algoritmo = str(payload.get("algoritmo", "FIFO")).upper()
    if algoritmo not in {"FIFO", "SJF", "RR", "PRIORIDADES", "EDF", "CFS", "IA"}:
        raise ValueError("Algoritmo nao reconhecido.")

    quantum = max(1, int(payload.get("quantum", 2)))
    sobrecarga = max(0, int(payload.get("sobrecarga_contexto", 0)))
    processos = copiar_processos(payload.get("processos", []))
    if not processos:
        raise ValueError("Informe ao menos um processo.")

    futuros = sorted(processos, key=lambda p: (p["chegada"], p["ordem"]))
    prontos = []
    timeline = []
    tempo = 0
    atual = None
    ultimo_id = None
    sobrecarga_restante = 0
    quantum_restante = quantum
    ticks_ociosos = 0
    ticks_sobrecarga = 0
    ticks_execucao = 0
    trocas_contexto = 0
    preempcoes = 0
    guarda = 0

    while futuros or prontos or atual is not None or sobrecarga_restante > 0:
        guarda += 1
        if guarda > 10000:
            raise RuntimeError("Simulacao interrompida por limite de seguranca.")

        adicionar_chegadas(futuros, prontos, tempo, algoritmo)

        if sobrecarga_restante > 0:
            timeline.append({"tipo": "sobrecarga", "inicio": tempo, "fim": tempo + 1})
            ticks_sobrecarga += 1
            sobrecarga_restante -= 1
            tempo += 1
            continue

        if algoritmo == "RR" and atual is not None and atual["restante"] > 0 and quantum_restante == 0:
            if prontos:
                prontos.append(atual)
                atual = None
                preempcoes += 1
            else:
                quantum_restante = quantum

        if algoritmo == "IA":
            if atual is not None:
                atual["tempo_atual"] = tempo
            atualizar_scores_ia(prontos + ([atual] if atual is not None else []), tempo)

        if algoritmo in {"PRIORIDADES", "EDF", "CFS", "IA"} and deve_preemptar(atual, prontos, algoritmo):
            prontos.append(atual)
            atual = None
            preempcoes += 1

        if atual is None and prontos:
            if algoritmo == "IA":
                atualizar_scores_ia(prontos, tempo)
            ordenar_prontos(prontos, algoritmo)
            atual = prontos.pop(0)
            quantum_restante = quantum

            if ultimo_id is not None and atual["id"] != ultimo_id:
                trocas_contexto += 1
                if sobrecarga > 0:
                    sobrecarga_restante = sobrecarga - 1
                    timeline.append({"tipo": "sobrecarga", "inicio": tempo, "fim": tempo + 1})
                    ticks_sobrecarga += 1
                    tempo += 1
                    continue

        if atual is not None:
            if nova_fatia(timeline, atual["id"], tempo):
                atual["inicio"].append(tempo)

            timeline.append(
                {
                    "tipo": "execucao",
                    "processo_id": atual["id"],
                    "inicio": tempo,
                    "fim": tempo + 1,
                }
            )
            atual["restante"] -= 1
            ticks_execucao += 1
            ultimo_id = atual["id"]

            if algoritmo == "RR":
                quantum_restante -= 1
            elif algoritmo == "CFS":
                atual["vruntime"] += 1 * (1.25 ** (atual["prioridade"] - 1))

            if atual["restante"] == 0:
                atual["termino"] = tempo + 1
                atual = None
        else:
            timeline.append({"tipo": "ocioso", "inicio": tempo, "fim": tempo + 1})
            ticks_ociosos += 1
            ultimo_id = None

        tempo += 1

    makespan = timeline[-1]["fim"] if timeline else 0
    tabela = []
    for processo in sorted(processos, key=lambda p: p["ordem"]):
        turnaround = processo["termino"] - processo["chegada"]
        espera = turnaround - processo["execucao"]
        tabela.append(
            {
                "id": processo["id"],
                "chegada": processo["chegada"],
                "execucao": processo["execucao"],
                "deadline": processo["deadline"],
                "prioridade": processo["prioridade"],
                "inicio": processo["inicio"],
                "termino": processo["termino"],
                "espera": espera,
                "turnaround": turnaround,
                "deadline_ok": processo["termino"] <= processo["deadline"],
            }
        )

    quantidade = len(tabela)
    media_turnaround = sum(p["turnaround"] for p in tabela) / quantidade
    media_espera = sum(p["espera"] for p in tabela) / quantidade

    return {
        "algoritmo": algoritmo,
        "timeline": timeline,
        "tabela": tabela,
        "metricas": {
            "media_turnaround": media_turnaround,
            "media_espera": media_espera,
            "throughput": quantidade / makespan if makespan else 0,
            "cpu_ociosa_percentual": (ticks_ociosos / makespan) * 100 if makespan else 0,
            "preempcoes": preempcoes,
            "trocas_contexto": trocas_contexto,
            "makespan": makespan,
            "ticks_sobrecarga": ticks_sobrecarga,
            "ticks_execucao": ticks_execucao,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def _headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._headers(204)

    def do_GET(self):
        if self.path == "/api/health":
            self._headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        self._headers(404)
        self.wfile.write(json.dumps({"erro": "Rota nao encontrada."}).encode("utf-8"))

    def do_POST(self):
        if self.path != "/api/simular":
            self._headers(404)
            self.wfile.write(json.dumps({"erro": "Rota nao encontrada."}).encode("utf-8"))
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            resultado = simular(payload)
            self._headers()
            self.wfile.write(json.dumps(resultado).encode("utf-8"))
        except Exception as exc:
            self._headers(400)
            self.wfile.write(json.dumps({"erro": str(exc)}).encode("utf-8"))

    def log_message(self, formato, *args):
        print("%s - %s" % (self.address_string(), formato % args))


if __name__ == "__main__":
    servidor = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Servidor Python em http://{HOST}:{PORT}")
    servidor.serve_forever()
