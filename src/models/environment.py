class EnergyManagementEnvironment:
    """
    Ambiente para gerenciamento de energia residencial utilizando Q-Learning.
    """

    PRIORITY_DEVICES = ["geladeira", "frigobar"]

    def __init__(self, device_list, preco_energia=None, max_time=24):
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
        # Preço da energia por hora
        self.preco_energia = (
            preco_energia
            if preco_energia
            else [0.5 if 12 <= i < 18 else 0.2 for i in range(self.max_time)]
        )

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
            if not isinstance(device, (list, tuple)) or len(device) != 3:
                raise ValueError("Cada dispositivo deve ser uma tupla/lista com 3 elementos: (nome, consumo, quantidade).")
            device_name, consumption, quantity = device
            if (not isinstance(device_name, str) or not isinstance(consumption, (int, float)) or not isinstance(quantity, int)): 
                raise ValueError("Nome deve ser uma string, consumo um número e quantidade um inteiro.")
            if consumption <= 0 or quantity <= 0:
                raise ValueError("Consumo e quantidade devem ser números positivos.")
            for i in range(1, quantity + 1):
                unique_name = f"{device_name}_{i}"
                devices[unique_name] = {"consumo": consumption,"estado": 0}
        return devices

    def reset(self):
        """
        Reseta o ambiente para o estado inicial.

        Returns:
            int: Estado inicial (tempo).
        """
        self.tempo = 0
        for device in self.devices:
            self.devices[device]["estado"] = 0
        for device in self.devices:
            if any(prio in device.lower() for prio in self.PRIORITY_DEVICES):
                self.devices[device]["estado"] = 1
        return self.tempo

    def step(self, actions):
        """
        Executa uma ação no ambiente, atualizando os estados dos dispositivos e calculando recompensas.

        Args:
            actions (list): Lista de estados (0 ou 1) para cada dispositivo.

        Returns:
            tuple: Recompensa obtida, consumo total, e flag indicando se o episódio terminou.
        """
        if len(actions) != len(self.devices):
            raise ValueError("Número de ações deve corresponder ao número de dispositivos.")

        for i, device in enumerate(self.devices):
            self.devices[device]["estado"] = actions[i]

        # Calcular o consumo total
        consumo_total = sum((self.devices[d]["consumo"] / 1000) * self.devices[d]["estado"] for d in self.devices)

        # Recompensa baseada na prioridade dos dispositivos
        reward = 0
        for device in self.devices:
            if self.devices[device]["estado"] == 1:  # Se o dispositivo está ligado
                if any(prio in device.lower() for prio in self.PRIORITY_DEVICES):
                    reward += 10  # Bônus maior para dispositivos prioritários
                else:
                    reward += 5  # Bônus padrão para outros dispositivos

        # Penalização para consumo excessivo
        if consumo_total > 5:  # Penalizar mais fortemente para consumo maior que 5kWh
            reward -= (
                consumo_total - 5
            ) * 20  # Penalização mais severa para consumo alto

        # Penalizar uso em horário de energia cara (12h às 18h)
        if 12 <= self.tempo < 18:
            reward -= (
                consumo_total * 10
            )  # Penalização extra para consumo em horário caro

        # Atualiza o tempo
        self.tempo = (self.tempo + 1) % self.max_time

        return reward, consumo_total, self.tempo == 0
