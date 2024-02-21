FROM python:3.11

# Create a non-root user
RUN useradd -m -u 1000 user

# Set user environment
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Copy files
COPY --chown=user . .

# Install dependencies
RUN pip install -r requirements.txt

# Command to run the application
CMD ["chainlit", "run", "app.py", "--port", "8000"]