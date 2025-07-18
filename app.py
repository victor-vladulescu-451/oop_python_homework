# Flask's endpoints are already asynchronous
# Custom math functions require multiprocessing
# Passing values between processes can be done using Queues
# https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues
import datetime
import os
from dotenv import load_dotenv
import sys
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
import custom_math
from multiprocessing import Process, Queue
import crud

load_dotenv()  # This loads variables from .env into os.environ

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return "Request body must be JSON", 400

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return "Email and password are required", 400

    user = crud.get_user(email, password)
    if user:
        access_token = create_access_token(
            identity=email, expires_delta=datetime.timedelta(hours=6)
        )
        return jsonify(access_token=access_token)
    else:
        return "Invalid email or password", 401


@app.route("/prime", methods=["GET"])
def prime():
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400
    result_queue = Queue()

    def worker(n, queue):
        try:
            res = custom_math.nth_prime(n)
        except ValueError as e:
            res = str(e)
        queue.put(res)

    process = Process(target=worker, args=(count, result_queue))
    process.start()
    process.join()

    result = result_queue.get()
    return str(result)


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400
    result_queue = Queue()

    def worker(n, queue):
        try:
            res = custom_math.nth_fibonacci(n)
        except ValueError as e:
            res = str(e)
        queue.put(res)

    process = Process(target=worker, args=(count, result_queue))
    process.start()
    process.join()

    result = result_queue.get()
    return str(result)


if __name__ == "__main__":
    sys.set_int_max_str_digits(10000000)  # Increase max digits for large numbers
    crud.create_tables()  # Ensure tables are created before running the app
    app.run(debug=True, host="0.0.0.0", port=5000)
