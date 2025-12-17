# 1) Use Python image from Docker Hub
FROM python:3.12

# 2) Inside the container, we'll work in /app
WORKDIR /app


# Install system packages needed for mysqlclient
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev build-essential \
    && rm -rf /var/lib/apt/lists/*


# 3) Copy requirement list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Now copy your whole Django project into the container
COPY . .

# 5) Open port 8000 so we can access Django
EXPOSE 8000

# 6) How to start Django inside the container
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]