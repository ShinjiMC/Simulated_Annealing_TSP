import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import random
import math

# Cargar el archivo GeoJSON
gdf = gpd.read_file('peru_departamental_simple.geojson')

# Reproyectar a un CRS adecuado para cálculos de distancia (por ejemplo, UTM)
gdf = gdf.to_crs(epsg=32718)  # UTM zona 18S, ajusta según sea necesario

centroids = gdf['geometry'].centroid
names = gdf['NOMBDEP']
coords = [(point.x, point.y) for point in centroids]

# Colores para los departamentos (aumenta la lista para que coincida con el número de departamentos)
color = [
    (0, 128, 0),       # Amazonas
    (255, 140, 0),     # Áncash
    (75, 0, 130),      # Apurímac
    (0, 0, 255),       # Arequipa
    (255, 165, 0),     # Ayacucho
    (255, 215, 0),     # Cajamarca
    (0, 0, 255),       # Callao
    (138, 43, 226),    # Cusco
    (128, 0, 128),     # Huancavelica
    (34, 139, 34),     # Huánuco
    (60, 179, 113),    # Ica
    (0, 128, 128),     # Junín
    (139, 69, 19),     # La Libertad
    (0, 255, 255),     # Lambayeque
    (255, 252, 132),   # Lima
    (0, 100, 0),       # Loreto
    (85, 107, 47),     # Madre de Dios
    (210, 105, 30),    # Moquegua
    (47, 79, 79),      # Pasco
    (255, 255, 0),     # Piura
    (0, 191, 255),     # Puno
    (60, 179, 113),    # San Martín
    (220, 20, 60),     # Tacna
    (32, 178, 170),    # Tumbes
    (34, 139, 34)      # Ucayali
]
color = [(r / 255, g / 255, b / 255) for r, g, b in color]
gdf['color'] = color[:len(names)]

# Función de distancia entre dos departamentos
def distance(idx1, idx2):
    x1, y1 = coords[idx1]
    x2, y2 = coords[idx2]
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Función de costo total para un camino
def total_distance(path):
    return sum(distance(path[i], path[i+1]) for i in range(len(path) - 1)) + distance(path[-1], path[0])

# Simulated Annealing
def simulated_annealing(nodes, temp=1000, cooling_rate=0.005):
    current_path = nodes[:]
    current_cost = total_distance(current_path)

    temperatures = [temp]
    costs = [current_cost]
    acceptance_probabilities = []

    # Primera iteración
    new_path = current_path[:]
    i, j = sorted(random.sample(range(len(new_path)), 2))
    new_path[i:j] = reversed(new_path[i:j])
    new_cost = total_distance(new_path)

    # Temperatura inicial y distancia inicial
    print(f"Temperatura inicial: {temp}")
    print(f"Distancia inicial: {current_cost}")

    # Graficar la ruta en la primera iteración con leyenda a la derecha
    fig, ax = plt.subplots(figsize=(12, 8))
    gdf.plot(ax=ax, color=gdf['color'], linewidth=1, edgecolor='black')
    x, y = zip(*[coords[i] for i in new_path + [new_path[0]]])
    ax.plot(x, y, marker='o', color='magenta', markersize=5, linestyle='-', linewidth=2)
    plt.title('Ruta en la primera iteración')
    plt.title(f'Temperatura: {temp:.2f}, Distancia: {current_cost:.2f}')
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=color, markersize=5) for name, color in zip(names, gdf['color'])]
    ax.legend(handles=legend_elements, title="Departamentos", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small', title_fontsize='medium')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

    # Simulated Annealing
    while temp > 1:
        new_path = current_path[:]
        i, j = sorted(random.sample(range(len(new_path)), 2))
        new_path[i:j] = reversed(new_path[i:j])
        new_cost = total_distance(new_path)
        if new_cost < current_cost or random.random() < math.exp(min((current_cost - new_cost) / temp, 709)):
            current_path = new_path
            current_cost = new_cost
            acceptance_probability = 1
        else:
            acceptance_probability = 0

        temperatures.append(temp)
        costs.append(current_cost)
        acceptance_probabilities.append(acceptance_probability)

        temp *= 1 - cooling_rate

    # Temperatura final
    final_temp = temp

    return current_path, current_cost, final_temp, temperatures, costs, acceptance_probabilities

# Calcular la temperatura inicial
initial_temp = 1000

nodes = list(range(len(coords)))
best_path, best_cost, final_temp, temperatures, costs, acceptance_probabilities = simulated_annealing(nodes, temp=initial_temp)
print("Mejor camino:", best_path)
print("Costo total (distancia):", best_cost)

# Graficar la ruta óptima con leyenda a la derecha
fig, ax = plt.subplots(figsize=(12, 8))
gdf.plot(ax=ax, color=gdf['color'], linewidth=1, edgecolor='black')
x, y = zip(*[coords[i] for i in best_path + [best_path[0]]])
ax.plot(x, y, marker='o', color='magenta', markersize=5, linestyle='-', linewidth=2)
plt.title(f'Ruta óptima con Simulated Annealing - Temperatura final: {final_temp:.2f}, Distancia: {best_cost:.2f}')

legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=color, markersize=5) for name, color in zip(names, gdf['color'])]
ax.legend(handles=legend_elements, title="Departamentos", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small', title_fontsize='medium')
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()

# Graficar temperatura vs iteraciones
plt.figure(figsize=(10, 5))
plt.plot(temperatures)
plt.xlabel('Iteraciones')
plt.ylabel('Temperatura')
plt.title('Variación de la Temperatura durante la Búsqueda')
plt.grid(True)
plt.show()

# Graficar costo vs iteraciones
plt.figure(figsize=(10, 5))
plt.plot(costs)
plt.xlabel('Iteraciones')
plt.ylabel('Costo Total')
plt.title('Variación del Costo Total durante la Búsqueda')
plt.grid(True)
plt.show()
