FROM python:3.9

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN python -m spacy download es_core_news_sm
CMD python index.py