class EnergyManagementEnvironment:
    """
    Ambiente para gerenciamento de energia residencial utilizando Q-Learning.
    """

    DISPOSITIVOS_PRIORITARIOS = ["geladeira", "frigobar"]

    def __init__(self, lista_dispositivos, preco_energia=None, max_tempo=24, hora_dormir=None, hora_acordar=None):
        """
        Inicializa o ambiente com uma lista de dispositivos e preços de energia.

        Args:
            lista_dispositivos (list): Lista de dispositivos no formato [(nome, consumo, quantidade), ...].
            preco_energia (list, optional): Lista de preços de energia por hora. Se None, usa padrão.
            max_tempo (int, optional): Número máximo de etapas (horas) no ambiente. Padrão é 24.
            hora_dormir (int, optional): Hora de dormir. Padrão é 22.
            hora_acordar (int, optional): Hora de acordar. Padrão é 6.
        """
        self.dispositivos = self.gerar_dispositivos(lista_dispositivos)
        self.tempo = 0
        self.max_tempo = max_tempo
        self.hora_dormir = hora_dormir
        self.hora_acordar = hora_acordar 
        self.preco_energia = preco_energia if preco_energia else [0.5 if 22 <= i < 5 else 0.2 for i in range(self.max_tempo)]

    def gerar_dispositivos(self, lista_dispositivos):
        """
        Gera um dicionário de dispositivos a partir da lista fornecida.

        Args:
            lista_dispositivos (list): Lista de dispositivos no formato [(nome, consumo, quantidade), ...].

        Returns:
            dict: Dicionário de dispositivos com seus consumos e estados.

        Raises:
            ValueError: Se o formato de lista_dispositivos estiver incorreto ou se consumo/quantidade forem inválidos.
        """
        dispositivos = {}
        for dispositivo in lista_dispositivos:
            nome_dispositivo, consumo, quantidade = dispositivo
            for i in range(1, quantidade + 1):
                nome_unico = f"{nome_dispositivo}_{i}"
                dispositivos[nome_unico] = {"consumo": consumo, "estado": 0}
        return dispositivos

    def remover_dispositivo(self, nome_dispositivo):
        """
        Remove um dispositivo da lista de dispositivos.

        Args:
            nome_dispositivo (str): Nome do dispositivo a ser removido.
        """
        dispositivos_correspondentes = [d for d in self.dispositivos if nome_dispositivo in d]

        if dispositivos_correspondentes:
            # Remover todos os dispositivos que contenham o nome passado (para múltiplas instâncias)
            for dispositivo in dispositivos_correspondentes:
                del self.dispositivos[dispositivo]
        else:
            raise ValueError(f"Dispositivo {nome_dispositivo} não encontrado.")

    def resetar(self):
        """
        Reseta o ambiente para o estado inicial.

        Returns:
            int: Estado inicial (tempo).
        """
        self.tempo = 0
        for dispositivo in self.dispositivos:
            self.dispositivos[dispositivo]["estado"] = 0
        return self.tempo

    def calcular_limite_consumo(self):
        consumo_dispositivos = sum(dispositivo["consumo"] for dispositivo in self.dispositivos.values())
        limite_base = consumo_dispositivos * 0.5
        return limite_base

    def executar_passos(self, acoes):
        """
        Executa uma ação no ambiente, atualizando os estados dos dispositivos e calculando recompensas.

        Args:
            acoes (list): Lista de estados (0 ou 1) para cada dispositivo.

        Returns:
            tuple: Recompensa obtida, consumo total, e flag indicando se o episódio terminou.
        """
        consumo_total = 0
        recompensa = 0

        for i, dispositivo in enumerate(self.dispositivos):
            if any(prio in dispositivo.lower() for prio in self.DISPOSITIVOS_PRIORITARIOS):
                if self.tempo % 3 == 0:
                    self.dispositivos[dispositivo]["estado"] = 1
                else:
                    self.dispositivos[dispositivo]["estado"] = 0
            else:
                self.dispositivos[dispositivo]["estado"] = acoes[i]

                if self.hora_dormir < self.hora_acordar:
                    desligar = self.hora_dormir <= self.tempo <= self.hora_acordar
                else:
                    desligar = self.tempo >= self.hora_dormir or self.tempo <= self.hora_acordar

                if desligar:
                    self.dispositivos[dispositivo]["estado"] = 0
                else:
                    self.dispositivos[dispositivo]["estado"] = acoes[i]

            consumo_total += (self.dispositivos[dispositivo]["consumo"] / 1000) * self.dispositivos[dispositivo]["estado"]

        limite_consumo = self.calcular_limite_consumo()
        excesso_consumo = consumo_total - limite_consumo
        if excesso_consumo > 0:
            if excesso_consumo < 0.5:
                penalidade_consumo = excesso_consumo * 20 
            elif excesso_consumo < 1.0:
                penalidade_consumo = excesso_consumo * 40 
            else:
                penalidade_consumo = excesso_consumo * 60
            recompensa -= penalidade_consumo
        else:
            recompensa += 20 

        if self.hora_dormir <= self.tempo or self.tempo < self.hora_acordar:
            if consumo_total <= limite_consumo * 0.7:
                recompensa += 10

        for dispositivo in self.dispositivos:
            if self.dispositivos[dispositivo]["estado"] == 1:
                if any(prio in dispositivo.lower() for prio in self.DISPOSITIVOS_PRIORITARIOS):
                    recompensa += 5
                else:
                    recompensa += 2

        self.tempo = (self.tempo + 1) % self.max_tempo

        return recompensa, consumo_total, self.tempo == 0
