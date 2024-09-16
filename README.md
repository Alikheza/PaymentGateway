
# Payment Gateway

Project Overview

This project demonstrates a microservice architecture for a payment gateway, leveraging FastAPI for efficient API development and RabbitMQ for asynchronous communication between microservices. While Redis is used as a database in this educational context, it's generally not recommended as the primary database for production environments. For more demanding workloads or complex data requirements, consider using a relational database like PostgreSQL, MySQL. These databases offer robust features, transaction support, and better scalability for long-term storage and retrieval of critical data.






## How it work
Upon product registration, users acquire full CRUD authority.

Initiating a payment through the API triggers a background check for availability via a message broker. If confirmed, the order advances to payment processing. A bank-issued payment gateway code is obtained to securely request payment. To simplify the process, we've simulated the bank's payment portal steps with a brief delay. Users can monitor their purchase status using a separate payment API.

![App diagram]()
## Tech Stack

**Client:** *

**Server:** Fastapi, redis, RabbitMQ


## Installation

To properly set up and deploy your project, follow these steps to separate the product and payment functionalities onto different servers. Additionally, ensure that Redis and RabbitMQ services are running, as they are crucial for the system's functionality.
Setup Instructions

Clone the Project Use the command:    
    
    git clone https://github.com/Alikheza/PaymentGateway.git

Navigate to the Project Directory:

    cd <project-directory>

Add Environment Variables: Create or update the .env file with the necessary environment variables.

    redis_username 
    redis_password 
    redis_database  
    redis_host 
    redis_port 
    RabbitMQ_host 
    RabbitMQ_port  
    RabbitMQ_user 
    RabbitMQ_password 

Deployment Options


Option 1: Deploy via Docker


Build the Docker Image
        
    docker build . -t <image-name>

Run the Docker Container

    docker run <image-name>

Option 2: Deploy via Script

Create a Python Virtual Environment
    
    python -m venv .venv

Activate the Virtual Environment

    On Windows: venv\Scripts\activate
    On macOS/Linux: source venv/bin/activate

Install Requirements

    pip install -r requirements.txt

Start the Project
    
    fastapi run app/main.py --port 80 

Make sure to replace placeholder <image-name> with the actual values specific to your project.