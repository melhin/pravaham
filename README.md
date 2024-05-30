# Django Server-Sent Events (SSE) Demonstration

This project is a demonstration of Server-Sent Events (SSE) using Django without relying on third-party libraries. 
* An example shown here is of a real-time updates for logged-in users of posts where they have been mentioned

## Requirements

- Python (>=3.11)
- Django (>=5.0)

## Quick Start

**Before starting anything**

*Have a **.env** file in the repo. Copy the env.example and then put in your secret key*

In theory, you can run the following commands to start the project:

```bash
make start
```

This command uses Docker Compose and sets up four major parts:

1. Data systems: Postgres and Redis.
2. A synchronous Django app.
3. An asynchronous Django app.
4. Nginx for serving the application.

Ensure that you have Docker and Docker Compose installed on your machine.

## Important Routes

- **Home Page:**
  - [http://localhost:8000](http://localhost:8000)
  - The home page where you can log in or sign up.

- **:A place where posts mentioning you as a user are present**
  - [http://localhost:8000/posts/lobby/](http://localhost:8000/posts/lobby/)
  - No login required. Get the latest content from Mastodon.

## Docker Compose Components

1. **Data Systems:**
   - Postgres and Redis for data storage and stream handling.

2. **Synchronous Django App:**
   - Provides all the functionalities for the user like posts

3. **Asynchronous Django App:**
   - Enhances real-time capabilities asynchronously.

4. **Nginx:**
   - Serves the application and routes the traffic

## Usage

1. Create a user account and log in.
2. Navigate to the Posts link to see what pots you were mentioned on.
3. In another window click on create post and write a post mentioning yourself or other users

## Conversion to Real-time

This project also demonstrates how to quickly convert a polling-based system to real-time.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
