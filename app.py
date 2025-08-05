# Flask's endpoints are already asynchronous
# Custom math functions require multiprocessing
# Passing values between processes can be done using Queues
# https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues
import os
import datetime
from dotenv import load_dotenv
import sys
from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt
import custom_math
from multiprocessing import Process, Queue
import crud
import atexit
from database import get_session
from models import MathRequest, MathResult, SystemMetric
from utils.monitoring.resource_monitor import ResourceMonitor

load_dotenv()  # This loads variables from .env into os.environ

monitor = ResourceMonitor(interval=1.0)
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)


@atexit.register
def stop_monitoring():
    if monitor.is_alive():
        monitor.stop()
        monitor.join()


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
        additional_claims = {"user_id": user.id}
        access_token = create_access_token(
            identity=email,
            expires_delta=datetime.timedelta(hours=6),
            additional_claims=additional_claims,
        )
        return jsonify(access_token=access_token)
    else:
        return "Invalid email or password", 401


@app.route("/metrics")
def metrics():
    start = request.args.get("start")
    end = request.args.get("end")
    with get_session() as session:
        query = session.query(SystemMetric)
        if start:
            start_dt = datetime.datetime.fromisoformat(start)
            query = query.filter(SystemMetric.timestamp >= start_dt)
        if end:
            end_dt = datetime.datetime.fromisoformat(end)
            query = query.filter(SystemMetric.timestamp <= end_dt)
        metrics = query.order_by(SystemMetric.timestamp).all()
    timestamps = [m.timestamp.isoformat() for m in metrics]
    cpu = [m.total_cpu_usage for m in metrics]
    ram = [m.total_ram_usage for m in metrics]
    # Render Jinja2 template and pass data as JSON
    return render_template(
        "metrics.html",
        timestamps=timestamps,
        cpu=cpu,
        ram=ram,
    )


@app.route("/prime", methods=["GET"])
@jwt_required()
def prime():
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400

    math_result = crud.get_math_result("prime", str({"count": count}))
    if math_result:
        math_request = MathRequest(
            requested_at=datetime.datetime.now(),
            user_id=get_jwt()["user_id"],
            result_id=math_result.id,
        )
        crud.save_math_request(math_request)
        return str(int(math_result.value))
    else:

        result_queue = Queue()

        def worker(n, queue):
            try:
                res = custom_math.nth_prime(n)
            except ValueError as e:
                res = str(e)
            queue.put(res)

        start_time = datetime.datetime.now()
        process = Process(target=worker, args=(count, result_queue))
        process.start()
        process.join()
        end_time = datetime.datetime.now()

        math_result = MathResult(
            operation="prime",
            parameters=str({"count": count}),
            value=result_queue.get(),
            calculation_time=int(
                (end_time - start_time) / datetime.timedelta(microseconds=1)
            ),
            user_id=get_jwt()["user_id"],
        )
        crud.save_math_result(math_result)
        math_request = MathRequest(
            requested_at=datetime.datetime.now(),
            user_id=get_jwt()["user_id"],
            result_id=math_result.id,
        )
        crud.save_math_request(math_request)
        return str(int(math_result.value))


@app.route("/fibonacci", methods=["GET"])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
    # Start the resource monitor thread
    if not monitor.is_alive():
        monitor.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
