# Simulador de Escalonamento SO

Aplicacao web em React/TSX com backend Python para simular algoritmos de escalonamento de processos.

## Requisitos

- Python 3
- Node.js e npm

## Instalar dependencias

```bash
cd src
npm install
```

## Rodar a aplicacao

Opcao mais simples, subindo backend e frontend juntos:

```bash
cd src
npm run dev
```

Depois acesse:

```text
http://127.0.0.1:5173
```

Tambem e possivel rodar separado.

Terminal 1, backend Python:

```bash
cd src
npm run backend
```

Terminal 2, frontend Vite:

```bash
cd src
npm run frontend
```

Se o backend ja estiver rodando, use apenas `npm run frontend`.

## Simulacoes disponiveis

A interface chama o backend em tempo real e aceita processos editados no JSON. Algoritmos disponiveis:

- FIFO / FCFS
- SJF
- Round-Robin
- Prioridades
- EDF
- CFS-Sim
- IA Autoral

Campos principais da entrada JSON:

```json
{
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "processos": [
    { "id": "P1", "chegada": 0, "execucao": 5, "deadline": 8, "prioridade": 2 }
  ]
}
```
