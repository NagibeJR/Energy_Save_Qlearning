import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.2, q_table=None):
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
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            return np.argmax(self.q_table[state])

    def decode_action(self, action):
        return [int(x) for x in format(action, f"0{self.num_devices}b")]

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (
            reward
            + self.gamma * self.q_table[next_state, best_next_action]
            - self.q_table[state, action]
        )

    def train(self, num_episodes=1000, speed_factor=1.0):
        all_rewards = []
        all_consumptions = []
        results = []  # Para armazenar resultados da simulação diária

        for episode in range(int(num_episodes / speed_factor)):
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

            # Armazenar resultados da simulação diária
            results.append(
                [episode, decoded_action, consumption, sum(all_consumptions)]
            )

            if episode % 100 == 0:
                print(
                    f"Episódio {episode} concluído. Recompensa: {total_reward:.2f}, Consumo: {total_consumption:.2f} kWh"
                )

        return all_rewards, all_consumptions, self.q_table

    def plot_results(self, all_rewards, all_consumptions):
        # Definindo os limites de consumo
        low_threshold = 1.5  # Limite para consumo baixo (kWh)
        high_threshold = 2.5  # Limite para consumo alto (kWh)

        # Classificando os consumos em categorias
        categories = []
        for consumption in all_consumptions:
            if consumption < low_threshold:
                categories.append("Baixo")
            elif consumption < high_threshold:
                categories.append("Médio")
            else:
                categories.append("Alto")

        # Convertendo para um array numpy para facilitar o uso
        categories = np.array(categories)

        # Contando o número de episódios em cada categoria
        counts = {
            "Baixo": np.sum(categories == "Baixo"),
            "Médio": np.sum(categories == "Médio"),
            "Alto": np.sum(categories == "Alto"),
        }

        # Gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(counts.keys(), counts.values(), color=["green", "orange", "red"])
        plt.title("Distribuição de Consumo por Categoria", fontsize=16)
        plt.xlabel("Categoria de Consumo", fontsize=12)
        plt.ylabel("Número de Episódios", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Adicionando alertas
        for idx, value in enumerate(counts.values()):
            plt.text(idx, value + 0.1, str(value), ha="center", fontsize=12)

        plt.tight_layout()
        plt.show()

        # Gráfico de recompensas
        plt.figure(figsize=(14, 6))
        plt.plot(
            all_rewards,
            label="Recompensa Total",
            color="blue",
            linestyle="-",
            marker="o",
        )
        plt.title("Recompensa Total por Episódio", fontsize=16)
        plt.xlabel("Episódio", fontsize=12)
        plt.ylabel("Recompensa", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def simulate_day(self):
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
