import numpy as np
import math


class QLearningAgent:
    """
    Agente que utiliza o algoritmo Q-Learning para gerenciar o consumo de energia.
    """

    def __init__(self, ambiente, alfa=0.1, gama=0.9, epsilon=0.2, tabela_q=None):
        """
        Inicializa o agente com os parâmetros de aprendizado.

        Args:
            ambiente (EnergyManagementEnvironment): O ambiente de gerenciamento de energia.
            alfa (float, optional): Taxa de aprendizado. Padrão é 0.1.
            gama (float, optional): Fator de desconto. Padrão é 0.9.
            epsilon (float, optional): Taxa de exploração. Padrão é 0.2.
            tabela_q (numpy.ndarray, optional): Tabela Q inicial. Se None, é inicializada com zeros.
        """
        self.ambiente = ambiente
        self.alfa = alfa
        self.gama = gama
        self.epsilon = epsilon
        self.numero_dispositivos = len(self.ambiente.dispositivos)
        self.numero_acoes = 2**self.numero_dispositivos
        if self.numero_acoes > 1000:
            raise ValueError(f"Número de ações ({self.numero_acoes}) é muito grande. Reduza o número de dispositivos.")
        self.tabela_q = tabela_q if tabela_q is not None else np.zeros((ambiente.max_tempo, self.numero_acoes))

    def escolher_ação(self, estado):
        """
        Escolhe uma ação com base na política epsilon-greedy.

        Args:
            estado (int): O estado atual.

        Returns:
            int: A ação escolhida.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.randint(self.numero_acoes)
        else:
            return np.argmax(self.tabela_q[estado])

    def decodificar_ação(self, ação):
        """
        Decodifica a ação inteira em uma lista binária representando o estado dos dispositivos.

        Args:
            ação (int): Ação a ser decodificada.

        Returns:
            list: Lista de estados dos dispositivos (0 ou 1).
        """
        return [int(x) for x in format(ação, f"0{self.numero_dispositivos}b")]

    def atualizar_tabela_q(self, estado, ação, recompensa, proximo_estado):
        """
        Atualiza a tabela Q com base na transição de estado.

        Args:
            estado (int): Estado atual.
            ação (int): Ação tomada.
            recompensa (float): Recompensa recebida.
            proximo_estado (int): Próximo estado.
        """
        melhor_proxima_ação = np.argmax(self.tabela_q[proximo_estado])
        self.tabela_q[estado, ação] += self.alfa * (
            recompensa + self.gama * self.tabela_q[proximo_estado, melhor_proxima_ação] - self.tabela_q[estado, ação]
        )

    def treinar(self, numero_epocas=5000, fator_velocidade=1.0):
        """
        Treina o agente usando o algoritmo Q-Learning.

        Args:
            numero_epocas (int, optional): Número de episódios de treinamento. Padrão é 5000.
            fator_velocidade (float, optional): Fator para ajustar a velocidade do treinamento. Padrão é 1.0.

        Returns:
            tuple: Listas de recompensas, consumos e a tabela Q treinada.
        """
        todas_recompensas = []
        todos_consumos = []
        resultados = []

        epocas = math.ceil(numero_epocas / fator_velocidade)

        for epoca in range(epocas):
            estado = self.ambiente.resetar()
            terminado = False
            recompensa_total = 0
            consumo_total = 0

            while not terminado:
                ação = self.escolher_ação(estado)
                ação_decodificada = self.decodificar_ação(ação)
                recompensa, consumo, terminado = self.ambiente.executar_passos(ação_decodificada)
                proximo_estado = self.ambiente.tempo
                self.atualizar_tabela_q(estado, ação, recompensa, proximo_estado)
                estado = proximo_estado
                recompensa_total += recompensa
                consumo_total += consumo

            todas_recompensas.append(recompensa_total)
            todos_consumos.append(consumo_total)

            resultados.append([epoca, ação_decodificada, consumo, sum(todos_consumos)])

            if epoca % 100 == 0:
                print(f"Episódio {epoca} concluído. Recompensa: {recompensa_total:.2f}, Consumo: {consumo_total:.2f} kWh")

        return todas_recompensas, todos_consumos, self.tabela_q

    def atualizar_numero_dispositivos(self):
        """
        Atualiza o número de dispositivos e o número de ações no agente.
        """
        self.numero_dispositivos = len(self.ambiente.dispositivos)
        self.numero_acoes = 2**self.numero_dispositivos

    def simular_dia(self):
        """
        Simula o consumo de energia durante um dia (24 horas).

        Returns:
            tuple: Consumo total e ações tomadas durante a simulação.
        """
        estado = self.ambiente.resetar()
        consumo_total = 0
        acoes_realizadas = []
        for passo in range(24):
            ação = self.escolher_ação(estado)
            ação_decodificada = self.decodificar_ação(ação)
            recompensa, consumo, terminado = self.ambiente.executar_passos(ação_decodificada)
            consumo_total += consumo
            acoes_realizadas.append((passo, ação_decodificada, consumo))
            estado = self.ambiente.tempo
        return consumo_total, acoes_realizadas