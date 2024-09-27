# Connectify API

## Overview
This is a scalable and secure social networking application API built using Django Rest Framework. It includes functionalities such as user management, friend request handling, notifications, and activity logging.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation Steps](#installation-steps)
- [API Documentation](#api-documentation)
- [Design Choices](#design-choices)
- [License](#license)

## Features
- **User Management**
  - User registration and login with email.
  - Token-based authentication (JWT) with refresh capabilities.
  - Role-based access control (RBAC).
  
- **User Search**
  - Search for users by email or name with pagination.
  
- **Friend Request Management**
  - Send, accept, and reject friend requests.
  - Rate limiting for friend requests to prevent spam.
  - Block/unblock users.

- **Friends List & Pending Requests**
  - List of friends and pending friend requests with pagination.

- **Notifications**
  - Log and retrieve user activities.
  
- **Data Privacy & Security**
  - Encrypt sensitive user data.
  - Protection against common security vulnerabilities.
  
- **Performance Optimization**
  - Caching with Redis and Django’s optimization techniques.

## Technologies Used
- **Backend**: Django, Django Rest Framework
- **Database**: PostgreSQL
- **Caching**: In-memory caching
- **Containerization**: Docker
- **Deployment**: Render
- **Authentication**: JWT (JSON Web Tokens)

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- PostgreSQL (for local development or You can also use [Railway](https://railway.app/)

## Installation Step (Docker Hub)

To get started, pull the Docker image from Docker Hub:

```bash
docker pull lesanabbas/social-media
```
Now, create a container using that image
```bash
docker run -p 8001:8001 \
  -e POSTGRES_NAME=railway \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=uWWkxgLnAhWEwaRENPUFsrfnHOIlBJwg \
  lesanabbas/social-media

```



## Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/lesanabbas/Connectify.git
cd Connectify
```
### Step 2: Set Up Environment Variables
Create a .env file in the root directory and add the necessary environment variables.
```bash
touch social_network/.env

```
You can use this Database or else you can Create new one from railway
```bash
POSTGRES_NAME=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=uWWkxgLnAhWEwaRENPUFsrfnHOIlBJwg
POSTGRES_HOST=junction.proxy.rlwy.net
POSTGRES_PORT=15884
```
### Step 3: Build Image and Run the Docker Container
```bash
docker-compose --env-file social_network/.env up --build
```
### Step 4: Run Migrations (Optional)
This is the optional step if you using new Database the need to migrate or else you can skip this step
```bash
docker ps  # will list down all running container 
docker exec -it <CONTAINER-NAME> python manage.py migrate

```
### Step 5: Create a Superuser (Optional)
To create an admin user, run:
```bash
docker exec -it <CONTAINER-NAME> python manage.py createsuperuser

```

### Step 6: Access the API

The API will be accessible at http://localhost:8001/


## API Documentation

## Structure
In a RESTful API, endpoints (URLs) define the structure of the API and how end users access data from our application using the HTTP methods - GET, POST, PUT, DELETE. Endpoints should be logically organized around _collections_ and _elements_, both of which are resources.

In our case, we have multiple resources, including `users`, `friends`, and `notifications`. Here are the following URLs:

### Users
| Endpoint          | HTTP Method | CRUD Method | Result                             |
|-------------------|-------------|-------------|------------------------------------|
| `/api/users/search/?query=`     | GET         | READ        | search user                      |
| `/api/users/block/` | POST         | CREATE        | Block a user                  |
| `/api/users/unblock/`     | DELETE        | REMOVE      | Unblock the user                  |
| `/api/users/activities/` | GET      | READ        | Get All activities of that user      |

### Friend Requests
| Endpoint                       | HTTP Method | CRUD Method | Result                                       |
|--------------------------------|-------------|-------------|----------------------------------------------|
| `/api/users/friend-request/`        | POST        | CREATE      | Send a friend request                        |
| `/api/users/friend-request/`        | PUT        | UPDATE      | Accept or Reject a friend request                      |
| `/api/users/friends/`               | GET         | READ        | List all friends                            |
| `/api/users/pending-requests/`       | GET         | READ        | List all pending friend requests            |

### Notifications
| Endpoint             | HTTP Method | CRUD Method | Result                           |
|----------------------|-------------|-------------|----------------------------------|
| `/api/users/notifications/` | GET         | READ        | Get all notifications            |

### Authentication
| Endpoint             | HTTP Method | CRUD Method | Result                                       |
|----------------------|-------------|-------------|----------------------------------------------|
| `/api/users/login/`        | POST        | CREATE      | User login and receive JWT tokens          |
| `/api/users/signup/`       | POST        | CREATE      | User registration                            |

### Example Usage
- **Get All Users**: `GET /api/users/`
- **Create User**: `POST /api/users/`
- **Search Users**: `GET /api/users/search/?q=keyword`
- **Send Friend Request**: `POST /api/friends/request/`
- **Accept Friend Request**: `POST /api/friends/accept/`
- **Get Notifications**: `GET /api/notifications/`

## Design Choices

- `Architecture:` The application is designed using the Django REST Framework to create a RESTful API. This architecture promotes the separation of concerns, enhances maintainability, and allows for scalable API development.

- `Database Choice:` PostgreSQL was chosen for its advanced features like full-text search, which optimizes user search functionalities and supports efficient data handling for a large dataset.

- `Caching Strategy:` The application utilizes Django's default in-memory caching for 10 to 15 minutes, improving performance by caching frequently accessed data and reducing database load.

- `Security Measures:` Implemented JWT for secure authentication, along with email encryption using Django’s built-in cryptography module to protect sensitive user information. Additionally, measures are in place to guard against common vulnerabilities such as SQL injection and XSS.

## Postman APIs Collection
You can test the API using [Postman Collection](https://documenter.getpostman.com/view/14305486/2sAXqy2ypB).

## Deploying on AWS EC2
- Launch an EC2 Instance:

  - Go to the AWS Management Console.
  - Launch a new EC2 instance using an Amazon Linux or Ubuntu AMI.

- Connect to your EC2 instance:
```bash
ssh -i <your_key_pair.pem> ec2-user@<your_instance_public_dns>
```

- Install Docker on EC2:

```bash
sudo yum update -y         # For Amazon Linux
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user

```

- Pull and run the Docker image on EC2:

```bash
docker pull lesanabbas/social-media
docker run -p 8001:8001 \
  -e POSTGRES_NAME=railway \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=uWWkxgLnAhWEwaRENPUFsrfnHOIlBJwg \
  lesanabbas/social-media

```

- Access your API:
  Open a web browser and go to
```bash
 http://<your_instance_public_dns>:8000
```
