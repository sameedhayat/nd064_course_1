FROM python:3.8

COPY techtrends/ /app
WORKDIR /app

EXPOSE 3111

RUN pip install -r requirements.txt
RUN python init_db.py

CMD [ "python", "app.py" ]