# What is this project? 

This is a REST API for math functions, written in Python using the Flask microframework. Each math request will run in a different process for true parallelization. It uses JSON Web Tokens for authentication / authorization, and stores each request and result in a Postgres database for fast retrieval when a future identical request is made.  

The API implements the following mathematical operations: 

- Prime function  returns nth prime number.
- The Fibonacci function returns the nth number from the Fibonacci sequence.
- Power(pow) function returns the exponential of a base.
- Factorial function returns the factorial of a number
- Sum of natural numbers returns the sum of a range of numbers between 0 and x. 

In the bellow pictures we can see some examples of how the functions are working and the advantages that the database holds. 

<img width="1615" height="573" alt="Screenshot 2025-08-12 141347" src="https://github.com/user-attachments/assets/ef1a0777-95e2-4744-970b-d35796f5d8fb" />

<img width="1582" height="674" alt="Screenshot 2025-08-12 141530" src="https://github.com/user-attachments/assets/1b1bee06-9fb0-4f23-becc-3b5f856174e1" />

<img width="1562" height="562" alt="image" src="https://github.com/user-attachments/assets/e93e397b-62c6-4d09-b306-00b96310833c" />


As we can see the call of the 25000th prime number was stored in the database after the first call thus significantly reducing the processing time from 117ms at only 17ms at the second call. 

# What technologies were used to create this project? 

 - Windows 11 with WSL 
 - Python 3.12.3 
 - Flask 3.1.1 
 - Postgres 17 
 - Swagger 
 - Postman 
 - DBeaver 
 - Visual Studio Code 

 
# How to run the API? 

1.  Navigate to the project directory 
2.  Create a virtual environment using venv 
3.  Activate said environment 
4.  Install requirements with  `pip install –r requirements.txt`
5.  Download and run the Postgres docker image by running  `docker compose up` 
6.  Run the API with  `python app.py` 


At this point, the backend will start and listen on port 5000. In order to use the API, you’ll need to add users to the database, login with their credentials and use a JWT to call the API endpoints. 

7.  Connect to the database using a DBMS like DBeaver (check the database.py file for the connection string)
8.  Add entries to the users database table (use the NOW() function as a value for the created_at column)
9.  Use Swagger at http://localhost:5000/apidocs or Postman to call the login endpoint with the credentials from the newly created users
10. Grab the JWT and use it to call math endpoints
11. Use your web browser and navigate to http://localhost:5000/metrics to view a timeline of CPU and RAM usage 


<img width="1434" height="741" alt="Screenshot 2025-08-12 141714" src="https://github.com/user-attachments/assets/15609ccb-5802-46ae-b18a-45c421f6b6d6" />

<img width="1427" height="513" alt="Screenshot 2025-08-12 141744" src="https://github.com/user-attachments/assets/44f45532-e5c3-45e7-9584-5649fe52cedd" />

 
