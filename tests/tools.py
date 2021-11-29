import os
import contextlib
import ytclient


INIT_ADMIN_USER = os.getenv("INIT_ADMIN_USER")
INIT_ADMIN_PASSWORD = os.getenv("INIT_ADMIN_PASSWORD")
LMS_URL = os.getenv("LMS_URL")


@contextlib.contextmanager
def lms_session(creds=None):
    """
    :param creds: any of the following
     - dict with username & password keys
     - (default) None -- gets username & password from environment
     - empty dict -- does not authenticate
    """

    if creds is None:
        # default to admin from the environment
        creds = {"username": INIT_ADMIN_USER, "password": INIT_ADMIN_PASSWORD}

    session = ytclient.RtxSession(LMS_URL)
    if len(creds):
        session.authenticate(creds["username"], creds["password"])

    try:
        yield session
    finally:
        session.close()


@contextlib.contextmanager
def lms_std_client(creds=None):
    """
    :param creds:  as in lms_session
    """
    with lms_session(creds) as session:
        yield session.std_client()


def attr_2_label(attr, method):
    if attr == None:
        return ""

    if attr.lower().startswith(method.lower()):
        attr = attr[len(method) :]
        attr = attr.lstrip("_")

    if attr.lower().startswith("api"):
        attr = attr[len("api") :]
        attr = attr.lstrip("_")

    if method.lower() == "get":
        attr = "read " + attr
    if method.lower() == "put":
        attr = "save " + attr
    if method.lower() == "patch":
        attr = "update " + attr
    if method.lower() == "delete":
        attr = "delete " + attr
    if method.lower() == "post":
        attr = "add " + attr
    return attr.replace("_", " ").title()


def _register_all_activities(client):
    options = client.get("/api/endpoints", unregistered=True)

    endpoints = options.main_table()

    for row in endpoints.rows:
        row.description = attr_2_label(row.act_name, row.method)

    print(f"POST api/activities registering {len(endpoints.rows)} new urls")
    client.post(
        "/api/activities",
        files={"activities": endpoints.as_http_post_file(exclusions=["method"])},
    )


def register_all_activities():
    with lms_std_client() as client:
        _register_all_activities(client)
