from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

def calculate_distance(route, matrix):
    total_dist = 0
    for i in range(len(route) - 1):
        total_dist += matrix[route[i]][route[i+1]]
    return total_dist

def two_opt_swap(route, i, k):
    new_route = route[0:i]
    new_route.extend(reversed(route[i:k + 1]))
    new_route.extend(route[k + 1:])
    return new_route

def optimize_route_2opt(initial_route, matrix):
    best_route = initial_route
    best_distance = calculate_distance(best_route, matrix)
    improved = True
    
    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for k in range(i + 1, len(best_route) - 1):
                new_route = two_opt_swap(best_route, i, k)
                new_distance = calculate_distance(new_route, matrix)
                
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_route = new_route
                    improved = True
    return best_route, best_distance

def nearest_neighbor(matrix, start_node=0):
    num_locations = len(matrix)
    unvisited = set(range(1, num_locations))
    route = [start_node]
    current_node = start_node
    
    while unvisited:
        next_node = min(unvisited, key=lambda node: matrix[current_node][node])
        unvisited.remove(next_node)
        route.append(next_node)
        current_node = next_node
        
    route.append(start_node)
    return route, calculate_distance(route, matrix)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    distance_matrix = data.get('matrix', [])
    initial_route = data.get('initial_route', [])

    if not distance_matrix or not initial_route:
        return jsonify({"error": "Invalid input parameters"}), 400

    # 1. Initial Route
    initial_distance = calculate_distance(initial_route, distance_matrix)

    # 2. 2-Opt Optimization
    opt_route, opt_distance = optimize_route_2opt(initial_route, distance_matrix)

    # 3. Nearest Neighbor
    nn_route, nn_distance = nearest_neighbor(distance_matrix)

    # 4. Randomized Search
    nodes = list(range(1, len(distance_matrix)))
    best_random_route = []
    best_random_distance = float('inf')

    for _ in range(100):
        random.shuffle(nodes)
        rand_route = [0] + nodes + [0]
        rand_dist = calculate_distance(rand_route, distance_matrix)
        if rand_dist < best_random_distance:
            best_random_distance = rand_dist
            best_random_route = rand_route

    return jsonify({
        "initial": {"route": initial_route, "distance": initial_distance},
        "opt": {"route": opt_route, "distance": opt_distance},
        "nn": {"route": nn_route, "distance": nn_distance},
        "random": {"route": best_random_route, "distance": best_random_distance},
        "num_nodes": len(distance_matrix)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)