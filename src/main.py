from views.energyapp import EnergyManagementApp
import tkinter as tk


def main():
    root = tk.Tk()
    EnergyManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
