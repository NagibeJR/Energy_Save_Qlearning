class EnergyManagementEnvironment:
    """
    Ambiente para gerenciamento de energia residencial utilizando Q-Learning.
    """

    PRIORITY_DEVICES = [
        "geladeira", "geladeira_1", "geladeira_2", "geladeira_3", "geladeira_4", "geladeira_5", "geladeira_6", "geladeira_7", "geladeira_8", 
        "Geladeira","Geladeira_1", "Geladeira_2", "Geladeira_3", "Geladeira_4", "Geladeira_5", "Geladeira_6", "Geladeira_7", "Geladeira_8",
        "frigobar", "frigobar_1", "frigobar_2", "frigobar_3", "frigobar_4", "frigobar_5", "frigobar_6", "frigobar_7", "frigobar_8",
        "Frigobar", "Frigobar_1", "Frigobar_2", "Frigobar_3", "Frigobar_4", "Frigobar_5", "Frigobar_6", "Frigobar_7", "Frigobar_8"]

    def __init__(self, device_list, preco_energia=None, max_time=24,  hora_dormir=22, hora_acordar=6):
        """
        Inicializa o ambiente com uma lista de dispositivos e preços de energia.

        Args:
            device_list (list): Lista de dispositivos no formato [(nome, consumo, quantidade), ...].
            preco_energia (list, optional): Lista de preços de energia por hora. Se None, usa padrão.
            max_time (int, optional): Número máximo de etapas (horas) no ambiente.
        """
        self.devices = self.generate_devices(device_list)
        self.tempo = 0
        self.max_time = max_time
        self.hora_dormir = hora_dormir
        self.hora_acordar = hora_acordar 
        self.preco_energia = (preco_energia if preco_energia else [0.5 if 22 <= i < 5 else 0.2 for i in range(self.max_time)])

    def generate_devices(self, device_list):
        """
        Gera um dicionário de dispositivos a partir da lista fornecida.

        Args:
            device_list (list): Lista de dispositivos no formato [(nome, consumo, quantidade), ...].

        Returns:
            dict: Dicionário de dispositivos com seus consumos e estados.

        Raises:
            ValueError: Se o formato de device_list estiver incorreto ou se consumo/quantidade forem inválidos.
        """
        devices = {}
        for device in device_list:
            device_name, consumption, quantity = device
            for i in range(1, quantity + 1):
                unique_name = f"{device_name}_{i}"
                devices[unique_name] = {"consumo": consumption, "estado": 0}
        return devices

    def remove_device(self, device_name):
        """
        Remove um dispositivo da lista de dispositivos.

        Args:
            device_name (str): Nome do dispositivo a ser removido.
        """
        matching_devices = [d for d in self.devices if device_name in d]

        if matching_devices:
            # Remover todos os dispositivos que contenham o nome passado (para múltiplas instâncias)
            for device in matching_devices:
                del self.devices[device]
        else:
            raise ValueError(f"Dispositivo {device_name} não encontrado.")

    def reset(self):
        """
        Reseta o ambiente para o estado inicial.

        Returns:
            int: Estado inicial (tempo).
        """
        self.tempo = 0
        for device in self.devices:
            self.devices[device]["estado"] = 0
        return self.tempo

    def step(self, actions):
        """
        Executa uma ação no ambiente, atualizando os estados dos dispositivos e calculando recompensas.

        Args:
            actions (list): Lista de estados (0 ou 1) para cada dispositivo.

        Returns:
            tuple: Recompensa obtida, consumo total, e flag indicando se o episódio terminou.
        """
        consumo_total = 0
        reward = 0

        for i, device in enumerate(self.devices):
            if device in self.PRIORITY_DEVICES:
                if self.tempo % 2 == 0:
                    self.devices[device]["estado"] = 1
                else:
                    self.devices[device]["estado"] = 0
            else:
                self.devices[device]["estado"] = actions[i]

                if self.hora_dormir <= self.tempo or self.tempo < self.hora_acordar:
                    self.devices[device]["estado"] = 0

        consumo_total += (self.devices[device]["consumo"] / 1000) * self.devices[device]["estado"]

        reward = 0
        for device in self.devices:
            if self.devices[device]["estado"] == 1:
                if any(prio in device.lower() for prio in self.PRIORITY_DEVICES):
                    reward += 10 
                else:
                    reward += 5

        if consumo_total > 5:
            reward -= (consumo_total - 5) * 20

        if self.tempo >= 22 or self.tempo < 5:
            reward -= consumo_total * 15

        self.tempo = (self.tempo + 1) % self.max_time

        return reward, consumo_total, self.tempo == 0
