import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox
from models.agent import QLearningAgent
from models.environment import EnergyManagementEnvironment
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class EnergyManagementApp:
    """
    Interface gráfica para o gerenciador de energia utilizando Q-Learning.
    """
    def __init__(self, master):
        self.master = master
        self.agente = None
        self.tabela_q = None
        self.dispositivos = []
        self.recompensas = []
        self.consumos = []
        self.resultados_simulacao = []
        self.ambiente = None
        self.acoes_realizadas = []
        self.estados_dispositivos = {}
        self.quantidades_dispositivos = {}
        self.criar_widgets()

    def criar_widgets(self):
        """
        Cria os widgets da interface gráfica.
        """
        # Configuração geral da janela para ser redimensionável
        self.master.grid_rowconfigure(0, weight=2)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

        # Frame para Configurações do Ambiente
        self.frame_configuracoes = ttk.LabelFrame(self.master, text="Configurações do Ambiente")
        self.frame_configuracoes.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_configuracoes.grid_columnconfigure(1, weight=1)

        # Seção "Gerenciar Horários"
        self.frame_horarios = ttk.LabelFrame(self.frame_configuracoes, text="Gerenciar Horários", padding=(10, 5))
        self.frame_horarios.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.frame_horarios.grid_columnconfigure((1, 3), weight=1)  # Configurar colunas 1 e 3 para expansão

        # Hora de Dormir
        self.label_hora_dormir = ttk.Label(self.frame_horarios, text="Hora de Dormir (0-23):")
        self.label_hora_dormir.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.spinbox_hora_dormir = ttk.Spinbox(self.frame_horarios, from_=0, to=23, width=5)
        self.spinbox_hora_dormir.set(22)  # Valor padrão
        self.spinbox_hora_dormir.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Hora de Acordar
        self.label_hora_acordar = ttk.Label(self.frame_horarios, text="Hora de Acordar (0-23):")
        self.label_hora_acordar.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.spinbox_hora_acordar = ttk.Spinbox(self.frame_horarios, from_=0, to=23, width=5)
        self.spinbox_hora_acordar.set(6)  # Valor padrão
        self.spinbox_hora_acordar.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Área de Entrada e Gerenciamento de Dispositivos
        self.frame_dispositivos = ttk.LabelFrame(self.frame_configuracoes, text="Gerenciamento de Dispositivos", padding=(10, 5))
        self.frame_dispositivos.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.frame_dispositivos.grid_columnconfigure(1, weight=1)

        # Nome do dispositivo
        self.label_nome_dispositivo = ttk.Label(self.frame_dispositivos, text="Nome do Dispositivo:")
        self.label_nome_dispositivo.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome_dispositivo = ttk.Entry(self.frame_dispositivos)
        self.entry_nome_dispositivo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Potência (W)
        self.label_potencia = ttk.Label(self.frame_dispositivos, text="Potência (W):")
        self.label_potencia.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_potencia = ttk.Entry(self.frame_dispositivos)
        self.entry_potencia.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Botão Adicionar Dispositivo
        self.botao_adicionar_dispositivo = ttk.Button(self.frame_dispositivos, text="Adicionar Dispositivo", command=self.adicionar_dispositivo)
        self.botao_adicionar_dispositivo.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        # Mensagem de feedback para validação de entrada de dados
        self.label_feedback = ttk.Label(self.frame_dispositivos, text="", foreground="red")
        self.label_feedback.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Lista de dispositivos adicionados com área de rolagem
        self.label_lista_dispositivos = ttk.Label(self.frame_dispositivos, text="Dispositivos Adicionados:")
        self.label_lista_dispositivos.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Frame para a lista de dispositivos com scroll
        self.frame_lista_dispositivos = ttk.Frame(self.frame_dispositivos)
        self.frame_lista_dispositivos.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.frame_lista_dispositivos.grid_rowconfigure(0, weight=1)
        self.frame_lista_dispositivos.grid_columnconfigure(0, weight=1)

        # Canvas para rolagem
        self.canvas_dispositivos = tk.Canvas(self.frame_lista_dispositivos, borderwidth=0, height=100)
        self.scrollbar_dispositivos = ttk.Scrollbar(self.frame_lista_dispositivos, orient="vertical", command=self.canvas_dispositivos.yview)
        self.scrollable_frame_dispositivos = ttk.Frame(self.canvas_dispositivos)

        self.scrollable_frame_dispositivos.bind("<Configure>", lambda e: self.canvas_dispositivos.configure(scrollregion=self.canvas_dispositivos.bbox("all")))

        self.canvas_dispositivos.create_window((0, 0), window=self.scrollable_frame_dispositivos, anchor="nw")
        self.canvas_dispositivos.configure(yscrollcommand=self.scrollbar_dispositivos.set)

        self.canvas_dispositivos.pack(side="left", fill="both", expand=True)
        self.scrollbar_dispositivos.pack(side="right", fill="y")

        # Inicialização da lista de widgets de dispositivos
        self.widgets_dispositivos = []

        # Frame para Controles de Treinamento e Simulação
        self.frame_controle = ttk.LabelFrame(self.master, text="Controles de Treinamento e Simulação")
        self.frame_controle.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_controle.grid_columnconfigure(0, weight=1)
        self.frame_controle.grid_columnconfigure(1, weight=1)

        # Botões de controle
        self.botao_treinar_do_zero = ttk.Button(self.frame_controle, text="Treinar do Zero", command=self.treinar_do_zero)
        self.botao_treinar_do_zero.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.botao_continuar_treinamento = ttk.Button(self.frame_controle, text="Continuar Treinamento", command=self.continuar_treinamento)
        self.botao_continuar_treinamento.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.botao_simular = ttk.Button(self.frame_controle, text="Simular Consumo em um Dia", command=self.simular_dia)
        self.botao_simular.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.botao_mostrar_simulacao = ttk.Button(self.frame_controle, text="Mostrar Simulação", command=self.mostrar_grafico_simulacao_e_estados_dispositivos)
        self.botao_mostrar_simulacao.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.botao_mostrar_tabela_q = ttk.Button(self.frame_controle, text="Mostrar Tabela Q", command=self.mostrar_tabela_q)
        self.botao_mostrar_tabela_q.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.botao_mostrar_grafico = ttk.Button(self.frame_controle, text="Mostrar Gráficos de Treinamento", command=self.mostrar_grafico_treinamento)
        self.botao_mostrar_grafico.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Frame para Console e Status
        self.frame_output = ttk.LabelFrame(self.master, text="Console e Status")
        self.frame_output.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_output.grid_rowconfigure(0, weight=1)
        self.frame_output.grid_columnconfigure(0, weight=1)

        # Console de saída
        self.texto_console = tk.Text(self.frame_output, state="disabled", height=5, wrap="word")
        self.texto_console.pack(padx=5, pady=5, fill="both", expand=True)

        # Status do sistema
        self.label_status = ttk.Label(self.frame_output, text="Status: Aguardando...", foreground="blue")
        self.label_status.pack(padx=5, pady=5, anchor="w")

    def adicionar_dispositivo(self):
        """
        Adiciona um novo dispositivo à lista de dispositivos.
        """
        try:
            nome_dispositivo = self.entry_nome_dispositivo.get().strip()
            potencia_dispositivo = float(self.entry_potencia.get())

            if not nome_dispositivo:
                self.label_feedback.config(text="Erro: Nome do dispositivo é obrigatório.", foreground="red")
                return
            if potencia_dispositivo <= 0:
                self.label_feedback.config(text="Erro: Potência deve ser um número positivo.", foreground="red")
                return

            if nome_dispositivo in self.quantidades_dispositivos:
                self.label_feedback.config(text="Erro: Dispositivo já existe. Use os botões para alterar a quantidade.", foreground="red")
                return

            total_dispositivos = sum(self.quantidades_dispositivos.values())
            if total_dispositivos + 1 > 9:
                self.label_feedback.config(text="Erro: Limite máximo de 9 dispositivos no total atingido.", foreground="red")
                return

            # Adicionar o novo dispositivo com quantidade 1
            dispositivo = (nome_dispositivo, potencia_dispositivo, 1)
            self.dispositivos.append(dispositivo)
            self.quantidades_dispositivos[nome_dispositivo] = 1

            self.atualizar_lista_dispositivos()
            self.label_feedback.config(text=f"Dispositivo '{nome_dispositivo}' adicionado com sucesso!", foreground="green")
            self.entry_nome_dispositivo.delete(0, tk.END)
            self.entry_potencia.delete(0, tk.END)

        except ValueError:
            self.label_feedback.config(text="Erro: Potência deve ser um número válido.", foreground="red")

    def atualizar_lista_dispositivos(self):
        """
        Atualiza a lista de dispositivos na interface gráfica.
        """
        # Limpar widgets anteriores
        for widget in self.widgets_dispositivos:
            widget.destroy()
        self.widgets_dispositivos = []

        for i, (nome_dispositivo, potencia, _) in enumerate(self.dispositivos):
            quantidade = self.quantidades_dispositivos[nome_dispositivo]

            self.dispositivos[i] = (nome_dispositivo, potencia, quantidade)

            frame_dispositivo = ttk.Frame(self.scrollable_frame_dispositivos)
            frame_dispositivo.pack(fill="x", padx=5, pady=2)

            label_dispositivo = ttk.Label( frame_dispositivo, text=f"{nome_dispositivo} | Potência: {potencia} W | Quantidade: {quantidade}")
            label_dispositivo.pack(side="left", padx=(0, 10))

            botao_incrementar = ttk.Button( frame_dispositivo, text="+", width=3, command=lambda nome=nome_dispositivo: self.incrementar_quantidade(nome))
            botao_incrementar.pack(side="left", padx=(0, 5))

            botao_decrementar = ttk.Button(frame_dispositivo, text="-", width=3, command=lambda nome=nome_dispositivo: self.decrementar_quantidade(nome))
            botao_decrementar.pack(side="left")

            self.widgets_dispositivos.append(frame_dispositivo)

    def incrementar_quantidade(self, nome_dispositivo):
        """
        Incrementa a quantidade de dispositivos, até o máximo de 8 para cada dispositivo.
        Verifica se o total de dispositivos não ultrapassa o limite de 9.
        """
        total_dispositivos = sum(self.quantidades_dispositivos.values())

        if total_dispositivos < 9 and self.quantidades_dispositivos[nome_dispositivo] < 8:
            self.quantidades_dispositivos[nome_dispositivo] += 1
            self.atualizar_lista_dispositivos()
            self.label_feedback.config(text="Quantidade do dispositivo incrementada com sucesso!", foreground="green")
        else:
            if self.quantidades_dispositivos[nome_dispositivo] >= 8:
                self.label_feedback.config(text="Erro: Limite máximo de 8 unidades para este dispositivo.", foreground="red")
            else:
                self.label_feedback.config(text="Erro: Limite máximo de 9 dispositivos no total atingido.", foreground="red")

    def decrementar_quantidade(self, nome_dispositivo):
        """
        Decrementa a quantidade de dispositivos, até o mínimo de 1.
        Remove o dispositivo se a quantidade chegar a 0.
        """
        if self.quantidades_dispositivos[nome_dispositivo] > 1:
            self.quantidades_dispositivos[nome_dispositivo] -= 1
            self.label_feedback.config(text="Quantidade do dispositivo decrementada com sucesso!", foreground="green")
        else:
            self.remover_dispositivo_por_nome(nome_dispositivo)
            self.label_feedback.config(text="Dispositivo removido com sucesso!", foreground="green")
        self.atualizar_lista_dispositivos()

    def remover_dispositivo_por_nome(self, nome_dispositivo):
        """
        Remove o dispositivo da lista com base no nome.
        """
        self.dispositivos = [d for d in self.dispositivos if d[0] != nome_dispositivo]
        del self.quantidades_dispositivos[nome_dispositivo]
        self.atualizar_lista_dispositivos()
        self.label_feedback.config(text="Dispositivo removido com sucesso!", foreground="green")

    def remover_dispositivo_por_indice(self, indice):
        """
        Remove um dispositivo da lista com base no índice.
        """
        try:
            nome_dispositivo = self.dispositivos[indice][0]
            del self.dispositivos[indice]
            del self.quantidades_dispositivos[nome_dispositivo]
            self.atualizar_lista_dispositivos()
            if self.ambiente:
                self.ambiente.remover_dispositivo(nome_dispositivo)
            if self.agente:
                self.agente.atualizar_numero_dispositivos()
            self.label_status.config(text="Dispositivo removido com sucesso!", foreground="green")
        except IndexError:
            self.label_status.config(text="Erro ao remover dispositivo.", foreground="red")

    def treinar_do_zero(self):
        """
        Inicia o treinamento do agente a partir do zero, reiniciando a Q-table.
        """
        confirmar = messagebox.askyesno("Confirmar", "Isso irá reiniciar a tabela Q. Deseja continuar?")
        if confirmar:
            self.tabela_q = None
            self.iniciar_treinamento()

    def continuar_treinamento(self):
        """
        Continua o treinamento do agente a partir da Q-table existente.
        """
        if self.tabela_q is None:
            self.treinar_do_zero()
        else:
            try:
                self.iniciar_treinamento()
            except ValueError as ve:
                messagebox.showerror("Erro ao Continuar Treinamento", "Ocorreu um erro durante o treinamento. Por favor, reinicie o treinamento.")

    def iniciar_treinamento(self):
        """
        Configura e inicia o processo de treinamento do agente.
        """
        if not self.dispositivos:
            self.label_status.config(text="Adicione pelo menos um dispositivo.", foreground="red")
            return

        try:
            hora_dormir = int(self.spinbox_hora_dormir.get())
            hora_acordar = int(self.spinbox_hora_acordar.get())
            if hora_dormir == hora_acordar:
                raise ValueError("Hora de dormir e acordar não podem ser iguais.")
        except ValueError as ve:
            messagebox.showerror("Erro de Validação", f"Valores inválidos para horas: {ve}")
            return

        self.limpar_console()
        self.ambiente = EnergyManagementEnvironment(lista_dispositivos=self.dispositivos, hora_dormir=hora_dormir, hora_acordar=hora_acordar)
        self.agente = QLearningAgent(self.ambiente, tabela_q=self.tabela_q)
        self.agente.atualizar_numero_dispositivos()

        try:
            recompensas, consumos, self.tabela_q = self.agente.treinar()
            self.recompensas = recompensas
            self.consumos = consumos

            self.texto_console.config(state="normal")
            self.texto_console.insert(tk.END, f"Treinamento concluído. Recompensas: {recompensas[-1]:.2f}, Consumo: {consumos[-1]:.2f} kWh\n")
            self.texto_console.config(state="disabled")
            self.label_status.config(text="Treinamento concluído!", foreground="green")

        except ValueError as ve:
            if "Número de ações deve corresponder ao número de dispositivos" in str(ve):
                messagebox.showerror("Erro de Treinamento", "O número de ações não corresponde ao número de dispositivos. Por favor, reinicie o treinamento.")
            else:
                messagebox.showerror("Erro", str(ve))

    def simular_dia(self, acoes_personalizadas=None):
        """
        Simula o consumo de energia durante um dia.
        """
        if self.tabela_q is None:
            self.label_status.config(text="Por favor, treine o modelo antes de simular.", foreground="red")
            return

        if not self.ambiente:
            self.ambiente = EnergyManagementEnvironment(self.dispositivos)

        consumo_total = 0
        self.acoes_realizadas = [] 
        self.estados_dispositivos = {dispositivo: [] for dispositivo in self.ambiente.dispositivos}

        estado = self.ambiente.resetar()

        try:
            for passo in range(24):
                if acoes_personalizadas and passo < len(acoes_personalizadas):
                    ação = acoes_personalizadas[passo]
                else:
                    ação = self.agente.escolher_ação(estado)

                ação_decodificada = self.agente.decodificar_ação(ação)
                recompensa, consumo, terminado = self.ambiente.executar_passos(ação_decodificada)
                consumo_total += consumo

                self.acoes_realizadas.append((passo, ação_decodificada, consumo))
                estado = self.ambiente.tempo

                for dispositivo in self.ambiente.dispositivos:
                    self.estados_dispositivos[dispositivo].append(self.ambiente.dispositivos[dispositivo]["estado"])

            self.texto_console.config(state="normal")
            self.texto_console.insert(tk.END, f"Simulação concluída! Consumo total: {consumo_total:.2f} kWh\n")
            self.texto_console.config(state="disabled")
            self.label_status.config(text=f"Simulação concluída! Consumo total: {consumo_total:.2f} kWh", foreground="green")

        except ValueError as ve:
            if "Número de ações deve corresponder ao número de dispositivos" in str(ve):
                messagebox.showerror("Erro de Simulação", "O número de ações não corresponde ao número de dispositivos. Por favor, treine o modelo novamente.")
            else:
                messagebox.showerror("Erro", str(ve))

    def mostrar_grafico_treinamento(self):
        """
        Exibe os gráficos de recompensas e consumo durante o treinamento.
        """
        if not self.recompensas or not self.consumos:
            self.label_status.config(text="Por favor, realize um treinamento antes de exibir o gráfico.", foreground="red")
            return

        janela_grafico = tk.Toplevel(self.master)
        janela_grafico.title("Gráficos de Recompensas e Consumo")

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        epocas = range(len(self.recompensas))

        recompensas_suavizadas = np.convolve(self.recompensas, np.ones(10)/10, mode='valid')
        consumos_suavizados = np.convolve(self.consumos, np.ones(10)/10, mode='valid')

        ax[0].plot(epocas[:len(recompensas_suavizadas)], recompensas_suavizadas, label="Recompensa Acumulada (suavizada)", color="blue", linewidth=2)
        ax[0].set_xlabel("Episódios")
        ax[0].set_ylabel("Recompensa Total")
        ax[0].set_title("Progresso da Recompensa Durante o Treinamento")
        ax[0].grid(True)
        ax[0].legend()

        ax[1].plot(epocas[:len(consumos_suavizados)], consumos_suavizados, label="Consumo de Energia (suavizado)", color="orange", linewidth=2)
        ax[1].set_xlabel("Episódios")
        ax[1].set_ylabel("Consumo Total (kWh)")
        ax[1].set_title("Consumo de Energia Durante o Treinamento")
        ax[1].grid(True)
        ax[1].legend()

        ax[0].set_ylim([min(recompensas_suavizadas) - 10, max(recompensas_suavizadas) + 10])
        ax[1].set_ylim([min(consumos_suavizados) - 0.2, max(consumos_suavizados) + 0.2])

        canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def mostrar_grafico_simulacao_e_estados_dispositivos(self):
        """
        Mostra ambos os gráficos: consumo total e estados dos dispositivos.
        """
        if not self.acoes_realizadas or not self.estados_dispositivos:
            self.label_status.config(text="Por favor, realize a simulação antes de visualizar os gráficos.", foreground="red")
            return

        self.mostrar_grafico_simulacao(self.acoes_realizadas)
        self.mostrar_grafico_estados_dispositivos(self.estados_dispositivos)

    def mostrar_grafico_simulacao(self, acoes_realizadas):
        """
        Exibe o gráfico de consumo total ao longo do dia.

        Args:
            acoes_realizadas (list): Lista de ações tomadas durante a simulação.
        """
        passos = [passo for passo, _, _ in acoes_realizadas]
        consumos = [consumo for _, _, consumo in acoes_realizadas]
        consumo_acumulado = [sum(consumos[: i + 1]) for i in range(len(consumos))]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(passos, consumo_acumulado, marker="o", label="Consumo Total (kWh)")
        ax.set_title("Consumo de Energia ao Longo do Dia")
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Consumo Total (kWh)")
        ax.set_xticks(passos)
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        janela_grafico = tk.Toplevel(self.master)
        janela_grafico.title("Gráfico de Simulação")

        canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def mostrar_grafico_estados_dispositivos(self, estados_dispositivos):
        """
        Exibe o gráfico de estados dos dispositivos ao longo do dia.

        Args:
            estados_dispositivos (dict): Dicionário com os estados dos dispositivos por hora.
        """
        if not estados_dispositivos or all(len(estados) == 0 for estados in estados_dispositivos.values()):
            messagebox.showerror("Erro", "Nenhum dado de estado dos dispositivos encontrado. Por favor, realize a simulação.")
            return

        horas = range(24)
        numero_dispositivos = len(estados_dispositivos)
        matriz_estados = []

        for dispositivo, estados in estados_dispositivos.items():
            if len(estados) != len(horas):
                messagebox.showerror("Erro", f"Dispositivo {dispositivo} tem um número incorreto de estados. Esperado: {len(horas)}, Recebido: {len(estados)}")
                return
            matriz_estados.append(estados)

        matriz_estados = list(map(list, zip(*matriz_estados)))
        array_estados = np.array(matriz_estados)

        if array_estados.shape[0] != len(horas):
            messagebox.showerror("Erro", f"Incompatibilidade entre o número de horas ({len(horas)}) e o número de estados ({array_estados.shape[0]}).")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        base_estados = np.zeros(len(horas))
        nomes_dispositivos = list(estados_dispositivos.keys())

        for i in range(numero_dispositivos):
            ax.bar(horas, array_estados[:, i], bottom=base_estados, label=nomes_dispositivos[i])
            base_estados += array_estados[:, i]

        ax.set_title("Estados dos Dispositivos ao Longo do Dia")
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Estado do Dispositivo (0=Desligado, 1=Ligado)")
        ax.set_xticks(horas)
        ax.set_xticklabels([f"{i}:00" for i in horas], rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        ax.legend(title="Dispositivos")
        fig.tight_layout()

        janela_grafico = tk.Toplevel(self.master)
        janela_grafico.title("Estados dos Dispositivos")

        canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def mostrar_tabela_q(self):
        """
        Exibe a Q-table em uma nova janela.
        """
        if self.tabela_q is None:
            self.label_status.config(text="Por favor, realize o treinamento antes de visualizar a Q-table.", foreground="red")
            return

        janela_q_table = tk.Toplevel(self.master)
        janela_q_table.title("Visualização da Q-table")
        texto_q_table = tk.Text(janela_q_table, wrap="none", height=20, width=60)
        texto_q_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        tabela_q_str = "\n".join(["\t".join([f"{q:.2f}" for q in linha]) for linha in self.tabela_q])
        texto_q_table.insert(tk.END, f"Q-table:\n{tabela_q_str}")
        texto_q_table.config(state="disabled")

    def limpar_console(self):
        """
        Limpa o console de saída.
        """
        self.texto_console.config(state="normal")
        self.texto_console.delete("1.0", tk.END)
        self.texto_console.config(state="disabled")
