import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys
import os
import csv
import pickle

from models.energyManagementEnvironment import EnergyManagementEnvironment
from models.qLearningAgent import QLearningAgent
from views.textRedirector import TextRedirector


class EnergyManagementApp:
    def __init__(self, master):
        self.master = master
        self.agent = None
        self.q_table = None  # Para armazenar a tabela Q entre os treinamentos
        self.devices = []
        self.device_widgets = []
        self.rewards = []
        self.consumptions = []
        self.simulation_results = []
        self.create_widgets()

    def create_widgets(self):
        # Frames para organizar a interface
        self.control_frame = ttk.LabelFrame(
            self.master, text="Controles de Treinamento"
        )
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.device_frame = ttk.LabelFrame(
            self.master, text="Gerenciamento de Dispositivos"
        )
        self.device_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.console_frame = ttk.LabelFrame(self.master, text="Console")
        self.console_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Botões de treinamento
        self.train_button = ttk.Button(
            self.control_frame,
            text="Treinar Novamente",
            command=self.train_from_scratch,
        )
        self.train_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.continue_button = ttk.Button(
            self.control_frame,
            text="Continuar Treinamento",
            command=self.continue_training,
        )
        self.continue_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.simulate_button = ttk.Button(
            self.control_frame,
            text="Simular Consumo em um Dia",
            command=self.simulate_day,
        )
        self.simulate_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.show_plot_button = ttk.Button(
            self.control_frame, text="Exibir Gráfico", command=self.show_plot
        )
        self.show_plot_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Salvar e Carregar Q-table
        self.save_q_button = ttk.Button(
            self.control_frame, text="Salvar Tabela Q", command=self.save_q_table
        )
        self.save_q_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.load_q_button = ttk.Button(
            self.control_frame, text="Carregar Tabela Q", command=self.load_q_table
        )
        self.load_q_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Controle de velocidade
        self.speed_label = ttk.Label(
            self.control_frame, text="Velocidade de Treinamento:"
        )
        self.speed_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.speed_scale = ttk.Scale(
            self.control_frame, from_=0.1, to=10, orient="horizontal"
        )
        self.speed_scale.set(1.0)
        self.speed_scale.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Seleção de perfil de usuário
        self.profile_label = ttk.Label(self.control_frame, text="Perfil de Usuário:")
        self.profile_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.profile_var = tk.StringVar(value="economico")
        self.profile_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.profile_var,
            values=["economico", "conforto", "balanceado"],
            state="readonly",
        )
        self.profile_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.profile_menu.current(0)

        # Entrada manual de dispositivos
        self.device_name_label = ttk.Label(
            self.device_frame, text="Nome do Dispositivo:"
        )
        self.device_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.device_name_entry = ttk.Entry(self.device_frame)
        self.device_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.device_consumption_label = ttk.Label(
            self.device_frame, text="Consumo (kWh):"
        )
        self.device_consumption_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.device_consumption_entry = ttk.Entry(self.device_frame)
        self.device_consumption_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.device_quantity_label = ttk.Label(self.device_frame, text="Quantidade:")
        self.device_quantity_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.device_quantity_entry = ttk.Entry(self.device_frame)
        self.device_quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.add_device_button = ttk.Button(
            self.device_frame, text="Adicionar Dispositivo", command=self.add_device
        )
        self.add_device_button.grid(
            row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew"
        )

        # Frame para exibir a lista de dispositivos adicionados
        self.device_list_label = ttk.Label(
            self.device_frame, text="Dispositivos Adicionados:"
        )
        self.device_list_label.grid(
            row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )

        self.device_list_frame = ttk.Frame(self.device_frame)
        self.device_list_frame.grid(
            row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew"
        )

        self.device_frame.grid_columnconfigure(1, weight=1)

        # Textbox para exibir o console
        self.console_output = ScrolledText(
            self.console_frame, state="disabled", height=10, wrap="word"
        )
        self.console_output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Redirecionar stdout para o console na interface
        sys.stdout = TextRedirector(self.console_output)

        # Exibição de status
        self.status_label = ttk.Label(
            self.master, text="Status: Aguardando...", foreground="blue"
        )
        self.status_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def add_device(self):
        try:
            # Coleta as informações do dispositivo
            device_name = self.device_name_entry.get().strip()
            device_consumption = float(self.device_consumption_entry.get())
            device_quantity = int(self.device_quantity_entry.get())

            # Validação das entradas
            if not device_name:
                raise ValueError("Nome do dispositivo não pode ser vazio.")
            if device_consumption <= 0:
                raise ValueError("Consumo deve ser maior que zero.")
            if device_quantity <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")

            # Adiciona à lista de dispositivos
            device = (device_name, device_consumption, device_quantity)
            self.devices.append(device)
            self.update_device_list()
            self.status_label.config(
                text=f"Dispositivo '{device_name}' adicionado! Consumo: {device_consumption} kWh, Quantidade: {device_quantity}",
                foreground="green",
            )
            self.device_name_entry.delete(0, tk.END)
            self.device_consumption_entry.delete(0, tk.END)
            self.device_quantity_entry.delete(0, tk.END)
        except ValueError as ve:
            self.status_label.config(text=f"Erro: {ve}", foreground="red")

    def update_device_list(self):
        # Limpa os widgets anteriores
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets = []

        # Cria novos widgets para cada dispositivo
        for i, (device_name, consumption, quantity) in enumerate(self.devices):
            device_label = ttk.Label(
                self.device_list_frame,
                text=f"{device_name} | Consumo: {consumption} kWh | Quantidade: {quantity}",
            )
            device_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            remove_button = ttk.Button(
                self.device_list_frame,
                text="Remover",
                command=lambda i=i: self.remove_device(i),
            )
            remove_button.grid(row=i, column=1, padx=5, pady=2, sticky="e")

            self.device_widgets.append(device_label)
            self.device_widgets.append(remove_button)

    def remove_device(self, index):
        # Remove o dispositivo da lista e atualiza a exibição
        try:
            del self.devices[index]
            self.update_device_list()
            self.status_label.config(
                text="Dispositivo removido com sucesso!", foreground="green"
            )
        except IndexError:
            self.status_label.config(
                text="Erro ao remover dispositivo: índice inválido.", foreground="red"
            )

    def train_from_scratch(self):
        """Treina o modelo do zero (reinicializa a tabela Q)"""
        confirm = messagebox.askyesno(
            "Confirmar", "Isso irá reiniciar a tabela Q. Deseja continuar?"
        )
        if confirm:
            self.q_table = None
            self.start_training()

    def continue_training(self):
        """Continua o treinamento com a tabela Q já existente"""
        if self.q_table is None:
            self.status_label.config(
                text="Nenhum treinamento anterior encontrado. Treinando do zero...",
                foreground="orange",
            )
            self.train_from_scratch()
        else:
            self.start_training()

    def start_training(self):
        if not self.devices:
            self.status_label.config(
                text="Adicione pelo menos um dispositivo.", foreground="red"
            )
            return

        # Configura o perfil de usuário selecionado
        profile = self.profile_var.get()

        # Recriar o ambiente e agente com o novo número de dispositivos e perfil
        env = EnergyManagementEnvironment(
            device_list=self.devices, user_profile=profile
        )
        self.agent = QLearningAgent(env, q_table=self.q_table)

        speed_factor = self.speed_scale.get()
        self.status_label.config(text="Treinamento em andamento...", foreground="blue")
        self.master.update()

        rewards, consumptions, self.q_table = self.agent.train(
            speed_factor=speed_factor
        )

        # Armazenar os resultados para exibição posterior
        self.rewards = rewards
        self.consumptions = consumptions

        # Atualizar o status ao final do treinamento
        self.status_label.config(
            text=f"Treinamento concluído! Última recompensa: {rewards[-1]:.2f}, Último consumo: {consumptions[-1]:.2f} kWh",
            foreground="green",
        )

    def simulate_day(self):
        """Simula o consumo de energia em um dia com base no modelo treinado"""
        if self.q_table is None:
            self.status_label.config(
                text="Por favor, treine o modelo antes de simular.", foreground="red"
            )
            return

        try:
            total_consumption, actions_taken = self.agent.simulate_day()
            self.simulation_results = actions_taken
            self.status_label.config(
                text=f"Simulação concluída! Consumo total no dia: {total_consumption:.2f} kWh",
                foreground="green",
            )
            # Exportar resultados da simulação
            self.export_simulation_results(actions_taken, total_consumption)
        except Exception as e:
            self.status_label.config(text=f"Erro na simulação: {e}", foreground="red")

    def export_simulation_results(self, actions_taken, total_consumption):
        """Exporta os resultados da simulação para um arquivo CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
            if file_path:
                with open(file_path, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ["Hora", "Ação (Estado dos Dispositivos)", "Consumo (kWh)"]
                    )
                    for step, action, consumption in actions_taken:
                        writer.writerow([step, action, consumption])
                    writer.writerow(["Total", "", total_consumption])
                self.status_label.config(
                    text=f"Resultados da simulação exportados para {os.path.basename(file_path)}",
                    foreground="green",
                )
        except Exception as e:
            self.status_label.config(text=f"Erro ao exportar: {e}", foreground="red")

    def show_plot(self):
        """Abre uma nova janela e exibe o gráfico de recompensas e consumo"""
        if (
            not hasattr(self, "rewards")
            or not hasattr(self, "consumptions")
            or not self.rewards
            or not self.consumptions
        ):
            self.status_label.config(
                text="Por favor, treine o modelo antes de exibir o gráfico.",
                foreground="red",
            )
            return

        plot_window = tk.Toplevel(self.master)
        plot_window.title("Gráfico de Recompensas e Consumo")

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        episodes = range(len(self.rewards))

        # Plotando as recompensas
        ax[0].plot(episodes, self.rewards, label="Recompensa Acumulada", color="blue")
        ax[0].set_xlabel("Episódios")
        ax[0].set_ylabel("Recompensa Total")
        ax[0].set_title("Progresso da Recompensa Durante o Treinamento")
        ax[0].grid(True)
        ax[0].legend()

        # Plotando o consumo de energia
        ax[1].plot(
            episodes, self.consumptions, label="Consumo de Energia", color="orange"
        )
        ax[1].set_xlabel("Episódios")
        ax[1].set_ylabel("Consumo Total (kWh)")
        ax[1].set_title("Consumo de Energia Durante o Treinamento")
        ax[1].grid(True)
        ax[1].legend()

        # Exibir gráfico na nova janela
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def save_q_table(self):
        """Salva a tabela Q atual em um arquivo"""
        if self.q_table is None:
            self.status_label.config(
                text="Nenhuma tabela Q para salvar. Treine o modelo primeiro.",
                foreground="red",
            )
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pkl",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            )
            if file_path:
                with open(file_path, "wb") as file:
                    pickle.dump(self.q_table, file)
                self.status_label.config(
                    text=f"Tabela Q salva em {os.path.basename(file_path)}",
                    foreground="green",
                )
        except Exception as e:
            self.status_label.config(
                text=f"Erro ao salvar tabela Q: {e}", foreground="red"
            )

    def load_q_table(self):
        """Carrega uma tabela Q de um arquivo"""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".pkl",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            )
            if file_path:
                with open(file_path, "rb") as file:
                    loaded_q_table = pickle.load(file)
                # Verificar se a tabela Q carregada corresponde ao número de dispositivos
                if self.agent and loaded_q_table.shape == self.agent.q_table.shape:
                    self.q_table = loaded_q_table
                    self.status_label.config(
                        text=f"Tabela Q carregada de {os.path.basename(file_path)}",
                        foreground="green",
                    )
                else:
                    messagebox.showerror(
                        "Erro",
                        "A tabela Q carregada não corresponde ao ambiente atual.",
                    )
        except Exception as e:
            self.status_label.config(
                text=f"Erro ao carregar tabela Q: {e}", foreground="red"
            )
