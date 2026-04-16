FROM python:3.10-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first (for docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy entire project
COPY . .

# expose Flask port
EXPOSE 5000

# run the app
CMD ["python", "app.py"]
