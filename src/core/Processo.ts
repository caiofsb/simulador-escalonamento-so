export type ProcessoInput = {
  id: string;
  chegada: number;
  execucao: number;
  prioridade: number;
  deadline: number;
  num_paginas?: number;
};

export class Processo {
  id: string;
  chegada: number;
  execucao: number;
  prioridade: number;
  deadline: number;
  num_paginas?: number;

  restante: number;
  inicio: number[];
  termino: number | null;
  vruntime: number;
  deadlineOk: boolean | null;

  constructor(dados: ProcessoInput) {
    this.id = dados.id;
    this.chegada = dados.chegada;
    this.execucao = dados.execucao;
    this.prioridade = dados.prioridade;
    this.deadline = dados.deadline;
    this.num_paginas = dados.num_paginas;

    this.restante = dados.execucao;
    this.inicio = [];
    this.termino = null;
    this.vruntime = 0;
    this.deadlineOk = null;
  }

  registrarInicio(tempo: number): void {
    this.inicio.push(tempo);
  }

  executar(tempo: number): void {
    if (tempo <= 0) {
      throw new Error("O tempo de execução deve ser maior que zero.");
    }

    this.restante -= tempo;

    if (this.restante < 0) {
      this.restante = 0;
    }
  }

  finalizar(tempo: number): void {
    this.termino = tempo;
    this.deadlineOk = tempo <= this.deadline;
  }

  estaFinalizado(): boolean {
    return this.restante <= 0;
  }

  calcularTurnaround(): number | null {
    if (this.termino === null) {
      return null;
    }

    return this.termino - this.chegada;
  }

  calcularEspera(): number | null {
    const turnaround = this.calcularTurnaround();

    if (turnaround === null) {
      return null;
    }

    return turnaround - this.execucao;
  }

  clonar(): Processo {
    return new Processo({
      id: this.id,
      chegada: this.chegada,
      execucao: this.execucao,
      prioridade: this.prioridade,
      deadline: this.deadline,
      num_paginas: this.num_paginas,
    });
  }
}