FROM python:3.11

COPY . /APP_A

WORKDIR /APP_A

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "service_a.py:app", "--host=0.0.0.0", "--port=80"] 


