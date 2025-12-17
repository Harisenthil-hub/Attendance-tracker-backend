HOW TO RUN BACKEND (NO PYTHON INSTALLATION REQUIRED)

1. Install Docker Desktop.

2. Unzip the backend folder.

3. Go into the unzipped folder in terminal (where docker-compose.yml is).

4. Create .env file:
     copy .env.example → .env
     edit DB_PASSWORD and SECRET_KEY inside .env

5. Run backend:
     docker-compose up --build

6. (Optional for first time) Create admin user:
     docker exec -it django_web python manage.py create_first_admin
