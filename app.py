import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

import os

app = Flask(__name__)

'''
from google.cloud import secretmanager

project_id = os.environ["GCP_PROJECT"]

secret_client = secretmanager.SecretManagerServiceClient()
db_name = f"projects/{project_id}/secrets/DB_NAME/versions/1"

db_pwd = f"projects/{project_id}/secrets/DB_PWD/versions/1"

db_name_response = secret_client.access_secret_version(name=db_name)
db_pwd_response = secret_client.access_secret_version(name=db_pwd)

secret_db_name_value = db_name_response.payload.data.decode('UTF-8')
secret_db_pwd_value = db_pwd_response.payload.data.decode('UTF-8')

def get_db_name(request):
    return secret_db_name_value

def get_db_pwd(request):
    return secret_db_pwd_value
'''


DB_NAME = os.environ["DB_NAME"]
DB_PWD = os.environ["DB_PWD"]

app.config[
    "MONGO_URI"] = "mongodb+srv://" + DB_NAME + ":password" + DB_PWD + "@clustertest.swcx9.mongodb.net/pythonFlask" \
                                                                       "?retryWrites=true&w=majority"

client = MongoClient("mongodb+srv://" + DB_NAME + ":password" + DB_PWD + "@clustertest.swcx9.mongodb.net/pythonFlask" \
                                                                         "?retryWrites=true&w=majority")

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