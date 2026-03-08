# jPoll - The Poll of the Day App

jPoll is a web-based voting application that allows users to answer a single poll of the day and view the aggregated results. It features user authentication, a dedicated admin zone for resetting votes using a secure token, and a JSON endpoint for fetching live results.

## Features

* **Daily Poll**: Users can view the current question and its available options.
* **Voting System**: Registered users can cast a single vote. 
* **Live Results**: Anyone can view the current vote counts and percentages without needing to vote.
* **User Authentication**: Full sign-up and sign-in functionality.
* **Admin Controls**: Administrators can reset the poll votes completely, provided they supply the correct server-side reset token.
* **JSON API**: Real-time poll results can be fetched via a dedicated `/poll/results` endpoint.
* **Bug Reporting**: A built-in form for users to report issues directly to the admins.

## Tech Stack

* **Backend**: Python, Flask
* **Database**: MySQL, SQLAlchemy (ORM), PyMySQL (Driver)
* **Frontend**: HTML, Jinja2 Templates, CSS
* **Configuration**: python-dotenv

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:
* Python 3.8 or higher
* MySQL Server
* Git 

---

## Step-by-Step Setup Guide

### 1. Download the Project

Navigate to your desired directory and clone or extract the project files.

### 2. Set Up a Virtual Environment

It is highly recommended to isolate the project dependencies using a virtual environment.

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages from the requirements file.

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL Database

Log into your MySQL server and create a dedicated database for the application.

```sql
CREATE DATABASE jpoll_db;
CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'db_password';
GRANT ALL PRIVILEGES ON jpoll_db.* TO 'db_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment Variables

Create a file named `.env` in the root directory of the project (next to `app.py`). Add the following configuration variables, updating the database URI to match the credentials you created in the previous step.

```text
SECRET_KEY=your_secure_random_secret_key
SQLALCHEMY_DATABASE_URI=mysql+pymysql://db_user:db_password@localhost/jpoll_db
RESET_TOKEN=superadmin123
```

### 6. Initialize the Database

Generate the database tables and populate the default data (including the default admin account and the first poll).

```bash
flask --app app init-db
```

### 7. Run the Application

Start the Flask development server.

```bash
flask --app app run --debug
```

The application will now be accessible in your web browser at `http://127.0.0.1:5000`.

---

## Usage Guide

### Default Accounts

The initialization script creates a default administrator account. You can log in with:
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

### ModuleNotFoundError: No module named 'flask'

Your virtual environment is either not activated or the dependencies were not installed properly. Run the activation command again and ensure `pip install -r requirements.txt` finishes without errors.

### sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied for user...")

The application cannot connect to the MySQL database. 
* Verify that your MySQL server is running.
* Double-check the `SQLALCHEMY_DATABASE_URI` in your `.env` file. It must exactly match the username, password, and database name configured in MySQL.

### Database Initialization Does Not Create Tables

If running `flask --app app init-db` does nothing or throws an error:
* Ensure you are running the command in the same directory as `app.py`.
* Check that your `.env` file is formatted correctly with no spaces around the equals signs.

### "Invalid reset token" Error

When trying to reset the poll as an admin, if you receive this error, the token you typed in the browser does not match the `RESET_TOKEN` value in your `.env` file. Ensure there are no trailing spaces in your `.env` file.

### Port 5000 is Already in Use

If Flask fails to start because the port is occupied, you can run the app on a different port:
```bash
flask --app app run --port 5001 --debug
```