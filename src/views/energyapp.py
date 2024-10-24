import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox, filedialog
from models.agent import QLearningAgent
from models.environment import EnergyManagementEnvironment
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class EnergyManagementApp:
    def __init__(self, master):
        self.master = master
        self.agent = None
        self.q_table = None
        self.devices = []
        self.rewards = []
        self.consumptions = []
        self.simulation_results = []
        self.create_widgets()

    def create_widgets(self):
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

        self.continue_button = ttk.Button(self.control_frame, text="Continuar Treinamento", command=self.continue_training)
        self.continue_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.simulate_button = ttk.Button(self.control_frame, text="Simular Consumo em um Dia", command=self.simulate_day)
        self.simulate_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.export_results_button = ttk.Button(self.control_frame, text="Exportar Resultados", command=self.export_results)
        self.export_results_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.show_q_table_button = ttk.Button(self.control_frame, text="Exibir Q-table", command=self.show_q_table)
        self.show_q_table_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.show_plot_button = ttk.Button(self.control_frame, text="Exibir Gráfico", command=self.show_plot)
        self.show_plot_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Área de entrada de dispositivos
        self.device_name_label = ttk.Label(self.device_frame, text="Nome do Dispositivo:")
        self.device_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.device_name_entry = ttk.Entry(self.device_frame)
        self.device_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.device_consumption_label = ttk.Label(self.device_frame, text="Potencia (W):")
        self.device_consumption_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.device_consumption_entry = ttk.Entry(self.device_frame)
        self.device_consumption_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.device_quantity_label = ttk.Label(self.device_frame, text="Quantidade:")
        self.device_quantity_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.device_quantity_entry = ttk.Entry(self.device_frame)
        self.device_quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.add_device_button = ttk.Button(self.device_frame, text="Adicionar Dispositivo", command=self.add_device)
        self.add_device_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        # Lista de dispositivos adicionados
        self.device_list_label = ttk.Label(self.device_frame, text="Dispositivos Adicionados:")
        self.device_list_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.device_list_frame = ttk.Frame(self.device_frame)
        self.device_list_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.device_list_frame.grid_columnconfigure(0, weight=1)

        self.device_widgets = []

        # Console de saída
        self.console_output = tk.Text(self.console_frame, state="disabled", height=10, wrap="word")
        self.console_output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Status do sistema
        self.status_label = ttk.Label(self.master, text="Status: Aguardando...", foreground="blue")
        self.status_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def add_device(self):
        try:
            device_name = self.device_name_entry.get().strip()
            device_consumption = float(self.device_consumption_entry.get())
            device_quantity = int(self.device_quantity_entry.get())
            if not device_name or device_consumption <= 0 or device_quantity <= 0:
                raise ValueError("Nome, consumo e quantidade devem ser válidos.")
            device = (device_name, device_consumption, device_quantity)
            self.devices.append(device)
            self.update_device_list()
            self.status_label.config(text=f"Dispositivo '{device_name}' adicionado!", foreground="green")
        except ValueError as ve:
            self.status_label.config(text=f"Erro: {ve}", foreground="red")

    def update_device_list(self):
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets = []

        for i, (device_name, consumption, quantity) in enumerate(self.devices):
            device_label = ttk.Label(self.device_list_frame,text=f"{device_name} | Potencia: {consumption} W | Quantidade: {quantity}")
            device_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            remove_button = ttk.Button(self.device_list_frame,text="Remover",command=lambda i=i: self.remove_device(i))
            remove_button.grid(row=i, column=1, padx=5, pady=2, sticky="e")

            self.device_widgets.append(device_label)
            self.device_widgets.append(remove_button)

    def remove_device(self, index):
        try:
            del self.devices[index]
            self.update_device_list()
            self.status_label.config(text="Dispositivo removido com sucesso!", foreground="green")
        except IndexError:
            self.status_label.config(text="Erro ao remover dispositivo.", foreground="red")

    def train_from_scratch(self):
        confirm = messagebox.askyesno("Confirmar", "Isso irá reiniciar a tabela Q. Deseja continuar?")
        if confirm:
            self.q_table = None
            self.start_training()

    def continue_training(self):
        if self.q_table is None:
            self.train_from_scratch()
        else:
            self.start_training()

    def start_training(self):
        if not self.devices:
            self.status_label.config(text="Adicione pelo menos um dispositivo.", foreground="red")
            return

        self.clear_console()  # Limpa o console

        # Inicialize o ambiente
        env = EnergyManagementEnvironment(self.devices)

        # Aqui, você cria o agente
        self.agent = QLearningAgent(env, q_table=self.q_table)

        rewards, consumptions, self.q_table = self.agent.train()

        # Salva as recompensas e consumos para visualização posterior
        self.rewards = rewards
        self.consumptions = consumptions

        # Mostra no console
        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, f"Treinamento concluído. Recompensas: {rewards[-1]:.2f}, Consumo: {consumptions[-1]:.2f} kWh\n")
        self.console_output.config(state="disabled")
        self.status_label.config(text="Treinamento concluído!", foreground="green")

    def simulate_day(self, custom_actions=None):
        if self.q_table is None:
            self.status_label.config(
                text="Por favor, treine o modelo antes de simular.", foreground="red"
            )
            return

        if not hasattr(self, "env") or self.env is None:
            self.env = EnergyManagementEnvironment(self.devices)

        total_consumption = 0
        actions_taken = []

        # Estado inicial
        state = self.env.reset()

        # Simular 24 horas
        for step in range(24):
            if custom_actions:
                action = custom_actions[step]
            else:
                action = self.agent.choose_action(state)

            decoded_action = self.agent.decode_action(action)
            reward, consumption, done = self.env.step(decoded_action)
            total_consumption += consumption
            actions_taken.append(
                (step, decoded_action, consumption, total_consumption)
            )  # Adicione o total aqui
            state = self.env.tempo

        self.console_output.config(state="normal")
        self.console_output.insert(
            tk.END, f"Simulação concluída! Consumo total: {total_consumption:.2f} kWh\n"
        )
        self.console_output.config(state="disabled")
        self.status_label.config(
            text=f"Simulação concluída! Consumo total: {total_consumption:.2f} kWh",
            foreground="green",
        )

        # Armazenar os resultados da simulação para exportação
        self.simulation_results = actions_taken  # Adiciona os resultados aqui

    def show_plot(self):
        if not self.rewards or not self.consumptions:
            self.status_label.config(text="Por favor, treine o modelo antes de exibir o gráfico.",foreground="red")
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

        ax[1].plot(
            episodes, self.consumptions, label="Consumo de Energia", color="orange"
        )
        ax[1].set_xlabel("Episódios")
        ax[1].set_ylabel("Consumo Total (kWh)")
        ax[1].set_title("Consumo de Energia Durante o Treinamento")
        ax[1].grid(True)
        ax[1].legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def export_results(self):
        if not self.simulation_results:
            self.status_label.config(
                text="Nenhum resultado disponível para exportar.", foreground="red"
            )
            return

        # Abre uma janela para escolher o local do arquivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Salvar resultados como",
        )

        if file_path:
            # Cria um DataFrame com os resultados
            df = pd.DataFrame(
                self.simulation_results,
                columns=["Passo", "Ação", "Consumo", "Consumo Total (kWh)"],
            )
            df.to_csv(file_path, index=False)
            self.status_label.config(
                text="Resultados exportados com sucesso!", foreground="green"
            )

    def show_q_table(self):
        if self.q_table is None:
            self.status_label.config(text="Por favor, treine o modelo antes de visualizar a Q-table.",foreground="red")
            return

        # Cria uma nova janela
        q_table_window = tk.Toplevel(self.master)
        q_table_window.title("Visualização da Q-table")

        # Exibe a Q-table em uma área de texto na nova janela
        q_table_text = tk.Text(q_table_window, wrap="none", height=20, width=60)
        q_table_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Insere a Q-table na área de texto
        q_table_text.insert(tk.END, f"Q-table:\n{self.q_table}")

        # Desabilita a edição no campo de texto
        q_table_text.config(state="disabled")

    def clear_console(self):
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", tk.END)
        self.console_output.config(state="disabled")
