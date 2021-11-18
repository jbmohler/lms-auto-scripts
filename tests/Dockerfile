FROM python:3.10

RUN pip install --upgrade pip

WORKDIR /tests
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ytclient.py ytclient.py
COPY mecolm-0.1-py3-none-any.whl mecolm-0.1-py3-none-any.whl

RUN pip install mecolm-0.1-py3-none-any.whl

COPY integration_tests.py integration_tests.py
COPY create_role.py create_role.py
COPY create_users.py create_users.py
# COPY create_accounts.py
# COPY create_contacts.py
# COPY create_transactions.py

RUN ls -la /tests

CMD python integration_tests.py sleep
