import os
import codecs
import tools

INIT_ADMIN_USER = os.getenv("INIT_ADMIN_USER")
INIT_ADMIN_PASSWORD = os.getenv("INIT_ADMIN_PASSWORD")


def login_logout():
    with tools.lms_session(creds={}) as session:
        try:
            session.std_client().get("api/user/me")
        except tools.ytclient.RtxError as e:
            print(f"Not yet authenticated; good ({str(e)})")

        try:
            session.authenticate(INIT_ADMIN_USER, "incorrect password")
        except tools.ytclient.RtxError as e:
            print(f"Auth failed due to incorrect password; good ({str(e)})")

        session.authenticate(INIT_ADMIN_USER, INIT_ADMIN_PASSWORD)

        try:
            payload = session.std_client().get("api/user/me")
            username = payload.main_table().rows[0].username
            print(f"Authenticated; got payload for user {username}")
        except tools.ytclient.RtxError as e:
            print(f"Did not get user payload; bad ({str(e)})")

        session.logout()

        try:
            session.std_client().get("api/user/me")
        except tools.ytclient.RtxError as e:
            print(f"Logout succeeded - no longer authenticated; good ({str(e)})")


def try_2fa():
    with tools.lms_session(creds={}) as session:
        session.authenticate_pin1("user2 x", "1928")

        try:
            session.std_client().get("api/user/me")
        except tools.ytclient.RtxError as e:
            print(f"Not yet authenticated; good ({str(e)})")

        seg = codecs.encode(session.yenot_sid.encode("ascii"), "hex").decode("ascii")
        fname = os.path.join(os.environ["YENOT_2FA_DIR"], "authpin-{}".format(seg))
        pin2 = open(fname, "r").read()
        session.authenticate_pin2(pin2)

        try:
            payload = session.std_client().get("api/user/me")
            print("got me")
            print(payload.main_table().rows)
        except Exception:
            raise


def sleep():
    with tools.lms_session(creds={}) as session:
        session.std_client().get("/api/request/sleep", duration=3)


def outer(f):
    f()
    # creds = {"username": "fred cfo", "password": "pigeon"}
    # with tools.lms_std_client(creds) as client:
    #    f(client)


def main():
    pass


if __name__ == "__main__":
    main()
