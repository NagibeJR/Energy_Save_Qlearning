
# Gerenciador de Energia com Q-learning

Este projeto implementa um gerenciador de energia utilizando a técnica de aprendizado por reforço **Q-learning**. O sistema simula o controle de dispositivos eletrônicos em um ambiente doméstico ou empresarial, visando otimizar o consumo de energia ao longo do tempo. O projeto foi desenvolvido em Python, com Tkinter para a interface gráfica (GUI), além de bibliotecas como Numpy e Matplotlib para a lógica de aprendizado e visualização de dados.

## Funcionalidades

- **Simulação de Ambiente com Dispositivos**: Controle dispositivos como ar-condicionado, lâmpadas e outros eletrodomésticos, definindo o consumo de energia de cada um.
- **Treinamento com Q-learning**: O sistema utiliza um agente de Q-learning para aprender a melhor maneira de controlar os dispositivos de acordo com as variações de preços de energia ao longo do dia.
- **Simulação de Consumo Diário**: Após o treinamento, o modelo pode simular o consumo de energia em um dia completo com base nas ações aprendidas.
- **Gráficos de Recompensa e Consumo**: O projeto exibe gráficos em uma janela separada mostrando o progresso do agente durante o treinamento.
- **Exportar Resultados**: O resultado da simulação diária pode ser exportado para um arquivo CSV para posterior análise.

## Tecnologias Utilizadas
- **Tkinter:** Biblioteca padrão para a criação de interfaces gráficas (GUI) em Python.
- **Pandas:** Utilizada para manipulação e análise de dados, especialmente para exportar resultados de simulações para CSV.
- **Matplotlib:** Usada para a criação de gráficos e visualização de dados.
- **Seaborn:** Biblioteca baseada no Matplotlib para criar visualizações estatísticas de forma mais atraente.
- **NumPy:** Biblioteca para suporte a arrays e operações matemáticas de alto desempenho, usada para operações matriciais e cálculos numéricos.

## Estrutura do Projeto

```
energy_management_qlearning_project/
│
├── src/
│   ├── models/
│   │   ├── actions.py
│   │   ├── agent.py
│   │   └── environment.py
│   │
│   ├── views/
│   │   |
│   │   └── energytApp.py
│   │
│   └── main.py
│
├── requirements.txt
└── README.md

```

## Instalação e Configuração

### Requisitos

- Python 3.8 ou superior.
- Virtualenv (opcional, mas recomendado).

### Passos para Instalar

1. **Clone ou Baixe o Projeto**:
   - Clone o repositório ou faça o download dos arquivos.

   ```bash
   git clone https://github.com/NagibeJR/Qlearnig_Project
   cd Qlearnig_Project
   ```

2. **Crie e Ative um Ambiente Virtual (Opcional, mas Recomendado)**:
   - **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instale as Dependências**:
   - Execute o comando abaixo para instalar todas as bibliotecas necessárias.
     ```bash
     pip install -r requirements.txt
     ```

4. **Execute o Projeto**:
   - Inicie a aplicação executando o arquivo `main.py`.
     ```bash
     python main.py
     ```

## Como Usar

1. **Adicionar Dispositivos**:
   - Na interface, insira o nome do dispositivo, o consumo de energia (em W) e a quantidade.
   - Clique em "Adicionar Dispositivo" para incluí-lo na lista de dispositivos a serem gerenciados.

2. **Treinamento**:
   - Para iniciar o treinamento do zero, clique em "Treinar do Zero". Caso já exista uma tabela Q salva, você pode clicar em "Continuar Treinamento" para prosseguir de onde parou.
   - Durante o treinamento, o progresso será exibido no console integrado com detalhes sobre recompensas e consumo.

3. **Simular o Consumo Diário**:
   - Após o treinamento, clique em "Simular Consumo em um Dia" para executar uma simulação baseada nas ações aprendidas pelo agente, exibindo o consumo total ao longo de um dia.

4. **Visualizar Gráficos**:
   - Para observar o desempenho do treinamento, clique em "Exibir Gráfico". Uma nova janela será aberta com gráficos que mostram a recompensa acumulada e o consumo de energia ao longo dos episódios.

5. **Exportar Resultados da Simulação**:
   - Após a simulação, clique em "Exportar Resultados" para salvar os resultados em um arquivo CSV, permitindo uma análise posterior.

## Estrutura da Interface

- **Treinamento**: Configurações para iniciar e continuar o treinamento, além de controles de perfil de usuário e velocidade.
- **Dispositivos**: Adicione dispositivos com consumo de energia, quantidade e visualize/remova da lista.
- **Console**: Console integrado para monitorar o progresso das operações.
- **Gráficos**: Visualize o progresso do agente com gráficos de recompensa e consumo.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

