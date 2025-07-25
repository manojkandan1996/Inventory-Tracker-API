from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)
api = Api(app)

inventory = []
item_id_counter = 1
LOW_STOCK_THRESHOLD = 5

class InventoryListResource(Resource):
    def get(self):
        return {"inventory": inventory}, 200

    def post(self):
        global item_id_counter
        data = request.get_json()

        if not data or 'item_name' not in data or 'quantity' not in data or 'category' not in data:
            raise BadRequest("Fields 'item_name', 'quantity', and 'category' are required.")

        try:
            quantity = int(data['quantity'])
            if quantity < 0:
                raise ValueError
        except ValueError:
            raise BadRequest("Quantity must be a non-negative integer.")

        item = {
            "id": item_id_counter,
            "item_name": data["item_name"],
            "quantity": quantity,
            "category": data["category"]
        }

        inventory.append(item)
        item_id_counter += 1

        return {"message": "Item added to inventory.", "item": item}, 201

class InventoryItemResource(Resource):
    def get(self, id):
        item = next((i for i in inventory if i['id'] == id), None)
        if not item:
            raise NotFound("Item not found.")
        return item, 200

    def put(self, id):
        data = request.get_json()
        item = next((i for i in inventory if i['id'] == id), None)
        if not item:
            raise NotFound("Item not found.")

        if 'item_name' in data:
            item['item_name'] = data['item_name']
        if 'quantity' in data:
            try:
                qty = int(data['quantity'])
                if qty < 0:
                    raise ValueError
                item['quantity'] = qty
            except ValueError:
                raise BadRequest("Quantity must be a non-negative integer.")
        if 'category' in data:
            item['category'] = data['category']

        response = {"message": "Item updated successfully.", "item": item}
        if item['quantity'] < LOW_STOCK_THRESHOLD:
            response["warning"] = "Stock is low!"

        return response, 200

    def delete(self, id):
        global inventory
        item = next((i for i in inventory if i['id'] == id), None)
        if not item:
            raise NotFound("Item not found.")
        inventory = [i for i in inventory if i['id'] != id]
        return {"message": f"Item {id} deleted from inventory."}, 200

# Register routes
api.add_resource(InventoryListResource, '/inventory')
api.add_resource(InventoryItemResource, '/inventory/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
