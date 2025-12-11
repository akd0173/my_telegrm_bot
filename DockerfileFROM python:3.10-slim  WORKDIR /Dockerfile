FROM python:3.10-slim

WORKDIR /app

# Install pip and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

CMD ["python", "bot.py"]
