import numpy as np


class EnergyManagementEnvironment:
    def __init__(self, device_list, user_profile="economico"):
        """
        device_list: list of tuples where each tuple contains (device_name, consumption, quantity)
                      Example: [("ar_condicionado", 3, 2), ("lampadas", 0.1, 4)]
        """
        self.devices = self.generate_devices(device_list)
        self.tempo = 0  # Representa a hora do dia (0 a 23)
        self.max_time = 24  # Há 24 horas no dia

        # Configurações de perfil de usuário
        self.profiles = {
            "economico": 0.5,  # Prefere economia, penaliza menos o consumo
            "conforto": 1.0,  # Prefere conforto, penaliza mais o consumo
            "balanceado": 0.75,  # Balanceia entre economia e conforto
        }
        self.user_profile = self.profiles.get(
            user_profile, 0.5
        )  # Default to "economico"

        # Preços de energia dinâmica (mais realista)
        self.preco_energia = [
            0.5 if 12 <= i < 18 else 0.2 for i in range(24)
        ]  # Preços simulados por hora

    def generate_devices(self, device_list):
        devices = {}
        for device_name, consumption, quantity in device_list:
            for i in range(1, quantity + 1):
                unique_name = f"{device_name}_{i}"
                devices[unique_name] = {"consumo": consumption, "estado": 0}
        return devices

    def reset(self):
        # Reinicia o ambiente
        self.tempo = 0
        for device in self.devices:
            self.devices[device]["estado"] = 0
        # Manter geladeira ligada inicialmente, se for o caso
        for device in self.devices:
            if "geladeira" in device.lower():
                self.devices[device]["estado"] = 1
        return self.tempo  # Retorna o estado inicial

    def step(self, actions):
        # Atualiza o estado dos dispositivos com base nas ações
        for i, device in enumerate(self.devices):
            self.devices[device]["estado"] = actions[i]

        # Calcula o consumo de energia atual
        consumo_total = sum(
            [
                self.devices[d]["consumo"] * self.devices[d]["estado"]
                for d in self.devices
            ]
        )
        custo_energia = consumo_total * self.preco_energia[self.tempo]

        # Calcula a recompensa com base no perfil do usuário
        reward = -custo_energia * self.user_profile

        # Avança o tempo
        self.tempo = (
            self.tempo + 1
        ) % self.max_time  # Garante que 'tempo' sempre estará entre 0 e 23

        return (
            reward,
            consumo_total,
            self.tempo == 0,
        )  # Retorna o novo estado (tempo atual) e se o episódio terminou
