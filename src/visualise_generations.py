import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pickle

fitness_values = []
for i in range(1,6):
    fitness_values_path = f"../networks/2_identical_intersections_period_10/testcase 3 - different intersections - all generations ({i})/fitness_values.pkl"
    with open(fitness_values_path, "rb") as f:
        fitness_values.append(pickle.load(f))

fitness_values = np.array(fitness_values)
average_fitness_values = np.mean(fitness_values, axis=0)
best_fitness_values = np.min(fitness_values, axis=0)

print(fitness_values)
plt.plot(average_fitness_values, label="Prosjek")
plt.plot(best_fitness_values, label="Najbolje")
plt.xlabel('Generacija')  # X-axis label
plt.ylabel('Kazna')  # Y-axis label
plt.legend()
plt.grid(True)
plt.show()