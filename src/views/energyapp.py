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
        self.agent = None
        self.q_table = None
        self.devices = []
        self.rewards = []
        self.consumptions = []
        self.simulation_results = []
        self.env = None
        self.actions_taken = []
        self.device_states = {}
        self.create_widgets()

    def create_widgets(self):
        """
        Cria os widgets da interface gráfica.
        """
        # Tornar a janela redimensionável
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Frames principais
        self.control_frame = ttk.LabelFrame(self.master, text="Controles de Treinamento")
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)

        self.device_frame = ttk.LabelFrame(self.master, text="Gerenciamento de Dispositivos")
        self.device_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.device_frame.grid_columnconfigure(0, weight=1)
        self.device_frame.grid_columnconfigure(1, weight=1)

        self.console_frame = ttk.LabelFrame(self.master, text="Console")
        self.console_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)

        # Botões de controle
        self.train_button = ttk.Button(self.control_frame, text="Treinar do Zero", command=self.train_from_scratch)
        self.train_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.continue_button = ttk.Button(self.control_frame,text="Continuar Treinamento", command=self.continue_training)
        self.continue_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.simulate_button = ttk.Button(self.control_frame,text="Simular Consumo em um Dia", command=self.simulate_day)
        self.simulate_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.show_simulate_button = ttk.Button(self.control_frame,text="Mostrar simulação",command=self.show_simulation_and_device_states_graph)
        self.show_simulate_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.show_q_table_button = ttk.Button(self.control_frame, text="Mostrar tabela Q", command=self.show_q_table)
        self.show_q_table_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.show_plot_button = ttk.Button(self.control_frame, text="Mostrar do treinamento", command=self.show_plot)
        self.show_plot_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Área de entrada de dispositivos
        self.device_frame.config(text="Adicionar Novo Dispositivo", padding=(10, 5))

        # Nome do dispositivo
        self.device_name_label = ttk.Label(self.device_frame, text="Nome do Dispositivo:")
        self.device_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.device_name_entry = ttk.Entry(self.device_frame)
        self.device_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Potência (W)
        self.device_consumption_label = ttk.Label(self.device_frame, text="Potência (W):")
        self.device_consumption_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.device_consumption_entry = ttk.Entry(self.device_frame)
        self.device_consumption_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Quantidade
        self.device_quantity_label = ttk.Label(self.device_frame, text="Quantidade:")
        self.device_quantity_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.device_quantity_entry = ttk.Entry(self.device_frame)
        self.device_quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Botão Adicionar Dispositivo
        self.add_device_button = ttk.Button(self.device_frame, text="Adicionar Dispositivo", command=self.add_device)
        self.add_device_button.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        # Mensagem de feedback para validação de entrada de dados
        self.feedback_label = ttk.Label(self.device_frame, text="", foreground="red")
        self.feedback_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Lista de dispositivos adicionados
        self.device_list_label = ttk.Label(self.device_frame, text="Dispositivos Adicionados:")
        self.device_list_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.device_list_frame = ttk.Frame(self.device_frame)
        self.device_list_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.device_list_frame.grid_columnconfigure(0, weight=1)

        self.device_widgets = []

        # Console de saída
        self.console_output = tk.Text(self.console_frame, state="disabled", height=10, wrap="word")
        self.console_output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Status do sistema
        self.status_label = ttk.Label(self.master, text="Status: Aguardando...", foreground="blue")
        self.status_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def add_device(self):
        """
        Adiciona um novo dispositivo à lista de dispositivos.
        """
        try:
            # Valida os dados de entrada
            device_name = self.device_name_entry.get().strip()
            device_consumption = float(self.device_consumption_entry.get())
            device_quantity = int(self.device_quantity_entry.get())

            # Verifica se os campos estão preenchidos corretamente
            if not device_name:
                self.feedback_label.config(text="Erro: Nome do dispositivo é obrigatório.", foreground="red")
                return
            if device_consumption <= 0:
                self.feedback_label.config(text="Erro: Potência deve ser um número positivo.", foreground="red")
                return
            if device_quantity <= 0:
                self.feedback_label.config(text="Erro: Quantidade deve ser um número positivo.", foreground="red")
                return

            # Adiciona o dispositivo à lista
            device = (device_name, device_consumption, device_quantity)
            self.devices.append(device)
            self.update_device_list()

            # Feedback de sucesso e limpa as entradas
            self.feedback_label.config(text=f"Dispositivo '{device_name}' adicionado com sucesso!", foreground="green")
            self.device_name_entry.delete(0, tk.END)
            self.device_consumption_entry.delete(0, tk.END)
            self.device_quantity_entry.delete(0, tk.END)

        except ValueError:
            self.feedback_label.config(text="Erro: Potência e Quantidade devem ser números válidos.", foreground="red")

    def update_device_list(self):
        """
        Atualiza a lista de dispositivos na interface gráfica.
        """
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets = []

        for i, (device_name, consumption, quantity) in enumerate(self.devices):
            device_label = ttk.Label(self.device_list_frame, text=f"{device_name} | Potência: {consumption} W | Quantidade: {quantity}")
            device_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            remove_button = ttk.Button(self.device_list_frame,text="Remover", command=lambda i=i: self.remove_device(i))
            remove_button.grid(row=i, column=1, padx=5, pady=2, sticky="e")

            self.device_widgets.append(device_label)
            self.device_widgets.append(remove_button)

    def remove_device(self, index):
        """
        Remove um dispositivo da lista com base no índice.

        Args:
            index (int): Índice do dispositivo a ser removido.
        """
        try:
            device_name = self.devices[index][0]
            del self.devices[index]
            self.update_device_list()
            self.env.remove_device(device_name)
            self.agent.update_num_devices()  # Atualize o número de dispositivos e ações
            self.status_label.config(text="Dispositivo removido com sucesso!", foreground="green")
        except IndexError:
            self.status_label.config(text="Erro ao remover dispositivo.", foreground="red")

    def train_from_scratch(self):
        """
        Inicia o treinamento do agente a partir do zero, reiniciando a Q-table.
        """
        confirm = messagebox.askyesno("Confirmar", "Isso irá reiniciar a tabela Q. Deseja continuar?")
        if confirm:
            self.q_table = None
            self.start_training()

    def continue_training(self):
        """
        Continua o treinamento do agente a partir da Q-table existente.
        """
        if self.q_table is None:
            self.train_from_scratch()
        else:
            try:
                self.start_training()
            except ValueError as ve:
                messagebox.showerror("Erro ao Continuar Treinamento", "Ocorreu um erro durante o treinamento. Por favor, reinicie o treinamento.",)

    def start_training(self):
        """
        Configura e inicia o processo de treinamento do agente.
        """
        if not self.devices:
            self.status_label.config(text="Adicione pelo menos um dispositivo.", foreground="red")
            return

        self.clear_console()  # Limpa o console

        # Inicialize o ambiente
        self.env = EnergyManagementEnvironment(self.devices)

        # Aqui, você cria o agente
        self.agent = QLearningAgent(self.env, q_table=self.q_table)

        # Atualiza o número de dispositivos e ações
        self.agent.update_num_devices()

        try:
            # Treinamento do agente
            rewards, consumptions, self.q_table = self.agent.train()

            # Salva as recompensas e consumos para visualização posterior
            self.rewards = rewards
            self.consumptions = consumptions

            # Mostra no console
            self.console_output.config(state="normal")
            self.console_output.insert(tk.END,f"Treinamento concluído. Recompensas: {rewards[-1]:.2f}, Consumo: {consumptions[-1]:.2f} kWh\n",)
            self.console_output.config(state="disabled")
            self.status_label.config(text="Treinamento concluído!", foreground="green")

        except ValueError as ve:
            if "Número de ações deve corresponder ao número de dispositivos" in str(ve):
                messagebox.showerror("Erro de Treinamento","O número de ações não corresponde ao número de dispositivos. Por favor, reinicie o treinamento.",)
            else:
                messagebox.showerror("Erro", str(ve))

    def simulate_day(self, custom_actions=None):
        """
        Simula o consumo de energia durante um dia.
        """
        if self.q_table is None:
            self.status_label.config(text="Por favor, treine o modelo antes de simular.", foreground="red")
            return

        if not self.env:
            self.env = EnergyManagementEnvironment(self.devices)

        total_consumption = 0
        self.actions_taken = []  # Redefine a variável para armazenar as ações
        self.device_states = {device: [] for device in self.env.devices}  # Redefine os estados

        state = self.env.reset()

        try:
            # Simular 24 horas
            for step in range(24):
                if custom_actions and step < len(custom_actions):
                    action = custom_actions[step]
                else:
                    action = self.agent.choose_action(state)

                decoded_action = self.agent.decode_action(action)
                reward, consumption, done = self.env.step(decoded_action)
                total_consumption += consumption

                self.actions_taken.append((step, decoded_action, consumption))
                state = self.env.tempo

                # Armazena o estado dos dispositivos a cada hora
                for device in self.env.devices:
                    self.device_states[device].append(self.env.devices[device]["estado"])

            self.console_output.config(state="normal")
            self.console_output.insert(tk.END, f"Simulação concluída! Consumo total: {total_consumption:.2f} kWh\n")
            self.console_output.config(state="disabled")
            self.status_label.config(text=f"Simulação concluída! Consumo total: {total_consumption:.2f} kWh", foreground="green")

        except ValueError as ve:
            if "Número de ações deve corresponder ao número de dispositivos" in str(ve):
                messagebox.showerror("Erro de Simulação", "O número de ações não corresponde ao número de dispositivos. Por favor, treine o modelo novamente.")
            else:
                messagebox.showerror("Erro", str(ve))

        except ValueError as ve:
            if "Número de ações deve corresponder ao número de dispositivos" in str(ve):
                messagebox.showerror("Erro de Simulação", "O número de ações não corresponde ao número de dispositivos. Por favor, treine o modelo novamente.")
            else:
                messagebox.showerror("Erro", str(ve))

    def show_plot(self):
        """
        Exibe os gráficos de recompensas e consumo durante o treinamento.
        """
        if not self.rewards or not self.consumptions:
            self.status_label.config(text="Por favor, treine o modelo antes de exibir o gráfico.", foreground="red")
            return

        plot_window = tk.Toplevel(self.master)
        plot_window.title("Gráfico de Recompensas e Consumo")

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        episodes = range(len(self.rewards))

        ax[0].plot(episodes, self.rewards, label="Recompensa Acumulada", color="blue")
        ax[0].set_xlabel("Episódios")
        ax[0].set_ylabel("Recompensa Total")
        ax[0].set_title("Progresso da Recompensa Durante o Treinamento")
        ax[0].grid(True)
        ax[0].legend()

        ax[1].plot(episodes, self.consumptions, label="Consumo de Energia", color="orange")
        ax[1].set_xlabel("Episódios")
        ax[1].set_ylabel("Consumo Total (kWh)")
        ax[1].set_title("Consumo de Energia Durante o Treinamento")
        ax[1].grid(True)
        ax[1].legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def show_simulation_and_device_states_graph(self):
        """
        Mostra ambos os gráficos: consumo total e estados dos dispositivos.
        """
        if not self.actions_taken or not self.device_states:
            self.status_label.config(text="Por favor, realize a simulação antes de visualizar os gráficos.", foreground="red",)
            return

        self.show_simulation_graph(self.actions_taken)
        self.show_device_states_graph(self.device_states)

    def show_simulation_graph(self, actions_taken):
        """
        Exibe o gráfico de consumo total ao longo do dia.

        Args:
            actions_taken (list): Lista de ações tomadas durante a simulação.
        """
        steps = [step for step, _, _ in actions_taken]
        consumptions = [consumption for _, _, consumption in actions_taken]
        total_consumption = [sum(consumptions[: i + 1]) for i in range(len(consumptions))]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(steps, total_consumption, marker="o", label="Consumo Total (kWh)")
        ax.set_title("Consumo de Energia ao Longo do Dia")
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Consumo Total (kWh)")
        ax.set_xticks(steps)
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        # Criação de uma nova janela para o gráfico
        graph_window = tk.Toplevel(self.master)
        graph_window.title("Gráfico de Simulação")

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_device_states_graph(self, device_states):
        """
        Exibe o gráfico de estados dos dispositivos ao longo do dia.

        Args:
            device_states (dict): Dicionário com os estados dos dispositivos por hora.
        """
        if not device_states or all(len(states) == 0 for states in device_states.values()):
            messagebox.showerror("Erro", "Nenhum dado de estado dos dispositivos encontrado. Por favor, realize a simulação.")
            return

        hours = range(24)  # Representando as horas do dia
        num_devices = len(device_states)
        states_matrix = []

        # Construindo a matriz de estados para os dispositivos
        for device, states in device_states.items():
            if len(states) != len(hours):  # Verifica se o número de estados corresponde ao número de horas
                messagebox.showerror("Erro", f"Dispositivo {device} tem um número incorreto de estados. Esperado: {len(hours)}, Recebido: {len(states)}")
                return
            states_matrix.append(states)

        # Transpondo a matriz para que as horas sejam nas linhas e os dispositivos nas colunas
        states_matrix = list(map(list, zip(*states_matrix)))

        # Converte a lista de estados em um array para facilitar o empilhamento
        states_array = np.array(states_matrix)  # Usando a importação do NumPy

        # Verifica se o número de dispositivos e o número de estados estão alinhados corretamente
        if states_array.shape[0] != len(hours):
            messagebox.showerror("Erro", f"Incompatibilidade entre o número de horas ({len(hours)}) e o número de estados ({states_array.shape[0]}).")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        bottom_states = np.zeros(len(hours))  # Base inicial para empilhar

        device_names = list(device_states.keys())

        # Para cada dispositivo, crie uma barra que empilha seu estado
        for i in range(num_devices):
            ax.bar(hours, states_array[:, i], bottom=bottom_states, label=device_names[i])
            bottom_states += states_array[:, i]  # Atualiza a base para o próximo dispositivo

        ax.set_title("Estados dos Dispositivos ao Longo do Dia")
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Estado do Dispositivo (0=Desligado, 1=Ligado)")
        ax.set_xticks(hours)
        ax.set_xticklabels([f"{i}:00" for i in hours], rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        ax.legend(title="Dispositivos")
        fig.tight_layout()

        # Criação de uma nova janela para o gráfico
        graph_window = tk.Toplevel(self.master)
        graph_window.title("Estados dos Dispositivos")

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_q_table(self):
        """
        Exibe a Q-table em uma nova janela.
        """
        if self.q_table is None:
            self.status_label.config(text="Por favor, treine o modelo antes de visualizar a Q-table.",foreground="red")
            return

        # Cria uma nova janela
        q_table_window = tk.Toplevel(self.master)
        q_table_window.title("Visualização da Q-table")

        # Exibe a Q-table em uma área de texto na nova janela
        q_table_text = tk.Text(q_table_window, wrap="none", height=20, width=60)
        q_table_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Formata a Q-table para melhor visualização
        q_table_str = "\n".join(["\t".join([f"{q:.2f}" for q in row]) for row in self.q_table])
        q_table_text.insert(tk.END, f"Q-table:\n{q_table_str}")

        # Desabilita a edição no campo de texto
        q_table_text.config(state="disabled")

    def clear_console(self):
        """
        Limpa o console de saída.
        """
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", tk.END)
        self.console_output.config(state="disabled")
