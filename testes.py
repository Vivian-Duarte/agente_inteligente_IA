class Ambiente:
    def __init__(self, alvo=25.0, em_uso=True, lista_temps=None, temp_inicial=25.0):
        self.alvo = alvo
        self.em_uso = em_uso
        self.lista_temps = lista_temps
        # Pega a primeira temperatura da lista do professor
        self.temp_atual = lista_temps[0] if lista_temps else temp_inicial
        self.passo = 0

    def obter_percepcoes(self):
        # Injeta as temperaturas do professor a cada passo
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
    def __init__(self, k=1.0):
        self.estado_resfriador = "DESLIGADO"
        self.estado_aquecedor = "DESLIGADO"
        self.tempo_espera = 0
        self.k = k
        self.historico_resfriamento = []
        self.historico_aquecimento = []
        self.acao_escolhida = "manter_sistema()"

    def perceber(self, ambiente):
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
        delta = 0.5 if percepcao["janela_uso"] else 2.0
        
        taxa_resf = sum(self.historico_resfriamento)/len(self.historico_resfriamento) if self.historico_resfriamento else self.k
        taxa_aquec = sum(self.historico_aquecimento)/len(self.historico_aquecimento) if self.historico_aquecimento else self.k

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

def rodar_teste(nome, lista_temps, alvo=25.0, em_uso=True, interpretacao=""):
    print(f"\n{'='*90}")
    print(f"CENÁRIO: {nome}")
    print(f"Lista de Entradas: {lista_temps}")
    print(f"{'-'*90}")
    print(f"{'Passo':<6} | {'Temp. Lida':<12} | {'Ação do Agente':<25} | {'Resfriador':<11} | {'Aquecedor'}")
    print(f"{'-'*90}")
    
    ambiente = Ambiente(alvo=alvo, em_uso=em_uso, lista_temps=lista_temps)
    agente = AgenteClimatizacao()
    
    for _ in range(len(lista_temps)):
        percepcao = agente.perceber(ambiente)
        agente.decidir(percepcao)
        agente.agir(ambiente)
        
        temp_log = f"{ambiente.temp_atual:.1f}°C" if not percepcao.get("bloqueado") else "Ignorado"
        print(f" {ambiente.passo-1:<5} | {temp_log:<12} | {agente.acao_escolhida:<25} | {agente.estado_resfriador:<11} | {agente.estado_aquecedor}")
    
    if interpretacao:
        print(f"\n> ANÁLISE CRÍTICA DO COMPORTAMENTO:\n{interpretacao}")


# ====================================================================
# PARTE 3 - TESTES OFICIAIS DO PROFESSOR
# ====================================================================
print("\n" + "#"*90)
print("PARTE 3 - TESTES OFICIAIS")
print("A TEMPERATURA DESEJADA ESTÁ COMO 25 graus")
print("#"*90)

# Cenário 1 — Oscilação
rodar_teste(
    nome="Cenário 1 — Oscilação", 
    lista_temps=[24.9, 25.1, 24.8, 25.2], 
    interpretacao="O agente mantém o sistema desligado porque nenhum limite de calor ou de frio é ultrapassado. As temperaturas lidas variam entre 24.8 °C e 25.2 °C, que estão perfeitamente dentro da margem aceitável (entre 24.5 °C e 25.5 °C, conforme a Seção 13 do readme). Como a sala está em uso, a Regra 5 determina que ele priorize o conforto, ignorando essas pequenas oscilações para não acionar o sistema desnecessariamente e economizar energia."
)

# Cenário 2 — Calor extremo
rodar_teste(
    nome="Cenário 2 — Calor extremo", 
    lista_temps=[30, 32, 35], 
    interpretacao="O agente liga o resfriador assim que o limite de calor é ultrapassado. Neste cenário, a leitura do ambiente foi de 30.0 °C, o que ultrapassa o Limite Superior aceitável de 25.5 °C (calculado pela Temperatura Desejada de 25.0 °C + a Margem Δ de 0.5 °C). Esta matemática do Limite Superior está definida na Seção 2 e na Seção 13 (Lógica final) do readme. Depois, entra em modo de 'Espera'. Conforme a Regra 1 e a Seção 7 do readme (Evitar microciclos), o modo espera bloqueia intencionalmente novas leituras dos sensores por um tempo para dar tempo que o equipamento faça efeito físico na sala, não repetindo o mesmo comando desnecessariamente e evitando o desgaste do motor."
)

# Cenário 3 — Resfriamento gradual
rodar_teste(
    nome="Cenário 3 — Resfriamento Gradual e Intertravamento", 
    lista_temps=[28, 27, 26, 25, 24], 
    interpretacao="Este cenário mapeia o ciclo de vida completo de uma climatização. O agente inicia combatendo o calor ativando o resfriamento. Ao cruzar os 25 °C, ele entra em modo passivo. O clímax lógico ocorre no passo final: quando a temperatura cai bruscamente para 24.0 °C (rompendo o limite inferior de 24.5 °C), o agente aplica a lógica de intertravamento. Ele desliga completamente o módulo resfriador e aciona imediatamente o módulo aquecedor, provando sua capacidade de adaptação dinâmica a quedas drásticas de temperatura no ambiente."
)