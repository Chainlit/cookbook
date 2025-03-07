FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY src/ ./src
COPY app.py setup.py .

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

COPY public/ ./public
COPY .chainlit/ ./.chainlit
COPY README.md chainlit.md .

# Set environment variables
ENV PYTHONUNBUFFERED 1
ARG PORT=5500

# Command to run the app
CMD python -m chainlit run app.py -h --host 0.0.0.0 --port ${PORT}

# Alternatively: Use entrypoint file
# COPY entrypoint.sh .
# RUN chmod +x ./entrypoint.sh
# ENTRYPOINT ["./entrypoint.sh"]