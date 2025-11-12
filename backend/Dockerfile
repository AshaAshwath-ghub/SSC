FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your code
COPY . .
# Copy .env file
COPY .env .

# Expose port (if needed)
EXPOSE 8000

# Start the app
CMD ["python", "-m", "app.main"]