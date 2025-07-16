# Flask's endpoints are already asynchronous
# Custom math functions require multiprocessing
# Passing values between processes can be done using Queues
# https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues
import sys
from flask import Flask, request
import custom_math
from multiprocessing import Process, Queue

app = Flask(__name__)


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
    app.run(debug=True, host="0.0.0.0", port=5000)
