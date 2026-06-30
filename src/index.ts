import { Processo } from "./core/Processo";

const processo = new Processo({
  id: "P1",
  chegada: 0,
  execucao: 5,
  prioridade: 2,
  deadline: 8,
});

console.log("Processo criado:");
console.log(processo);

processo.registrarInicio(0);
processo.executar(5);
processo.finalizar(5);

console.log("Após execução:");
console.log({
  id: processo.id,
  inicio: processo.inicio,
  termino: processo.termino,
  restante: processo.restante,
  turnaround: processo.calcularTurnaround(),
  espera: processo.calcularEspera(),
  deadlineOk: processo.deadlineOk,
});