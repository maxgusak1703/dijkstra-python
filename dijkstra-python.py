import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def create_matrix():
    try:
        global num_vertices
        num_vertices = int(vertices_entry.get())
        if num_vertices < 2:
            messagebox.showerror("Помилка", "Кількість вершин повинна бути не менше 2.")
            return
        vertices_entry.config(state=tk.DISABLED)
        create_matrix_button.config(state=tk.DISABLED)
        initialize_matrix(num_vertices)
    except ValueError:
        messagebox.showerror("Помилка", "Будь ласка, введіть коректне число вершин.")

def initialize_matrix(num_vertices):
    global matrix_entries
    matrix_entries = []

    for i in range(num_vertices):
        row_entries = []
        for j in range(num_vertices):
            if i == 0:
                tk.Label(matrix_frame, text=f'x{j+1}').grid(row=i, column=j+1)
            if j == 0:
                tk.Label(matrix_frame, text=f'x{i+1}').grid(row=i+1, column=j)
            entry = tk.Entry(matrix_frame, width=5)
            entry.grid(row=i+1, column=j+1, padx=5, pady=5)
            entry.insert(0, "0")
            row_entries.append(entry)
        matrix_entries.append(row_entries)

    start_label.pack(side=tk.LEFT, padx=(0, 10), pady=5)
    start_entry.pack(side=tk.LEFT, padx=5, pady=5)
    end_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)
    end_entry.pack(side=tk.LEFT, padx=5, pady=5)
    submit_button.pack(padx=5, pady=10)

def algorithm_dijkstra(matrix, start, end):
    G = nx.Graph()
    
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] != 0:
                G.add_edge(f'x{i+1}', f'x{j+1}', weight=matrix[i][j])

    distances = {node: float('inf') for node in G.nodes}
    previous_nodes = {node: None for node in G.nodes}
    distances[f'x{start+1}'] = 0
    nodes = list(G.nodes)

    steps = []
    while nodes:
        current_node = min(nodes, key=lambda node: distances[node])
        nodes.remove(current_node)
        
        if distances[current_node] == float('inf'):
            break
        
        for neighbor in G.neighbors(current_node):
            edge_weight = G[current_node][neighbor]['weight']
            new_distance = distances[current_node] + edge_weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                steps.append((current_node, neighbor, distances.copy(), previous_nodes.copy()))

    path, current_step = [], f'x{end+1}'
    while previous_nodes[current_step] is not None:
        path.insert(0, current_step)
        current_step = previous_nodes[current_step]
    if path:
        path.insert(0, current_step)

    return path, distances[f'x{end+1}'], steps, G

def submit():
    try:
        global graf
        graf = [[int(entry_list[i].get()) for i in range(len(entry_list))] for entry_list in matrix_entries]

        start_vertex = int(start_entry.get()) - 1
        end_vertex = int(end_entry.get()) - 1

        if start_vertex < 0 or start_vertex >= len(graf) or end_vertex < 0 or end_vertex >= len(graf):
            messagebox.showerror("Помилка", "Номер вершини має бути в межах графа.")
            return

        shortest_path, shortest_path_length, steps, G = algorithm_dijkstra(graf, start_vertex, end_vertex)
        
        if not shortest_path:
            messagebox.showinfo("Результат", "Шлях не знайдено.")
            return
        
        shortest_path_label.config(text="Найкоротший шлях: " + ' -> '.join(shortest_path))
        path_length_label.config(text="Довжина шляху: " + str(shortest_path_length))
        
        animate_graph(G, steps, shortest_path)
        
    except ValueError:
        messagebox.showerror("Помилка", "Некоректний ввід. Будь ласка, введіть додатні числа.")

def animate_graph(G, steps, shortest_path):
    
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots()
    nx.draw(G, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=15)
    
    path_edges = [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path) - 1)]
    
    def update(num):
        ax.clear()
        nx.draw(G, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=15)
        
        if num < len(steps):
            current_node, neighbor, distances, _ = steps[num]
            nx.draw_networkx_nodes(G, pos, nodelist=[current_node, neighbor], node_color='r', node_size=1500)
            nx.draw_networkx_edges(G, pos, edgelist=[(current_node, neighbor)], width=2, edge_color='r')
        else:
            nx.draw_networkx_nodes(G, pos, nodelist=shortest_path[1:-1], node_color='yellow', node_size=1500)
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2, edge_color='yellow')
            nx.draw_networkx_nodes(G, pos, nodelist=[shortest_path[0]], node_color='green', node_size=1500)
            nx.draw_networkx_nodes(G, pos, nodelist=[shortest_path[-1]], node_color='red', node_size=1500)
        
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        
        if num < len(steps):
            current_distances = steps[num][2]
            distance_text = f'Найкоротші відстані: {current_distances}'
        else:
            final_distances = steps[-1][2]
            distance_text = f'Найкоротші відстані: {final_distances}'
        
        ax.set_title(distance_text, fontsize=12)
    
    ani = FuncAnimation(fig, update, frames=len(steps) + 1, interval=2000, repeat=False)
    plt.show()

root = tk.Tk()
root.title("Алгоритм Дейкстри")

input_frame = tk.Frame(root)
input_frame.pack()

vertices_label = tk.Label(input_frame, text="Кількість вершин")
vertices_label.pack(side=tk.LEFT, padx=5, pady=5)
vertices_entry = tk.Entry(input_frame, width=5)
vertices_entry.pack(side=tk.LEFT, padx=5, pady=5)
create_matrix_button = tk.Button(input_frame, text="Створити матрицю", command=create_matrix)
create_matrix_button.pack(side=tk.LEFT, padx=5, pady=5)

matrix_frame = tk.Frame(root)
matrix_frame.pack()

start_label = tk.Label(root, text="Початкова вершина")
start_entry = tk.Entry(root, width=5)
end_label = tk.Label(root, text="Кінцева вершина")
end_entry = tk.Entry(root, width=5)

submit_button = tk.Button(root, text="Пошук найкоротшого шляху", command=submit)
shortest_path_label = tk.Label(root, text="")
path_length_label = tk.Label(root, text="")

shortest_path_label.pack()
path_length_label.pack()

root.mainloop()