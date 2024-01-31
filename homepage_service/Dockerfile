FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app

RUN opentelemetry-bootstrap -a install

EXPOSE 80

ENTRYPOINT ["opentelemetry-instrument"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 


