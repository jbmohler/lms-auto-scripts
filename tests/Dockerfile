FROM python:3.10

RUN pip install --upgrade pip

WORKDIR /tests
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY integration_tests.py integration_tests.py
RUN ls -la /tests

CMD python integration_tests.py

