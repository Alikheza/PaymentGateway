FROM python:3.12

WORKDIR /src

COPY ./requirements.txt /src

RUN pip install -r requirements.txt

COPY . .

RUN mkdir logs

ENV PYTHONPATH /src

CMD ["fastapi", "run", "app/main.py", "--port", "80"]

