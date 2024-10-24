import numpy as np
import math


class QLearningAgent:
    """
    Agente que utiliza o algoritmo Q-Learning para gerenciar o consumo de energia.
    """

    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.2, q_table=None):
        """
        Inicializa o agente com os parâmetros de aprendizado.

        Args:
            env (EnergyManagementEnvironment): O ambiente de gerenciamento de energia.
            alpha (float, optional): Taxa de aprendizado. Padrão é 0.1.
            gamma (float, optional): Fator de desconto. Padrão é 0.9.
            epsilon (float, optional): Taxa de exploração. Padrão é 0.2.
            q_table (numpy.ndarray, optional): Tabela Q inicial. Se None, é inicializada com zeros.
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.num_devices = len(self.env.devices)
        self.num_actions = 2**self.num_devices
        self.q_table = (
            q_table
            if q_table is not None
            else np.zeros((env.max_time, self.num_actions))
        )

    def choose_action(self, state):
        """
        Escolhe uma ação com base na política epsilon-greedy.

        Args:
            state (int): O estado atual.

        Returns:
            int: A ação escolhida.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            return np.argmax(self.q_table[state])

    def decode_action(self, action):
        """
        Decodifica a ação inteira em uma lista binária representando o estado dos dispositivos.

        Args:
            action (int): Ação a ser decodificada.

        Returns:
            list: Lista de estados dos dispositivos (0 ou 1).
        """
        return [int(x) for x in format(action, f"0{self.num_devices}b")]

    def update_q_table(self, state, action, reward, next_state):
        """
        Atualiza a tabela Q com base na transição de estado.

        Args:
            state (int): Estado atual.
            action (int): Ação tomada.
            reward (float): Recompensa recebida.
            next_state (int): Próximo estado.
        """
        best_next_action = np.argmax(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (reward + self.gamma * self.q_table[next_state, best_next_action] - self.q_table[state, action])

    def train(self, num_episodes=1000, speed_factor=1.0):
        """
        Treina o agente usando o algoritmo Q-Learning.

        Args:
            num_episodes (int, optional): Número de episódios de treinamento. Padrão é 1000.
            speed_factor (float, optional): Fator para ajustar a velocidade do treinamento. Padrão é 1.0.

        Returns:
            tuple: Listas de recompensas, consumos e a tabela Q treinada.
        """
        all_rewards = []
        all_consumptions = []
        results = []

        episodes = math.ceil(num_episodes / speed_factor)

        for episode in range(episodes):
            state = self.env.reset()
            done = False
            total_reward = 0
            total_consumption = 0

            while not done:
                action = self.choose_action(state)
                decoded_action = self.decode_action(action)
                reward, consumption, done = self.env.step(decoded_action)
                next_state = self.env.tempo
                self.update_q_table(state, action, reward, next_state)
                state = next_state
                total_reward += reward
                total_consumption += consumption

            all_rewards.append(total_reward)
            all_consumptions.append(total_consumption)

            results.append([episode, decoded_action, consumption, sum(all_consumptions)])

            if episode % 100 == 0:
                print(f"Episódio {episode} concluído. Recompensa: {total_reward:.2f}, Consumo: {total_consumption:.2f} kWh")

        return all_rewards, all_consumptions, self.q_table

    def simulate_day(self):
        """
        Simula o consumo de energia durante um dia (24 horas).

        Returns:
            tuple: Consumo total e ações tomadas durante a simulação.
        """
        state = self.env.reset()
        total_consumption = 0
        actions_taken = []
        for step in range(24):
            action = self.choose_action(state)
            decoded_action = self.decode_action(action)
            reward, consumption, done = self.env.step(decoded_action)
            total_consumption += consumption
            actions_taken.append((step, decoded_action, consumption))
            state = self.env.tempo
        return total_consumption, actions_taken
