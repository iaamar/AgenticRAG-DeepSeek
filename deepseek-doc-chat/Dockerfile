# Use the official Python image from the Docker Hub
FROM python:3.11

# Install dependencies
RUN apt update && apt install -y \
    libc6 \
    libc6-dev \
    build-essential \
    libstdc++6


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --force-reinstall semantic_text_splitter

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app_deep_seek.py"]