FROM python:3.10

# 1. Use /app as a standard working directory to match your docker-compose volume
WORKDIR /app

# 2. Copy and install dependencies first (better for build caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of your project files (core, chat, manage.py, etc.)
COPY . .

EXPOSE 8000

# 4. FIXED: Point to 'core.asgi' instead of 'api.asgi'
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
