import tkinter as tk
from views.views import EnergyManagementApp


def main():
    root = tk.Tk()
    root.title("Gerenciador de Energia com Q-learning")
    root.geometry("800x800")
    app = EnergyManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
