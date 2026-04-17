class Ambiente:
    """Simula o ambiente fornecendo percepções complexas ao agente."""
    def __init__(self, alvo=25.0, em_uso=True, lista_temps=None, temp_inicial=25.0):
        self.alvo = alvo
        self.em_uso = em_uso
        self.lista_temps = lista_temps
        # Se for teste oficial, pega a temp da lista. Senão, pega a inicial.
        self.temp_atual = lista_temps[0] if lista_temps else temp_inicial
        self.passo = 0

    def obter_percepcoes(self):
        # Injeta as temperaturas simuladas a cada passo
        if self.lista_temps and self.passo < len(self.lista_temps):
            self.temp_atual = self.lista_temps[self.passo]
            
        return {
            "temperatura_atual": self.temp_atual,
            "temperatura_desejada": self.alvo,
            "janela_uso": self.em_uso
        }

    def aplicar_efeito(self, acao):
        self.passo += 1

class AgenteClimatizacao:
    """Cérebro do sistema: percebe o ambiente e decide a melhor ação."""
    def __init__(self, k=1.0):
        # Intertravamento: Sistemas independentes
        self.estado_resfriador = "DESLIGADO"
        self.estado_aquecedor = "DESLIGADO"
        
        self.tempo_espera = 0
        self.k = k
        
        # Memória para Testes Dinâmicos (Aprendizado)
        self.historico_resfriamento = []
        self.historico_aquecimento = []
        self.acao_escolhida = "manter_sistema()"

    def perceber(self, ambiente):
        # Regra 1: Bloqueio durante a espera (Inércia Térmica)
        if self.tempo_espera > 0:
            self.tempo_espera -= 1
            return {"bloqueado": True}
        return ambiente.obter_percepcoes()

    def decidir(self, percepcao):
        if percepcao.get("bloqueado"):
            self.acao_escolhida = "manter_sistema() (Espera)"
            return self.acao_escolhida

        t_atual = percepcao["temperatura_atual"]
        alvo = percepcao["temperatura_desejada"]
        
        # Regra 5: Define a margem com base na janela de uso
        delta = 0.5 if percepcao["janela_uso"] else 2.0
        
        # Regra 8 e 9: Testes Dinâmicos (Calcula a taxa real ou usa fallback k)
        taxa_resf = sum(self.historico_resfriamento)/len(self.historico_resfriamento) if self.historico_resfriamento else self.k
        taxa_aquec = sum(self.historico_aquecimento)/len(self.historico_aquecimento) if self.historico_aquecimento else self.k

        # Lógica Final e Intertravamento
        if t_atual >= alvo + delta:
            self.estado_resfriador = "LIGADO"
            self.estado_aquecedor = "DESLIGADO"
            self.acao_escolhida = "resfriar()"
            self.tempo_espera = max(1, int((t_atual - alvo) / taxa_resf))
            self.historico_resfriamento.append(0.20)
            
        elif t_atual <= alvo - delta:
            self.estado_resfriador = "DESLIGADO"
            self.estado_aquecedor = "LIGADO"
            self.acao_escolhida = "aquecer()"
            self.tempo_espera = max(1, int((alvo - t_atual) / taxa_aquec))
            self.historico_aquecimento.append(0.20)
            
        else:
            self.estado_resfriador = "DESLIGADO"
            self.estado_aquecedor = "DESLIGADO"
            self.acao_escolhida = "manter_sistema()"

        return self.acao_escolhida

    def agir(self, ambiente):
        ambiente.aplicar_efeito(self.acao_escolhida)
