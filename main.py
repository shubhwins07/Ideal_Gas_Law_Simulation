# since we will be simulating the ideal law, there is no need to simulate collisions between molecules
# and only the collisions between the container and molecules.

# Since this is a two dimensional simulation, we will be using the 2D version of the laws, based on the equi-partition in only 2 dimensions

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import json
import os

matplotlib.use("TkAgg")

# Load simulation parameters from sim_config.json if present; otherwise use defaults
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sim_config.json")

_defaults = {
    "n_molecules": 10000,
    "container_size": 10,  # nanometers
    "temperature": 300,  # Kelvin
    "time_step": 10000,
    "mass_per_mole": 2.016e-3,  # kg/mol
    "dt": 1e-13,
}

_config = {}
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as _f:
            _config = json.load(_f)
    except Exception as _e:
        print(f"Warning: could not read config {CONFIG_PATH}: {_e}")

n_molecules = int(_config.get("n_molecules", _defaults["n_molecules"]))
container_size = float(_config.get("container_size", _defaults["container_size"]))
temperature = float(_config.get("temperature", _defaults["temperature"]))
time_step = int(_config.get("time_step", _defaults["time_step"]))
mass_per_mole = float(_config.get("mass_per_mole", _defaults["mass_per_mole"]))
dt = float(_config.get("dt", _defaults["dt"]))

containerSizeSI = (
    container_size * 1e-9
)  # Convert container size from nanometers to meters

# The Constants
k_B = 1.380649e-23
r = 8.314462618
mass_of_molecule = mass_per_mole / 6.022e23  # mass of single molecule in kg

# Calculating the other parameters
moles = n_molecules / 6.022e23

v_rms = np.sqrt(2 * k_B * temperature / mass_of_molecule)

# Assigning random initial positions and velocities to the molecules
positions = np.random.rand(n_molecules, 2) * container_size
velocities = (np.random.rand(n_molecules, 2) - 0.5) * 2 * v_rms

angles = np.random.rand(n_molecules) * 2 * np.pi

velocities = np.column_stack((v_rms * np.cos(angles), v_rms * np.sin(angles)))

v_squared_mean = np.sqrt(np.mean(velocities[:, 0] ** 2 + velocities[:, 1] ** 2))

# Calculating pressure using kinetic theory of gases, which states that the pressure exerted by a gas is proportional to the average kinetic energy of its molecules
pressure_kinetic = (
    n_molecules * mass_of_molecule * (v_squared_mean**2) / (2 * containerSizeSI**2)
)

# Calculating pressure using ideal gas law, which states that the pressure of an ideal gas is directly proportional to the number of moles and temperature, and inversely proportional to the volume
pressure_ideal = (n_molecules * k_B * temperature) / (
    containerSizeSI**2
)  # Directly using Boltzmann Constant instead of gas constant, since we are using no. of molecules instead of moles

# Creating our plot
fig, ax = plt.subplots()
scatter = ax.scatter(positions[:, 0], positions[:, 1], marker="o", s=1)
ax.set_xlim(0, container_size)
ax.set_ylim(0, container_size)
plt.title("Gas Law Simulation")
plt.gca().set_aspect("equal", adjustable="box")

#Initializing an array to store the number of collisions at each time step
collisions_array = []
pressure_momentum_array = []


#Simulation Loop
for step in range(time_step):
    #Updating positions based on velocities
    positions += velocities * dt * 1e9

    collisions = 0
    momentum_transfer = 0

    for i in range(n_molecules):
        for j in range(2):  # Check for collisions with walls
            if positions[i, j] <= 0 or positions[i, j] >= container_size:

                momentum_transfer += 2 * mass_of_molecule * abs(velocities[i, j])

                velocities[i, j] *= -1  # Reverse velocity on collision with wall
                collisions += 1

    collisions_array = np.append(collisions_array, collisions)

    #calculating pressure using momentum transfer
    pressure_momentum = momentum_transfer / (dt * containerSizeSI * 4)
    pressure_momentum_array = np.append(pressure_momentum_array, pressure_momentum)
    
    avg_observed_pressure = np.mean(pressure_momentum_array)

    status = (
        f"Step {step+1}/{time_step} | Collisions {collisions} | Avg_Collisions {np.mean(collisions_array):.3e} | "
        f"P_Observed {pressure_momentum:.3e} Pa | P_ideal {pressure_ideal:.3e} Pa | P_kin {pressure_kinetic:.3e} Pa | "
        f"Avg P_Observed {avg_observed_pressure:.3e} Pa"
    )
    # Write the status to stdout and clear to end-of-line (ANSI) so the line is overwritten
    import sys

    try:
        sys.stdout.write("\r" + status + "\x1b[K")
        sys.stdout.flush()
    except Exception:
        # Fallback: simple carriage-return print
        print(status, end="\r", flush=True)

    if not plt.fignum_exists(fig.number):  # Check if the figure window is still open
        break

    scatter.set_offsets(positions)  # Update point positions
    plt.pause(0.001)

plt.show()
