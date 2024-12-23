# Use the Python 3.11 base image
FROM python:3.11
RUN apt-get update && apt-get install -y curl npm
RUN npm install -g ngrok
# Set the working directory inside the container to /code
WORKDIR /app

# Copy the requirements.txt to the container's /code directory
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the entire backend folder into the container
COPY . /app/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
