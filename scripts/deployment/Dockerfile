FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY my_flask_simple.py /app/
COPY show_cmd /app/show_cmd
WORKDIR /app
CMD ["python", "my_flask_simple.py"]

