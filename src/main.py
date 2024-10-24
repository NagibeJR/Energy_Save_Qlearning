from views.energyApp import EnergyManagementApp
import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Gerenciador de Energia com Q-learning")
    EnergyManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
