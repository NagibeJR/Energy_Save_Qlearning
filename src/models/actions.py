class Action:
    """
    Representa uma ação com seu nome e valor Q associado.
    """

    def __init__(self, action: str, q: float):
        self.action = action
        self.q = q
