class Action:
    """
    Representa uma ação com seu nome e valor Q associado.
    """

    def __init__(self, nome_ação: str, valor_q: float):
        self.nome_ação = nome_ação
        self.valor_q = valor_q
