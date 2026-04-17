# Especificação do agente inteligente para controle de temperatura

## 1. Percepções do agente

### Sensores
O agente observa os seguintes elementos do ambiente:

- temperatura atual da sala;
- temperatura desejada configurada pelo usuário;
- umidade do ambiente;
- presença ou ausência de pessoas na sala;
- estado interno do sistema: ligado ou desligado;
- tempo atual;
- janela de uso da sala;
- histórico de variações de temperatura.

### Ações
O agente pode executar as seguintes ações:

- `ligar_sistema()`: ativa o sistema de climatização;
- `desligar_sistema()`: desativa o sistema de climatização;
- `manter_sistema()`: mantém o estado atual;
- `aquecer()`: eleva a temperatura quando o ambiente estiver abaixo do ideal;
- `resfriar()`: reduz a temperatura quando o ambiente estiver acima do ideal.

## 2. Variáveis de controle

- `temperatura_atual`: temperatura medida no ambiente;
- `temperatura_desejada`: temperatura configurada pelo usuário;
- `Δ`: margem de oscilação aceitável;
- `limite_superior = temperatura_desejada + Δ`;
- `limite_inferior = temperatura_desejada - Δ`;
- `tempo_espera`: intervalo definido para evitar leituras e mudanças desnecessárias;
- `taxa_resfriamento`: velocidade com que a temperatura cai quando o sistema está ligado;
- `taxa_aquecimento`: velocidade com que a temperatura sobe quando o sistema está desligado;
- `k`: constante de fallback quando ainda não há aprendizado suficiente.

## 3. Memória do agente

O agente armazena em memória:

- o último estado do sistema;
- a última temperatura registrada;
- a temperatura desejada;
- a margem de oscilação;
- o histórico de resfriamentos;
- o histórico de aquecimentos;
- o tempo de espera entre mudanças;
- os registros da janela de uso da sala;
- os resultados dos testes dinâmicos de aprendizagem.

## 4. Histórico aprendido

O agente mantém registros para aprender com o comportamento do ambiente, incluindo:

- histórico de decaimentos de temperatura;
- histórico de aquecimentos;
- tempo necessário para atingir certos intervalos;
- resposta do ambiente quando o sistema liga ou desliga;
- eficiência da climatização em diferentes horários;
- comportamento da sala quando está sendo usada e quando está vazia.

Esse histórico permite estimar melhor o momento certo de ligar, desligar, resfriar ou aquecer.

## 5. Janela de uso da sala

O agente considera uma janela de uso para saber quando a sala está sendo utilizada e quando não está.

### Quando a sala está em uso
- prioriza manter a temperatura próxima da desejada;
- reage mais rapidamente às variações;
- evita desconforto térmico.

### Quando a sala não está em uso
- pode aceitar uma faixa de temperatura mais ampla;
- reduz a frequência de acionamento do sistema;
- economiza energia.

Essa informação pode ser obtida por presença de pessoas, horário de uso ou ambos.

## 6. Regras de decisão

### Regra 1 Espera antes da nova leitura
Antes de fazer uma nova leitura, o agente verifica se ainda existe tempo de espera.

Se `tempo_espera > 0`:
- não lê os sensores;
- diminui o contador de espera;
- executa `manter_sistema()`.

### Regra 2 Leitura dos sensores
Se não houver espera:
- lê `temperatura_atual`;
- lê `temperatura_desejada`;
- lê o estado do sistema;
- lê a presença de pessoas;
- lê a janela de uso.

### Regra 3 Registro da leitura
Cada leitura é armazenada para permitir aprendizado posterior:

- temperatura;
- estado do sistema;
- horário;
- presença;
- uso da sala.

### Regra 4 Atualização da aprendizagem
O agente calcula e atualiza:

- taxa de resfriamento;
- taxa de aquecimento;
- histórico de decaimentos;
- tempo médio de resposta do ambiente.

### Regra 5 Ligar o sistema
Se:

- `temperatura_atual > temperatura_desejada + Δ`
- e o sistema estiver desligado

então:

- `ligar_sistema()`

Se já estiver ligado:
- `manter_sistema()`

### Regra 6 — Desligar o sistema
Se:

- `temperatura_atual ≤ temperatura_desejada - Δ`
- e o sistema estiver ligado

então:

- `desligar_sistema()`

### Regra 7 Aquecer
Se:

- `temperatura_atual < temperatura_desejada - Δ`

então:

- executar `aquecer()`, quando esse recurso estiver disponível no sistema.

### Regra 8 Resfriar
Se:

- `temperatura_atual > temperatura_desejada + Δ`

então:

- executar `resfriar()`, quando esse recurso estiver disponível no sistema.

### Regra 9 Manter estado
Se nenhuma condição for atendida:

- `manter_sistema()`

### Regra 10 Execução e atualização
Após decidir:

- executa a ação;
- atualiza o estado interno;
- registra o resultado no histórico.

## 7. Evitar microciclos de oscilação

Para evitar liga/desliga excessivo, o agente define um tempo mínimo de espera entre mudanças de estado.

### Regra de espera mínima
Após uma mudança de estado:
- o agente não pode tomar uma nova decisão imediata;
- ele espera um intervalo mínimo antes de reavaliar.

Isso reduz:
- consumo de energia;
- desgaste do equipamento;
- oscilações curtas e repetitivas.

## 8. Espera durante resfriamento

Se o sistema estiver ligado, o agente calcula quanto tempo deve esperar antes da próxima leitura.

Se já aprendeu:

tempo = (temperatura_atual - temperatura_desejada) / taxa_resfriamento

Senão:


tempo = k . (temperatura_atual - temperatura_desejada)

Onde `k` é uma constante de fallback.

## 9. Testes dinâmicos para aprendizagem

O agente realiza testes dinâmicos para melhorar sua estimativa do comportamento térmico do ambiente.

Esses testes servem para:

- medir quanto tempo a temperatura leva para cair;
- medir quanto tempo a temperatura leva para subir;
- observar o efeito real do sistema em diferentes horários;
- ajustar a taxa de resfriamento e a taxa de aquecimento.

Assim, o agente aprende com o uso real da sala e melhora suas decisões ao longo do tempo.

## 10. Temperatura de resfriamento

O agente pode trabalhar com uma temperatura de resfriamento em pequenos passos, por exemplo:

- resfriar de `0,20°C` em `0,20°C`;
- ou aquecer de `0,20°C` em `0,20°C`.

Isso significa que a alteração térmica pode ser controlada em incrementos menores, evitando mudanças bruscas.

Esse comportamento ajuda a:
- estabilizar o ambiente;
- reduzir oscilações;
- tornar o controle mais preciso.

## 11. Comportamento racional

O agente é considerado racional porque:

- mantém a temperatura da sala próxima da desejada;
- respeita a margem de oscilação definida;
- evita liga/desliga excessivo;
- reduz gasto de energia sempre que possível;
- reage quando a temperatura sobe demais ou cai demais;
- aprende com o histórico do ambiente;
- adapta seu comportamento à janela de uso da sala.

## 12. Resposta a diferentes cenários

- **Temperatura alta:** liga e resfria o ambiente;
- **Temperatura ideal:** mantém o sistema;
- **Temperatura baixa:** desliga ou aquece, conforme o contexto;
- **Sala em uso:** prioriza conforto;
- **Sala sem uso:** prioriza economia de energia.

## 13. Lógica final do sistema

Liga quando:


temperatura_atual >= temperatura_desejada + Δ

Desliga quando:

temperatura_atual <= temperatura_desejada - Δ

Mantém quando:

temperatura_desejada - Δ < temperatura_atual < temperatura_desejada + Δ

Resfria quando:

temperatura_atual > temperatura_desejada + Δ

Aquece quando:

temperatura_atual < temperatura_desejada - Δ


