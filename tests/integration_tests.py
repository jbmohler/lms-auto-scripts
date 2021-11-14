import os
import json
import time
import contextlib
import requests

URL = os.getenv("LMS_URL")


def wait_healthy():
    while True:
        try:
            response = requests.get(f"{URL}/api/ping")
            if response.status_code == 200:
                break
        except Exception as e:
            print(str(e))
        time.sleep(3)


@contextlib.contextmanager
def lms_client_session():
    session = requests.Session()

    try:
        r = session.post(
            f"{URL}/api/session",
            data={
                "username": os.getenv("INIT_ADMIN_USER"),
                "password": os.getenv("INIT_ADMIN_PASSWORD"),
            },
        )
        if r.status_code >= 300:
            raise RuntimeError(f"Error logging in {r.text}")
        yield session
    finally:
        # session.
        session.close()


def read_something(session):
    response = session.get(f"{URL}/api/activities/list")
    print(json.dumps(json.loads(response.text), indent=4))
    print("Now ready to read in the test code")


def main():
    wait_healthy()
    with lms_client_session() as session:
        read_something(session)


if __name__ == "__main__":
    main()
