FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /stockproject

COPY requirements.txt /stockproject/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /stockproject/

EXPOSE 8000

#CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]