#include <iostream>
#include <vector>
#include <algorithm>

// Estrutura simples para exportar o estado de cada processo para a IA
struct DadosProcessoIA {
    int id;
    int tempo_chegada;
    int burst_total;
    int tempo_restante;
    int tempo_espera_atual;
};

struct Processo {
    int id;
    int tempo_chegada;
    int burst_total;
    int tempo_restante;
    int tempo_inicio;
    int tempo_conclusao;
    int tempo_espera;
    int tempo_turnaround;

    Processo(int _id, int _chegada, int _burst) 
        : id(_id), tempo_chegada(_chegada), burst_total(_burst), 
          tempo_restante(_burst), tempo_inicio(-1), tempo_conclusao(0), 
          tempo_espera(0), tempo_turnaround(0) {}
};

class MotorSimulacao {
private:
    int clock_atual;
    std::vector<Processo> processos_futuros;
    std::vector<Processo*> fila_prontos;
    Processo* processo_em_execucao;
    std::vector<Processo> processos_concluidos;
    int indice_chegada;
    // Guardas para o cálculo da recompensa
    double penalidade_espera_acumulada;

public:
    MotorSimulacao() : clock_atual(0), processo_em_execucao(nullptr), penalidade_espera_acumulada(0.0), indice_chegada(0) {}

    int obter_clock_atual() const { return clock_atual; }

    void adicionar_processo(int id, int chegada, int burst) {
        processos_futuros.push_back(Processo(id, chegada, burst));
    }

    void preparar_simulacao() {
        std::sort(processos_futuros.begin(), processos_futuros.end(), 
            [](const Processo& a, const Processo& b) { return a.tempo_chegada < b.tempo_chegada; });
    }

    // --- PORTA DE SAÍDA: VERIFICAÇÃO DE ESTADO ---
    // Indica se o simulador precisa que a IA tome uma decisão neste ciclo de clock
    bool precisa_de_decisao() {
        // Se a CPU estiver livre (ou se quisermos preempção a cada ciclo) e houver processos na fila
        return (processo_em_execucao == nullptr && !fila_prontos.empty());
    }

    // Retorna a lista de processos prontos formatada para a IA ler
    std::vector<DadosProcessoIA> obter_estado_fila() {
        std::vector<DadosProcessoIA> estado;
        for (auto* p : fila_prontos) {
            DadosProcessoIA dados;
            dados.id = p->id;
            dados.tempo_chegada = p->tempo_chegada;
            dados.burst_total = p->burst_total;
            dados.tempo_restante = p->tempo_restante;
            dados.tempo_espera_atual = clock_atual - p->tempo_chegada;
            estado.push_back(dados);
        }
        return estado;
    }

    // --- PORTA DE ENTRADA: APLICAÇÃO DA AÇÃO ---
    // A IA escolhe o índice do processo dentro da lista gerada por 'obter_estado_fila'
    void aplicar_acao(int idx_escolhido) {
        if (idx_escolhido < 0 || idx_escolhido >= static_cast<int>(fila_prontos.size())) {
            std::cerr << "Erro: Ação inválida escolhida pela IA!" << std::endl;
            return;
        }

        // Remove o processo escolhido da fila de prontos e coloca na CPU
        processo_em_execucao = fila_prontos[idx_escolhido];
        fila_prontos.erase(fila_prontos.begin() + idx_escolhido);

        if (processo_em_execucao->tempo_inicio == -1) {
            processo_em_execucao->tempo_inicio = clock_atual;
        }
    }

    // --- PORTA DE FEEDBACK: CÁLCULO DA RECOMPENSA ---
    // Retorna o feedback do último passo para guiar o aprendizado do agente
    double obter_recompensa() {
        // Exemplo de recompensa negativa: penaliza o tamanho da fila e o tempo que as pessoas esperam
        double recompensa = -1.0 * fila_prontos.size();
        
        // Se houver processos esperando há muito tempo, aplica uma penalidade extra
        for (auto* p : fila_prontos) {
            int espera = clock_atual - p->tempo_chegada;
            if (espera > 10) { // Limiar arbitrário para evitar starvation
                recompensa -= 0.5;
            }
        }
        return recompensa;
    }

    // Executa a lógica interna de passagem do tempo (1 tick)
    bool avancar_clock() {
        // 1. Atualiza novos processos que chegaram
        while (indice_chegada < processos_futuros.size() && processos_futuros[indice_chegada].tempo_chegada == clock_atual) {
            fila_prontos.push_back(&processos_futuros[indice_chegada]);
            indice_chegada++;
        }

        // 2. Se houver processo na CPU, consome 1 ciclo
        if (processo_em_execucao != nullptr) {
            processo_em_execucao->tempo_restante--;

            // Se terminou, limpa a CPU para a IA escolher o próximo no próximo ciclo
            if (processo_em_execucao->tempo_restante == 0) {
                processo_em_execucao->tempo_conclusao = clock_atual + 1;
                processo_em_execucao->tempo_turnaround = processo_em_execucao->tempo_conclusao - processo_em_execucao->tempo_chegada;
                processo_em_execucao->tempo_espera = processo_em_execucao->tempo_turnaround - processo_em_execucao->burst_total;
                
                processos_concluidos.push_back(*processo_em_execucao);
                processo_em_execucao = nullptr; 
            }
        }

        clock_atual++;
        
        // Retorna true se a simulação global ainda não acabou
        return !(indice_chegada >= processos_futuros.size() && fila_prontos.empty() && processo_em_execucao == nullptr);
    }
};
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Muito importante: converte std::vector do C++ para listas do Python automaticamente

namespace py = pybind11;

// "motor_simulacao" será o nome do módulo que importaremos no Python
PYBIND11_MODULE(motor_simulacao, m) {
    m.doc() = "Motor de simulacao de escalonamento em C++ de alta performance";

    // Exportando a struct de dados
    py::class_<DadosProcessoIA>(m, "DadosProcessoIA")
        .def_readonly("id", &DadosProcessoIA::id)
        .def_readonly("tempo_chegada", &DadosProcessoIA::tempo_chegada)
        .def_readonly("burst_total", &DadosProcessoIA::burst_total)
        .def_readonly("tempo_restante", &DadosProcessoIA::tempo_restante)
        .def_readonly("tempo_espera_atual", &DadosProcessoIA::tempo_espera_atual);

    // Exportando a classe principal e seus métodos
    py::class_<MotorSimulacao>(m, "MotorSimulacao")
        .def(py::init<>()) // Construtor padrão
        .def("adicionar_processo", &MotorSimulacao::adicionar_processo)
        .def("preparar_simulacao", &MotorSimulacao::preparar_simulacao)
        .def("precisa_de_decisao", &MotorSimulacao::precisa_de_decisao)
        .def("obter_estado_fila", &MotorSimulacao::obter_estado_fila)
        .def("aplicar_acao", &MotorSimulacao::aplicar_acao)
        .def("obter_recompensa", &MotorSimulacao::obter_recompensa)
        .def("avancar_clock", &MotorSimulacao::avancar_clock)
        .def("obter_clock_atual", &MotorSimulacao::obter_clock_atual);
}