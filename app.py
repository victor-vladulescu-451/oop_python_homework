# Flask's endpoints are already asynchronous
# Custom math functions require multiprocessing
# Passing values between processes can be done using Queues
# https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues
import sys
from flask import Flask, request
import custom_math
from multiprocessing import Process, Queue
import crud

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return "Request body must be JSON", 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return "Email and password are required", 400

    user = crud.get_user(email, password)
    if user:
        return "Logged in successfully", 200
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


@app.route("/pow", methods=["GET"])
def power():
    try:
        base = int(request.args.get("base", 1))
        exponent = int(request.args.get("exponent", 1))
    except ValueError:
        return "Invalid request, base and exponent parameters must be integers", 400
    result_queue = Queue()

    def worker(b, e, queue):
        try:
            res = custom_math.nth_pow(b, e)
        except ValueError as e:
            res = str(e)
        queue.put(res)

    process = Process(target=worker, args=(base, exponent, result_queue))
    process.start()
    process.join()

    result = result_queue.get()
    return str(result) 


@app.route("/factorial", methods=["GET"])
def factorial():
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400
    result_queue = Queue()

    def worker(n, queue):
        try:
            res = custom_math.nth_factorial(n)
        except ValueError as e:
            res = str(e)
        queue.put(res)

    process = Process(target=worker, args=(count, result_queue))
    process.start()
    process.join()

    result = result_queue.get()
    return str(result) 


@app.route("/sum_of_natural_numbers", methods=["GET"]) 
def sum_of_natural_numbers():
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400
    result_queue = Queue()

    def worker(n, queue):
        try:
            res = custom_math.nth_sum_of_natural_numbers(n)
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
