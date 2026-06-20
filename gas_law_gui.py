import math
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Physical constants
N_A = 6.02214076e23  # Avogadro's number
k_B = 1.380649e-23  # Boltzmann constant, J/K

GAS_DATA = {
    "Hydrogen": 2.016e-3,  # g/mol
    "Helium": 4.003e-3,  # g/mol
    "Nitrogen": 28.02e-3,  # g/mol
    "Oxygen": 32.00e-3,  # g/mol
}


def calculate_properties():
    try:
        molecules = int(num_molecules_var.get())
        if molecules <= 0:
            raise ValueError("Number of molecules must be positive.")

        container_size = float(container_size_var.get())
        if container_size <= 0:
            raise ValueError("Container size must be positive.")

        temperature = float(temperature_var.get())
        if temperature <= 0:
            raise ValueError("Temperature must be positive.")

    except ValueError as error:
        messagebox.showerror("Input error", str(error))
        return

    gas_name = gas_var.get()
    molar_mass = GAS_DATA.get(gas_name, 28.02)

    volume_m3 = (container_size * 1e-9) ** 3
    moles = molecules / N_A
    mass_per_molecule = (molar_mass / 1000.0) / N_A
    pressure_pa = molecules * k_B * temperature / volume_m3
    v_rms = math.sqrt(3 * k_B * temperature / mass_per_molecule)

    moles_value.set(f"{moles:.6e}")
    volume_value.set(f"{volume_m3:.6e} m^3")
    molecular_mass_value.set(f"{mass_per_molecule:.6e} kg")
    pressure_value.set(f"{pressure_pa:.6e} Pa")
    rms_value.set(f"{v_rms:.3e} m/s")


def save_config():
    try:
        molecules = int(num_molecules_var.get())
        if molecules <= 0:
            raise ValueError("Number of molecules must be positive.")

        container = float(container_size_var.get())
        if container <= 0:
            raise ValueError("Container size must be positive.")

        temperature = float(temperature_var.get())
        if temperature <= 0:
            raise ValueError("Temperature must be positive.")
        time_steps = int(time_step_var.get())
        if time_steps <= 0:
            raise ValueError("Time steps must be positive.")
    except ValueError as error:
        messagebox.showerror("Input error", str(error))
        return

    gas_name = gas_var.get()
    # GAS_DATA entries are kg/mol (e.g. 2.016e-3 for H2)
    mass_per_mole = GAS_DATA.get(gas_name, 28.02e-3)

    config = {
        "n_molecules": molecules,
        "container_size": container,
        "temperature": temperature,
        "mass_per_mole": mass_per_mole,
        "time_step": time_steps,
    }

    config_path = os.path.join(os.path.dirname(__file__), "sim_config.json")
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", f"Configuration saved to {config_path}")
    except Exception as e:
        messagebox.showerror("Save error", str(e))


def create_gui():
    root = tk.Tk()
    root.title("Gas Law Parameter Simulator")
    root.resizable(False, False)

    global num_molecules_var, container_size_var, temperature_var, gas_var
    global moles_value, volume_value, molecular_mass_value, pressure_value, rms_value
    global time_step_var

    # Load existing config if present to pre-fill the GUI
    config_path = os.path.join(os.path.dirname(__file__), "sim_config.json")
    _cfg = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as _f:
                _cfg = json.load(_f)
        except Exception:
            _cfg = {}

    init_molecules = str(_cfg.get("n_molecules", 10000))
    init_container = str(_cfg.get("container_size", 10))
    init_temperature = str(_cfg.get("temperature", 300))
    init_time_step = str(_cfg.get("time_step", 1000))

    # If mass_per_mole is present, try to pick the matching gas name
    init_gas = "Hydrogen"
    mp = _cfg.get("mass_per_mole")
    if mp is not None:
        for name, val in GAS_DATA.items():
            try:
                if abs(val - float(mp)) < 1e-12:
                    init_gas = name
                    break
            except Exception:
                continue

    num_molecules_var = tk.StringVar(master=root, value=init_molecules)
    container_size_var = tk.StringVar(master=root, value=init_container)
    temperature_var = tk.StringVar(master=root, value=init_temperature)
    time_step_var = tk.StringVar(master=root, value=init_time_step)
    gas_var = tk.StringVar(master=root, value=init_gas)

    moles_value = tk.StringVar(master=root, value="0")
    volume_value = tk.StringVar(master=root, value="0")
    molecular_mass_value = tk.StringVar(master=root, value="0")
    pressure_value = tk.StringVar(master=root, value="0")
    rms_value = tk.StringVar(master=root, value="0")

    main_frame = ttk.Frame(root, padding="12 12 12 12")
    main_frame.grid(row=0, column=0, sticky="NSEW")

    ttk.Label(main_frame, text="Gas type:").grid(row=0, column=0, sticky="W", pady=4)
    gas_combo = ttk.Combobox(
        main_frame,
        textvariable=gas_var,
        values=list(GAS_DATA.keys()),
        state="readonly",
        width=22,
    )
    gas_combo.grid(row=0, column=1, sticky="EW", pady=4)

    ttk.Label(main_frame, text="Number of molecules:").grid(
        row=1, column=0, sticky="W", pady=4
    )
    ttk.Entry(main_frame, textvariable=num_molecules_var, width=24).grid(
        row=1, column=1, sticky="EW", pady=4
    )

    ttk.Label(main_frame, text="Container size (nm):").grid(
        row=2, column=0, sticky="W", pady=4
    )
    ttk.Entry(main_frame, textvariable=container_size_var, width=24).grid(
        row=2, column=1, sticky="EW", pady=4
    )

    ttk.Label(main_frame, text="Temperature (K):").grid(
        row=3, column=0, sticky="W", pady=4
    )
    ttk.Entry(main_frame, textvariable=temperature_var, width=24).grid(
        row=3, column=1, sticky="EW", pady=4
    )

    ttk.Label(main_frame, text="Time steps:").grid(row=4, column=0, sticky="W", pady=4)
    ttk.Entry(main_frame, textvariable=time_step_var, width=24).grid(
        row=4, column=1, sticky="EW", pady=4
    )

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=(12, 10), sticky="EW")

    calculate_button = ttk.Button(
        button_frame, text="Calculate", command=calculate_properties
    )
    calculate_button.pack(side="left", padx=4)

    save_button = ttk.Button(button_frame, text="Save", command=save_config)
    save_button.pack(side="left", padx=4)

    quit_button = ttk.Button(button_frame, text="Quit", command=root.destroy)
    quit_button.pack(side="right", padx=4)

    separator = ttk.Separator(main_frame, orient="horizontal")
    separator.grid(row=5, column=0, columnspan=2, sticky="EW", pady=8)

    result_labels = [
        ("Moles:", moles_value),
        ("Volume:", volume_value),
        ("Mass per molecule:", molecular_mass_value),
        ("Pressure (ideal):", pressure_value),
        ("RMS speed:", rms_value),
    ]

    for i, (label_text, var) in enumerate(result_labels, start=6):
        ttk.Label(main_frame, text=label_text).grid(row=i, column=0, sticky="W", pady=3)
        ttk.Label(main_frame, textvariable=var, foreground="#00529B").grid(
            row=i, column=1, sticky="W", pady=3
        )

    main_frame.columnconfigure(1, weight=1)
    calculate_properties()
    root.mainloop()


if __name__ == "__main__":
    create_gui()
