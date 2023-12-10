# Django Real-time Server-Sent Events (SSE) Demonstration

This project is a demonstration of Server-Sent Events (SSE) using Django without relying on third-party libraries. It includes two cases:
* real-time updates for logged-in users and their posts
* streaming the Mastodon firehose using Redis streams.

## Requirements

- Python (>=3.11)
- Django (>=5.0)

## Quick Start

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

- **Mastodon Content:**
  - [http://localhost:8000/posts/content/](http://localhost:8000/posts/content/)
  - No login required. Get the latest content from Mastodon.

- **Real-time Content Stream (Load Test):**
  - [http://localhost:8000/realtime/content/stream/](http://localhost:8000/realtime/content/stream/)
  - For load testing purposes.

## Docker Compose Components

1. **Data Systems:**
   - Postgres and Redis for data storage and stream handling.

2. **Synchronous Django App:**
   - Provides all the functionalities for the user like posts and mastadon content

3. **Asynchronous Django App:**
   - Enhances real-time capabilities asynchronously.

4. **Nginx:**
   - Serves the application and routes the traffic

## Usage

### Case 1: Real-time updates for logged-in users and their posts

1. Create a user account and log in.
2. Navigate to the User Posts link to see what logged in user posts have been made.
3. In another window or possibly as another user you 

### Case 2: Streaming the Mastodon firehose

1. Navigate to the Mastodon firehose stream.
   ```bash
   http://localhost:8000/firehose/
   ```
2. Open the browser's console to view real-time updates from the Mastodon firehose.

### Load Testing

1. Access the real-time content stream for load testing.
   ```bash
   http://localhost:8000/realtime/content/stream/
   ```
2. Run the following command for load testing.
   ```bash
   make runfeed
   ```

## Conversion to Real-time

This project also demonstrates how to quickly convert a polling-based system to real-time.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
