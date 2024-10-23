import numpy as np


class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.2, q_table=None):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # Número de dispositivos
        self.num_devices = len(self.env.devices)

        # Número de combinações de ações possíveis (2^n onde n é o número de dispositivos)
        self.num_actions = 2**self.num_devices

        # A tabela Q tem uma linha para cada estado (24 horas no dia) e uma coluna para cada possível ação
        if q_table is None:
            self.q_table = np.zeros((env.max_time, self.num_actions))
        else:
            self.q_table = q_table  # Reutiliza a tabela Q de treinamentos anteriores

    def choose_action(self, state):
        # Epsilon-greedy: escolher aleatoriamente ou a melhor ação
        if np.random.uniform(0, 1) < self.epsilon:
            # Escolher uma ação aleatória (inteiro representando uma combinação de ações)
            return np.random.randint(self.num_actions)
        else:
            # Escolher a melhor ação com base na tabela Q
            return np.argmax(self.q_table[state])

    def decode_action(self, action):
        # Decodifica a ação de volta em uma lista binária que corresponde ao estado de cada dispositivo
        return [int(x) for x in format(action, f"0{self.num_devices}b")]

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (
            reward
            + self.gamma * self.q_table[next_state, best_next_action]
            - self.q_table[state, action]
        )

    def train(self, num_episodes=1000, speed_factor=1.0):
        all_rewards = []  # Para armazenar as recompensas por episódio
        all_consumptions = []  # Para armazenar o consumo por episódio

        for episode in range(int(num_episodes / speed_factor)):
            state = self.env.reset()  # Estado inicial (tempo = 0)
            done = False
            total_reward = 0
            total_consumption = 0

            while not done:
                # Escolha uma ação (um inteiro que representa uma combinação de ações)
                action = self.choose_action(state)

                # Decodifique a ação para aplicar ao ambiente (ex: [1, 0, 1, 0, ...] para dispositivos)
                decoded_action = self.decode_action(action)

                # Execute a ação no ambiente
                reward, consumption, done = self.env.step(decoded_action)

                # O próximo estado é o novo tempo (de 0 a 23)
                next_state = self.env.tempo

                # Atualize a tabela Q com base no estado e ação
                self.update_q_table(state, action, reward, next_state)
                state = next_state  # Atualize o estado para a próxima iteração

                total_reward += reward
                total_consumption += consumption

            all_rewards.append(total_reward)
            all_consumptions.append(total_consumption)

            if episode % 100 == 0:
                print(
                    f"Episódio {episode} concluído. Recompensa: {total_reward:.2f}, Consumo: {total_consumption:.2f} kWh"
                )

        # Retorne os resultados do treinamento para análise posterior
        return all_rewards, all_consumptions, self.q_table

    def simulate_day(self):
        """Simula um dia de uso do agente já treinado, com base nas ações aprendidas"""
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
