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
from flasgger import Swagger

load_dotenv()  # This loads variables from .env into os.environ

monitor = ResourceMonitor(interval=1.0)
app = Flask(__name__)
SWAGGER_TEMPLATE = {
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme."
            + 'Example: "Authorization: Bearer {token}"',
        }
    },
    "security": [{"Bearer": []}],
}

swagger = Swagger(app, template=SWAGGER_TEMPLATE)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)


@atexit.register
def stop_monitoring():
    if monitor.is_alive():
        monitor.stop()
        monitor.join()


@app.route("/login", methods=["POST"])
def login():
    """
    User login endpoint.
    ---
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Logged in successfully
      400:
        description: Request body must be JSON or missing fields
      401:
        description: Invalid email or password
    """
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
    """
    Get system metrics.
    Retrieves CPU and RAM usage metrics.
    ---
    parameters:
      - name: start
        in: query
        type: string
        required: false
        description: Starting datetime in ISO format (e.g., 2023-10-01T00:00:00Z)
      - name: end
        in: query
        type: string
        required: false
        description: Ending datetime in ISO format (e.g., 2023-10-01T23:59:59Z)
    responses:
      200:
        description: Retrieved system metrics
    """
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
    """
    Get the nth prime number.
    ---
    parameters:
      - name: count
        in: query
        type: integer
        required: true
        description: The position of the prime number to return.
    responses:
      200:
        description: The nth prime number
        schema:
          type: string
      400:
        description: Invalid request, count parameter must be a positive integer
    """
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
        return str(math_result.value)
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
        return str(math_result.value)


@app.route("/fibonacci", methods=["GET"])
@jwt_required()
def fibonacci():
    """
    Get the nth Fibonacci number.
    ---
    parameters:
      - name: count
        in: query
        type: integer
        required: true
        description: The position requested from the Fibonacci sequence.
    responses:
      200:
        description: The nth Fibonacci number
        schema:
          type: string
      400:
        description: Invalid request, count parameter must be a positive integer
    """
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400

    math_result = crud.get_math_result("fibonacci", str({"count": count}))
    if math_result:
        math_request = MathRequest(
            requested_at=datetime.datetime.now(),
            user_id=get_jwt()["user_id"],
            result_id=math_result.id,
        )
        crud.save_math_request(math_request)
        return str(math_result.value)

    else:
        result_queue = Queue()

        def worker(n, queue):
            try:
                res = custom_math.nth_fibonacci(n)
            except ValueError as e:
                res = str(e)
            queue.put(res)

        start_time = datetime.datetime.now()
        process = Process(target=worker, args=(count, result_queue))
        process.start()
        process.join()
        end_time = datetime.datetime.now()

        math_result = MathResult(
            operation="fibonacci",
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
        return str(math_result.value)


@app.route("/factorial", methods=["GET"])
@jwt_required()
def factorial():
    """
    Calculate factorial of N.
    ---
    parameters:
      - name: count
        in: query
        type: integer
        required: true
        description: The factorial of N.
    responses:
      200:
        description: The factorial of N
        schema:
          type: string
      400:
        description: Invalid request, count parameter must be a positive integer
    """
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400

    math_result = crud.get_math_result("factorial", str({"count": count}))
    if math_result:
        math_request = MathRequest(
            requested_at=datetime.datetime.now(),
            user_id=get_jwt()["user_id"],
            result_id=math_result.id,
        )
        crud.save_math_request(math_request)
        return str(math_result.value)

    else:

        result_queue = Queue()

        def worker(n, queue):
            try:
                res = custom_math.nth_factorial(n)
            except ValueError as e:
                res = str(e)
            queue.put(res)

        start_time = datetime.datetime.now()
        process = Process(target=worker, args=(count, result_queue))
        process.start()
        process.join()
        end_time = datetime.datetime.now()

        math_result = MathResult(
            operation="factorial",
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
        return str(math_result.value)


@app.route("/sum_of_natural_numbers", methods=["GET"])
@jwt_required()
def sum_of_natural_numbers():
    """
    Get the sum of all integers from 1 to N.
    ---
    parameters:
      - name: count
        in: query
        type: integer
        required: true
        description: The number to calculate the sum for.
    responses:
      200:
        description: The sum of integer range
        schema:
          type: string
      400:
        description: Invalid request, count parameter must be a positive integer
    """
    try:
        count = int(request.args.get("count", 1))
    except ValueError:
        return "Invalid request, count parameter must be a positive integer", 400

    math_result = crud.get_math_result("sum_of_natural_numbers", str({"count": count}))
    if math_result:
        math_request = MathRequest(
            requested_at=datetime.datetime.now(),
            user_id=get_jwt()["user_id"],
            result_id=math_result.id,
        )
        crud.save_math_request(math_request)
        return str(math_result.value)

    else:
        result_queue = Queue()

        def worker(n, queue):
            try:
                res = custom_math.nth_sum_of_natural_numbers(n)
            except ValueError as e:
                res = str(e)
            queue.put(res)

        start_time = datetime.datetime.now()
        process = Process(target=worker, args=(count, result_queue))
        process.start()
        process.join()
        end_time = datetime.datetime.now()

        math_result = MathResult(
            operation="sum_of_natural_numbers",
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
        return str(math_result.value)


@app.route("/pow", methods=["GET"])
@jwt_required()
def power():
    """
    Calculate base raised to the exponent.
    ---
    parameters:
      - name: base
        in: query
        type: integer
        required: true
        description: The base number.
      - name: exponent
        in: query
        type: integer
        required: true
        description: The exponent.
    responses:
      200:
        description: The result of base ** exponent
        schema:
          type: string
      400:
        description: Invalid request, base and exponent parameters must be integers
    """
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


if __name__ == "__main__":
    sys.set_int_max_str_digits(0)  # Increase max digits for large numbers
    crud.create_tables()  # Ensure tables are created before running the app
    # Start the resource monitor thread
    if not monitor.is_alive():
        monitor.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
