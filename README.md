# Healthcare Backend API

Django REST Framework API with PostgreSQL, JWT authentication, patient and doctor records, and patient-doctor assignments.

## Setup

These instructions use **Windows Command Prompt (CMD)**. They assume Python and PostgreSQL are installed. If `py` is not recognized on your computer, use `python` as shown below.

### 1. Open the project folder and create a virtual environment

Open Command Prompt and change to the folder containing `manage.py` (replace the example path if you put the project somewhere else):

```cmd
cd /d D:\Django-Healthcare-Backend
python --version
python -m venv venv
venv\Scripts\activate
```

When activation succeeds, `(venv)` appears at the start of the prompt. Activate this environment again whenever you open a new Command Prompt for this project.

### 2. Install the project dependencies

Run these commands while the virtual environment is active:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` installs Django, Django REST Framework, JWT support, the PostgreSQL driver, and the environment-variable loader used by this project.

### 3. Create a PostgreSQL user and database

Make sure the PostgreSQL service is running. In **pgAdmin**, open the Query Tool connected to your PostgreSQL server, or open a terminal where `psql` is available and connect as a PostgreSQL administrator:

```cmd
psql -U postgres
```

At the PostgreSQL prompt (not the Windows CMD prompt), create a dedicated user and database. Replace the example password with a strong password of your own:

```sql
CREATE USER healthcare_user WITH PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

If using `psql`, exit it with:

```sql
\q
```

If the database or user already exists, do not create it again; use the existing details in the next step.

### 4. Create and configure your private `.env` file

Back in Command Prompt, copy the example configuration and open the new file:

```cmd
copy .env.example .env
notepad .env
```

Generate a strong Django secret key in another Command Prompt command:

```cmd
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the generated value into `SECRET_KEY` in `.env`. Set the database values to match the PostgreSQL user and database created above:

```dotenv
SECRET_KEY=paste-your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=the-password-you-set-for-healthcare_user
DB_HOST=localhost
DB_PORT=5432
```

Save and close Notepad. Keep `.env` private: it contains secrets and is excluded from Git by `.gitignore`. `DEBUG=True` is for local development only; do not use it in production.

### 5. Check the configuration and create database tables

With `(venv)` active and the PostgreSQL server running, execute:

```cmd
python manage.py check
python manage.py migrate
```

`check` reports configuration issues. `migrate` applies the project's database migrations and creates Django's and the healthcare app's tables in PostgreSQL.

### 6. Start the development server

```cmd
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. Leave the Command Prompt window open while using the API. Press `Ctrl+C` in that window to stop the server. The built-in Django server is for development, not production.

## Authentication

- `POST /api/auth/register/` with `{ "name": "Ada Lovelace", "email": "ada@example.com", "password": "a-strong-password" }`
- `POST /api/auth/login/` with `{ "username": "ada@example.com", "password": "a-strong-password" }`
- `POST /api/auth/token/refresh/` with `{ "refresh": "..." }`

Send the returned access token on protected requests as `Authorization: Bearer <access>`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/patients/` | Create a patient for the current user |
| GET | `/api/patients/` | List the current user's patients |
| GET, PUT, PATCH, DELETE | `/api/patients/<id>/` | Read, update, or delete an owned patient |
| POST | `/api/doctors/` | Create a doctor |
| GET | `/api/doctors/` | List doctors |
| GET, PUT, PATCH, DELETE | `/api/doctors/<id>/` | Read, update, or delete a doctor |
| POST | `/api/mappings/` | Assign a doctor using `{ "patient": 1, "doctor": 1 }` |
| GET | `/api/mappings/` | List assignments for the current user's patients |
| GET | `/api/mappings/<patient_id>/` | List doctors assigned to an owned patient |
| DELETE | `/api/mappings/<mapping_id>/` | Remove an assignment owned through the patient's user |

All record endpoints require JWT authentication. Patient and mapping access is scoped to the authenticated user's patients; doctor records are shared for reading and authenticated users can manage them. Duplicate assignments are rejected by a database uniqueness constraint.
