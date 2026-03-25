import json
import os
from flask import Flask, jsonify, request

# Flask equivalent of @SpringBootApplication
app = Flask(__name__)

# Load customers.json once when server starts
# Same idea as loading data into memory at startup in Spring Boot
def load_customers():
    # __file__ is this app.py file's location
    # We go up one level then into data/customers.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'data', 'customers.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['customers']

CUSTOMERS = load_customers()


# GET /api/health
# Same as @GetMapping("/api/health") in Spring Boot
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "service": "mock-server"}), 200


# GET /api/customers?page=1&limit=10
# Same as @GetMapping("/api/customers") with @RequestParam in Spring Boot
@app.route('/api/customers', methods=['GET'])
def get_customers():
    # request.args.get() = @RequestParam in Spring Boot
    # int() converts string to integer, default values = 1 and 10
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    # Pagination logic — same math you'd use in Spring Boot manually
    # page=1, limit=10 → start=0, end=10
    # page=2, limit=10 → start=10, end=20
    start = (page - 1) * limit
    end = start + limit

    # Slice the list — Python list slicing [start:end]
    paginated = CUSTOMERS[start:end]

    return jsonify({
        "data": paginated,
        "total": len(CUSTOMERS),
        "page": page,
        "limit": limit
    }), 200


# GET /api/customers/C001
# Same as @GetMapping("/api/customers/{id}") with @PathVariable in Spring Boot
@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    # next() with default None = same as Optional.ofNullable() in Java
    customer = next((c for c in CUSTOMERS if c['customer_id'] == customer_id), None)

    if customer is None:
        # 404 same as ResponseEntity.notFound() in Spring Boot
        return jsonify({"error": "Customer not found", "customer_id": customer_id}), 404

    return jsonify({"data": customer}), 200


# Entry point — same as main() in Spring Boot
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)