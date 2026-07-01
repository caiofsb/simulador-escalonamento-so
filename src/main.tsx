import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type ProcessoEntrada = {
  id: string;
  chegada: number;
  execucao: number;
  deadline: number;
  prioridade: number;
};

type CasoEntrada = {
  quantum: number;
  sobrecarga_contexto: number;
  processos: ProcessoEntrada[];
};

type EventoTimeline = {
  tipo: "execucao" | "sobrecarga" | "ocioso";
  processo_id?: string;
  inicio: number;
  fim: number;
};

type LinhaTabela = ProcessoEntrada & {
  inicio: number[];
  termino: number;
  espera: number;
  turnaround: number;
  deadline_ok: boolean;
};

type Resultado = {
  algoritmo: string;
  timeline: EventoTimeline[];
  tabela: LinhaTabela[];
  metricas: {
    media_turnaround: number;
    media_espera: number;
    throughput: number;
    cpu_ociosa_percentual: number;
    preempcoes: number;
    trocas_contexto: number;
    makespan: number;
    ticks_sobrecarga: number;
    ticks_execucao: number;
  };
};

const casos: Record<string, CasoEntrada> = {
  base: {
    quantum: 2,
    sobrecarga_contexto: 1,
    processos: [
      { id: "P1", chegada: 0, execucao: 5, deadline: 8, prioridade: 2 },
      { id: "P2", chegada: 1, execucao: 4, deadline: 12, prioridade: 1 },
      { id: "P3", chegada: 3, execucao: 2, deadline: 20, prioridade: 3 },
    ],
  },
  ociosidade: {
    quantum: 2,
    sobrecarga_contexto: 1,
    processos: [
      { id: "P1", chegada: 0, execucao: 3, deadline: 7, prioridade: 2 },
      { id: "P2", chegada: 6, execucao: 4, deadline: 14, prioridade: 1 },
      { id: "P3", chegada: 12, execucao: 2, deadline: 18, prioridade: 3 },
    ],
  },
  estresse: {
    quantum: 4,
    sobrecarga_contexto: 1,
    processos: [
      { id: "P1", chegada: 0, execucao: 9, deadline: 18, prioridade: 3 },
      { id: "P2", chegada: 1, execucao: 3, deadline: 9, prioridade: 1 },
      { id: "P3", chegada: 2, execucao: 7, deadline: 16, prioridade: 4 },
      { id: "P4", chegada: 4, execucao: 2, deadline: 11, prioridade: 2 },
      { id: "P5", chegada: 6, execucao: 6, deadline: 20, prioridade: 1 },
    ],
  },
};

const algoritmos = [
  ["FIFO", "FIFO / FCFS"],
  ["SJF", "SJF"],
  ["RR", "Round-Robin"],
  ["PRIORIDADES", "Prioridades"],
  ["EDF", "EDF"],
  ["CFS", "CFS-Sim"],
  ["IA", "IA Autoral"],
];

function numero(valor: number, casas = 2) {
  return valor.toFixed(casas);
}

function App() {
  const [algoritmo, setAlgoritmo] = useState("FIFO");
  const [caso, setCaso] = useState("base");
  const [quantum, setQuantum] = useState(casos.base.quantum);
  const [sobrecarga, setSobrecarga] = useState(casos.base.sobrecarga_contexto);
  const [jsonEntrada, setJsonEntrada] = useState(JSON.stringify(casos.base, null, 2));
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [tickVisivel, setTickVisivel] = useState(0);

  const processosEntrada = useMemo(() => {
    try {
      const dados = JSON.parse(jsonEntrada) as CasoEntrada;
      return dados.processos ?? [];
    } catch {
      return [];
    }
  }, [jsonEntrada]);

  const algoritmoAtual = algoritmos.find(([valor]) => valor === algoritmo)?.[1] ?? algoritmo;
  const statusSimulacao = resultado ? "Resultado pronto" : "Sem execucao";
  const ultimoTempo = resultado?.metricas.makespan ?? 0;

  function carregarCaso(nome: string) {
    const selecionado = casos[nome];
    setCaso(nome);
    setQuantum(selecionado.quantum);
    setSobrecarga(selecionado.sobrecarga_contexto);
    setJsonEntrada(JSON.stringify(selecionado, null, 2));
    setResultado(null);
    setTickVisivel(0);
  }

  function atualizarCampoJson(campo: "quantum" | "sobrecarga_contexto", valor: number) {
    if (campo === "quantum") {
      setQuantum(valor);
    } else {
      setSobrecarga(valor);
    }

    try {
      const entrada = JSON.parse(jsonEntrada) as CasoEntrada;
      setJsonEntrada(JSON.stringify({ ...entrada, [campo]: valor }, null, 2));
    } catch {
      setErro("Corrija o JSON para sincronizar os parametros.");
    }
  }

  function atualizarJson(valor: string) {
    setJsonEntrada(valor);
    setResultado(null);
    setTickVisivel(0);

    try {
      const entrada = JSON.parse(valor) as CasoEntrada;
      if (Number.isFinite(entrada.quantum)) setQuantum(entrada.quantum);
      if (Number.isFinite(entrada.sobrecarga_contexto)) setSobrecarga(entrada.sobrecarga_contexto);
      setErro("");
    } catch {
      // Enquanto o usuario edita, o erro formal aparece ao simular.
    }
  }

  async function simular() {
    setCarregando(true);
    setErro("");

    try {
      const entrada = JSON.parse(jsonEntrada) as CasoEntrada;
      const resposta = await fetch("/api/simular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...entrada,
          algoritmo,
          quantum,
          sobrecarga_contexto: sobrecarga,
        }),
      });
      const corpo = await resposta.json();

      if (!resposta.ok) {
        throw new Error(corpo.erro ?? "Falha ao simular.");
      }

      setResultado(corpo as Resultado);
      setTickVisivel(0);
    } catch (error) {
      setResultado(null);
      setTickVisivel(0);
      setErro(error instanceof Error ? error.message : "Erro inesperado.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    if (!resultado) return;

    const maxDeadline = resultado.tabela.reduce((maior, processo) => Math.max(maior, processo.deadline), 0);
    const limite = Math.max(resultado.metricas.makespan, maxDeadline + 1);
    const timer = window.setInterval(() => {
      setTickVisivel((atual) => {
        if (atual >= limite) {
          window.clearInterval(timer);
          return atual;
        }
        return atual + 1;
      });
    }, 170);

    return () => window.clearInterval(timer);
  }, [resultado]);

  return (
    <main className="app-shell">
      <header className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Sistemas Operacionais</p>
          <h1>Simulador de Escalonamento</h1>
        </div>
        <div className="hero-status" aria-label="Resumo da simulacao">
          <div>
            <span>Algoritmo</span>
            <strong>{algoritmoAtual}</strong>
          </div>
          <div>
            <span>Processos</span>
            <strong>{processosEntrada.length}</strong>
          </div>
          <div>
            <span>Tempo</span>
            <strong>{ultimoTempo}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{statusSimulacao}</strong>
          </div>
        </div>
      </header>

      <section className="workspace">
        <aside className="control-panel">
          <div className="panel-title-row">
            <div>
              <p className="eyebrow">Entrada</p>
              <h2>Configuracao</h2>
            </div>
            <span className="live-pill">{carregando ? "Rodando" : "Pronto"}</span>
          </div>

          <label className="field">
            <span>Algoritmo</span>
            <select value={algoritmo} onChange={(event) => setAlgoritmo(event.target.value)}>
              {algoritmos.map(([valor, rotulo]) => (
                <option value={valor} key={valor}>
                  {rotulo}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Caso</span>
            <select value={caso} onChange={(event) => carregarCaso(event.target.value)}>
              <option value="base">Caso base</option>
              <option value="ociosidade">Caso com ociosidade</option>
              <option value="estresse">Caso de estresse</option>
            </select>
          </label>

          <div className="split-fields">
            <label className="field">
              <span>Quantum</span>
              <input min={1} type="number" value={quantum} onChange={(event) => atualizarCampoJson("quantum", Number(event.target.value))} />
            </label>
            <label className="field">
              <span>Sobrecarga</span>
              <input min={0} type="number" value={sobrecarga} onChange={(event) => atualizarCampoJson("sobrecarga_contexto", Number(event.target.value))} />
            </label>
          </div>

          <label className="field json-field">
            <span>Entrada JSON</span>
            <textarea value={jsonEntrada} spellCheck={false} onChange={(event) => atualizarJson(event.target.value)} />
          </label>

          <button className="primary-button" onClick={simular} type="button" disabled={carregando}>
            {carregando ? "Simulando..." : "Simular"}
          </button>
        </aside>

        <section className="results">
          {erro ? <div className="error-box">{erro}</div> : null}
          <Metricas resultado={resultado} />
          <Gantt resultado={resultado} processosEntrada={processosEntrada} tickVisivel={tickVisivel} />
          <Tabela resultado={resultado} processosEntrada={processosEntrada} />
        </section>
      </section>
    </main>
  );
}

function Metricas({ resultado }: { resultado: Resultado | null }) {
  const metricas = resultado?.metricas;
  const itens = [
    ["Turnaround medio", metricas ? numero(metricas.media_turnaround) : "-"],
    ["Espera media", metricas ? numero(metricas.media_espera) : "-"],
    ["Throughput", metricas ? numero(metricas.throughput, 3) : "-"],
    ["CPU ociosa", metricas ? `${numero(metricas.cpu_ociosa_percentual)}%` : "-"],
    ["Preempcoes", metricas ? String(metricas.preempcoes) : "-"],
    ["Trocas contexto", metricas ? String(metricas.trocas_contexto) : "-"],
  ];

  return (
    <div className="metric-grid">
      {itens.map(([rotulo, valor]) => (
        <article className="metric-card" key={rotulo}>
          <span>{rotulo}</span>
          <strong>{valor}</strong>
        </article>
      ))}
    </div>
  );
}

function eventoNoTempo(timeline: EventoTimeline[], tempo: number, tipo: EventoTimeline["tipo"], processoId?: string) {
  return timeline.find((evento) => evento.inicio === tempo && evento.tipo === tipo && (!processoId || evento.processo_id === processoId));
}

function Gantt({
  resultado,
  processosEntrada,
  tickVisivel,
}: {
  resultado: Resultado | null;
  processosEntrada: ProcessoEntrada[];
  tickVisivel: number;
}) {
  const linhasProcesso = resultado?.tabela ?? processosEntrada;
  const timeline = resultado?.timeline ?? [];
  const makespan = resultado?.metricas.makespan ?? 0;
  const maxDeadline = linhasProcesso.reduce((maior, processo) => Math.max(maior, processo.deadline), 0);
  const total = resultado ? Math.max(makespan, maxDeadline + 1, 1) : 0;
  const linhas = [
    ...linhasProcesso.map((processo) => ({ tipo: "processo" as const, rotulo: processo.id, processo })),
    { tipo: "sobrecarga" as const, rotulo: "Sobrecarga" },
    { tipo: "ocioso" as const, rotulo: "Ociosa" },
  ];
  const progresso = resultado ? Math.min(100, (tickVisivel / Math.max(total, 1)) * 100) : 0;

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Linha do tempo</p>
          <h2>Gantt</h2>
          <p className="panel-note">{resultado ? `${Math.min(tickVisivel, total)} / ${total} u.t.` : "Aguardando simulacao."}</p>
        </div>
        <div className="legend">
          <span><i className="swatch run" />Execucao</span>
          <span><i className="swatch overhead" />Sobrecarga</span>
          <span><i className="swatch late" />Apos deadline</span>
          <span><i className="deadline-mark" />Deadline</span>
        </div>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progresso}%` }} />
      </div>
      <div className="gantt">
        {!resultado ? (
          <div className="empty-state">
            <strong>Nenhuma execucao ainda.</strong>
            <span>O Gantt sera montado aqui apos a simulacao.</span>
          </div>
        ) : (
          <div className="gantt-grid" style={{ gridTemplateColumns: `120px repeat(${total}, 32px)` }}>
            <div className="gantt-label" style={{ gridColumn: 1, gridRow: 1 }}>Tempo</div>
            {Array.from({ length: total }, (_, tempo) => (
              <div className="time-cell" style={{ gridColumn: tempo + 2, gridRow: 1 }} key={`tempo-${tempo}`}>
                {tempo}
              </div>
            ))}

            {linhas.map((linha, indice) => {
              const gridRow = indice + 2;
              return (
                <React.Fragment key={linha.rotulo}>
                  <div className="gantt-label" style={{ gridColumn: 1, gridRow }}>{linha.rotulo}</div>
                  {Array.from({ length: total }, (_, tempo) => {
                    let classe = "gantt-cell";
                    let texto = "";
                    let deadline = false;
                    const visivel = tempo < tickVisivel;

                    if (linha.tipo === "processo") {
                      deadline = linha.processo.deadline === tempo && visivel;
                      const evento = visivel ? eventoNoTempo(timeline, tempo, "execucao", linha.processo.id) : undefined;
                      if (evento) {
                        classe += tempo >= linha.processo.deadline ? " late" : " run";
                        texto = linha.processo.id;
                      }
                    } else if (visivel && linha.tipo === "sobrecarga" && eventoNoTempo(timeline, tempo, "sobrecarga")) {
                      classe += " overhead";
                    } else if (visivel && linha.tipo === "ocioso" && eventoNoTempo(timeline, tempo, "ocioso")) {
                      classe += " idle";
                    }

                    if (deadline) classe += " deadline";

                    return (
                      <div className={classe} style={{ gridColumn: tempo + 2, gridRow }} key={`${linha.rotulo}-${tempo}`}>
                        {texto}
                      </div>
                    );
                  })}
                </React.Fragment>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}

function Tabela({ resultado, processosEntrada }: { resultado: Resultado | null; processosEntrada: ProcessoEntrada[] }) {
  return (
    <section className="panel">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Processos</p>
          <h2>Tabela final</h2>
        </div>
        <span className="table-count">{resultado ? resultado.tabela.length : processosEntrada.length} linhas</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Chegada</th>
              <th>Execucao</th>
              <th>Deadline</th>
              <th>Prioridade</th>
              <th>Inicio(s)</th>
              <th>Termino</th>
              <th>Espera</th>
              <th>Turnaround</th>
              <th>Deadline OK?</th>
            </tr>
          </thead>
          <tbody>
            {resultado ? (
              resultado.tabela.map((processo) => (
                <tr key={processo.id}>
                  <td>{processo.id}</td>
                  <td>{processo.chegada}</td>
                  <td>{processo.execucao}</td>
                  <td>{processo.deadline}</td>
                  <td>{processo.prioridade}</td>
                  <td>{processo.inicio.join(", ")}</td>
                  <td>{processo.termino}</td>
                  <td>{processo.espera}</td>
                  <td>{processo.turnaround}</td>
                  <td className={processo.deadline_ok ? "status-ok" : "status-bad"}>{processo.deadline_ok ? "Sim" : "Nao"}</td>
                </tr>
              ))
            ) : (
              processosEntrada.map((processo) => (
                <tr className="preview-row" key={processo.id}>
                  <td>{processo.id}</td>
                  <td>{processo.chegada}</td>
                  <td>{processo.execucao}</td>
                  <td>{processo.deadline}</td>
                  <td>{processo.prioridade}</td>
                  <td>-</td>
                  <td>-</td>
                  <td>-</td>
                  <td>-</td>
                  <td>-</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
