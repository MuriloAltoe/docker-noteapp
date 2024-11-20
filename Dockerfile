FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY templates/index.html .templates/

COPY . .

CMD ["python3", "app.py"]
