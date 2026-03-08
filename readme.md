# jPoll - The Poll of the Day App

jPoll is a web-based voting application that allows users to answer a single poll of the day and view the aggregated results. It features user authentication, a dedicated admin zone for resetting votes using a secure token, and a JSON endpoint for fetching live results. The entire application is containerized using Docker for easy deployment.

## Features

* **Daily Poll**: Users can view the current question and its available options.
* **Voting System**: Registered users can cast a single vote. 
* **Live Results**: Anyone can view the current vote counts and percentages without needing to vote.
* **User Authentication**: Full sign-up and sign-in functionality.
* **Admin Controls**: Administrators can reset the poll votes completely, provided they supply the correct server-side reset token.
* **JSON API**: Real-time poll results can be fetched via a dedicated `/poll/results` endpoint.
* **Bug Reporting**: A built-in form for users to report issues directly to the admins.
* **Dockerized Environment**: Quick and consistent deployment using Docker and Docker Compose.
* **Auto-Initialize**: The database schema and default admin user automatically initialize on startup.
* **Development Mode**: Integrated setup for hot-reloading Flask inside Docker during local development.

## Tech Stack

* **Backend**: Python, Flask
* **Database**: MySQL, SQLAlchemy (ORM), PyMySQL (Driver)
* **Frontend**: HTML, Jinja2 Templates, CSS
* **Infrastructure**: Docker, Docker Compose

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:
* Docker
* Docker Compose
* Git 

---

## Step-by-Step Setup Guide

### 1. Download the Project

Navigate to your desired directory and clone or extract the project files.

### 2. Configure Environment Variables

Create a copy of the template environment file and rename it to `.env` in the root directory of the project.

```bash
cp .env.template .env
```

Open the `.env` file and populate it with your specific credentials.

```text
APP_PORT=8000
SECRET_KEY=your_secure_random_secret_key
MYSQL_DATABASE=jpoll_db
MYSQL_USER=jpoll_user
MYSQL_PASSWORD=jpoll_password
MYSQL_ROOT_PASSWORD=root_password
RESET_TOKEN=superadmin123
```

### 3. Build and Run the Containers (Production Mode)

Use Docker Compose to build the web application image and start both the web and database containers in the background.

```bash
docker compose up -d --build
```

The database tables and initial data will be automatically generated upon startup. The application will be accessible in your web browser at `http://localhost:8000` (or the port you defined in `APP_PORT`).

---

## Development Mode

To actively develop the application and take advantage of Flask's auto-reload functionality while still using the Docker database setup, use the development override file.

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

---

## Usage Guide

### Default Accounts

The startup script creates a default administrator account. You can log in immediately with:
* **Email**: `admin@jpoll.com`
* **Password**: `admin`

### Resetting the Poll

To test the admin reset feature:
1. Log in with the admin account.
2. Scroll to the bottom of the "Today's poll" page to find the "Admin zóna".
3. Enter the exact token specified in your `.env` file for the `RESET_TOKEN` variable.
4. Click "Reset votes".

---

## Troubleshooting

### Database Fails to Initialize

If the application throws an error when attempting to auto-create tables:
* The MySQL container might still be booting up. Wait 10-15 seconds and restart the web container.
* Ensure the database variables in your `.env` file contain no trailing spaces or special characters.

### "Invalid reset token" Error

When trying to reset the poll as an admin, if you receive this error, the token you typed in the browser does not match the `RESET_TOKEN` value in your `.env` file. Ensure there are no trailing spaces in your `.env` file.

### Port is Already in Use

If Docker fails to start the web container because the port is occupied, you can change the host port mapping in your `.env` file to a different port:

```text
APP_PORT=8080
```

Then rebuild the containers:

```bash
docker compose up -d
```