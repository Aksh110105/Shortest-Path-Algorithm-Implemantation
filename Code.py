from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import heapq

app = Flask(__name__)
CORS(app)

# Define graph with Dijkstra's algorithm
G = {}
locations = {
    'Dehradun': (30.3165, 78.0322),
    'Delhi': (28.6139, 77.2090),
    'Chakrata': (30.7494, 77.9154),
    'Mumbai': (19.0760, 72.8777),
    'Bangalore': (12.9716, 77.5946),
    'Chennai': (13.0827, 80.2707),
    'Jammu': (32.7266, 74.8570),
    'Lucknow': (26.8467, 80.9462)
}

# Adding edges (distances in km for simplicity)
distances = {
    ('Dehradun', 'Delhi'): 240,
    ('Dehradun', 'Chakrata'): 90,
    ('Delhi', 'Mumbai'): 1400,
    ('Delhi', 'Chennai'): 2200,
    ('Mumbai', 'Bangalore'): 980,
    ('Bangalore', 'Chennai'): 350,
    ('Delhi', 'Lucknow'): 550,
    ('Lucknow', 'Chennai'): 2100,
    ('Chakrata', 'Jammu'): 550,
    ('Dehradun', 'Jammu'): 520
}

# Initialize the graph
for loc1, loc2 in distances.keys():
    weight = distances[(loc1, loc2)]
    if loc1 not in G:
        G[loc1] = {}
    if loc2 not in G:
        G[loc2] = {}
    G[loc1][loc2] = weight
    G[loc2][loc1] = weight

def dijkstra(graph, start, end):
    queue = []
    heapq.heappush(queue, (0, start))
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.reverse()

    return path, distances[end]

# Calculate route
@app.route('/route', methods=['GET'])
def calculate_route():
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        path, distance = dijkstra(G, start, end)
        # Assume an average speed of 60 km/h for travel time calculation
        travel_time = distance / 60.0
        return jsonify({
            'path': path,
            'distance': distance,
            'travel_time': travel_time
        })
    except KeyError:
        return jsonify({'error': 'Invalid location selected'}), 404

# Route for hover-based distance and time preview
@app.route('/preview', methods=['GET'])
def preview_route():
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        distance = dijkstra(G, start, end)[1]
        travel_time = distance / 60.0
        return jsonify({
            'distance': distance,
            'travel_time': travel_time
        })
    except KeyError:
        return jsonify({'error': 'Invalid location selected for preview'}), 404

if __name__ == '__main__':
    app.run(debug=True)
