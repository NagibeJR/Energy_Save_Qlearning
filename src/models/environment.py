class EnergyManagementEnvironment:
    def __init__(self, device_list):
        self.devices = self.generate_devices(device_list)
        self.tempo = 0
        self.max_time = 24
        self.preco_energia = [0.5 if 12 <= i < 18 else 0.2 for i in range(24)]

    def generate_devices(self, device_list):
        devices = {}
        for device_name, consumption, quantity in device_list:
            for i in range(1, quantity + 1):
                unique_name = f"{device_name}_{i}"
                devices[unique_name] = {
                    "consumo": consumption,
                    "estado": 0,
                }
        return devices

    def reset(self):
        self.tempo = 0
        for device in self.devices:
            self.devices[device]["estado"] = 0
        for device in self.devices:
            if "geladeira" in device.lower():
                self.devices[device]["estado"] = 1
        return self.tempo

    def step(self, actions):
        for i, device in enumerate(self.devices):
            self.devices[device]["estado"] = actions[i]

        # Calcular o consumo total em kWh
        consumo_total = sum(
            [
                (self.devices[d]["consumo"] / 1000) * self.devices[d]["estado"]  # Convertendo watts para kWh
                for d in self.devices
            ]
        )

        # Custo de energia baseado no consumo total
        custo_energia = consumo_total * self.preco_energia[self.tempo]

        # Recompensa baseada em limites de consumo
        if consumo_total < 2:  # Recompensa maior para consumo baixo
            reward = 10 - 2 * custo_energia
        elif consumo_total < 3:  # Recompensa intermediária para consumo moderado
            reward = 5 - 3 * custo_energia
        else:  # Penalização para consumo alto
            reward = -5 * custo_energia

        # Atualiza o tempo
        self.tempo = (self.tempo + 1) % self.max_time

        return reward, consumo_total, self.tempo == 0
