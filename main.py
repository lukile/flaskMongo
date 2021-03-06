import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

app.config[
    "MONGO_URI"] = "mongodb://" + DB_URI + ":" + DB_PORT + "/" + DB_NAME


client = MongoClient("mongodb://" + DB_URI + ":" + DB_PORT + "/" + DB_NAME)

db = client.pythonFlask
user_table = db.user

try:
    db.command("serverStatus")
except Exception as e:
    print(e)

else:
    print("You are connected")

client.close()


@app.route('/create/user/', methods=['POST'])
def create_user():
    record = json.loads(request.data)
    user = {"name": record["name"], "email": record["email"]}

    user_table.insert_one(user)

    return json.dumps(user, default=str)


@app.route('/', methods=['GET'])
def query_users():
    users = user_table.find({}, {'_id': False})

    format_users = []

    for user in users:
        format_users.append(user)

    return jsonify(format_users)


@app.route('/find/user/<name>', methods=['GET'])
def query_one_user(name):
    cursor = user_table.find({"name": name}, {'_id': False})
    list_cursor = list(cursor)

    user_data = json.dumps(list_cursor)

    return user_data


@app.route('/update/user/<name>', methods=["PUT"])
def update_user(name):
    record = json.loads(request.data)

    user = {"name": name}
    user_to_update = {"$set": {"email": record["email"]}}

    user_table.update_one(user, user_to_update)

    return query_one_user(name)


@app.route("/delete/user/<name>", methods=['DELETE'])
def delete_user(name):
    user = {"name": name}

    user_table.delete_one(user)

    return query_users()


if __name__ == '__main__':
    app.run()