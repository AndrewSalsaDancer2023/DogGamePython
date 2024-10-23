FROM python:3.12
RUN mkdir app
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 80
CMD  ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]