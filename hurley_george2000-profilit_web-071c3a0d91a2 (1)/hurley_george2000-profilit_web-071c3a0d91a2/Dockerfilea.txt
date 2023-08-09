# Use the official Python image as the base image
FROM python:3.10

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the port on which Django will run
EXPOSE 8000

# Set the entry point for running the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
