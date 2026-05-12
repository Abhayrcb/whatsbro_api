FROM python:3.10

RUN mkdir  /api

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]