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

        for _ in range(3):
            try:
                payload = session.std_client().get("api/user/me")
                username = payload.main_table().rows[0].username
                sesslist = payload.named_table("sessions").rows
                sesslist.sort(key=lambda x: (1 if x.inactive else 2, x.issued))
                for row in sesslist:
                    print(f"\t{row.inactive}\t{row.id[9:13]} {row.ipaddress} {row.issued:%x %X} {row.expires:%x %X}")
                print(f"Authenticated; got payload for user {username}")
            except tools.ytclient.RtxError as e:
                print(f"Did not get user payload; bad ({str(e)})")
            import time; time.sleep(1)

        session.logout()

        try:
            session.std_client().get("api/user/me")
        except tools.ytclient.RtxError as e:
            print(f"Logout succeeded - no longer authenticated; good ({str(e)})")


def activate_2fa():
    creds = {"username": "admin", "password": "zyx987"}
    with tools.lms_std_client(creds) as client:
        payload = client.get("api/roles/list")
        roles = payload.main_table()

        user = [r for r in roles.rows if r.role_name == 'User'][0]

        payload = client.get("api/activities/by-role", role=user.id)
        activities = payload.main_table()

        for r in activities.rows:
            print(r)

    creds = {"username": "fred cfo", "password": "pigeon"}
    try:
        with tools.lms_std_client(creds) as client:
            payload = client.get("api/user/me")
            userid = payload.main_table().rows[0].id

            payload = client.get("api/user/me/address/new")

            addresses = payload.main_table()
            row = addresses.rows[0]
            row.addr_type = "phone"
            row.address = "717-123-1234"
            row.is_2fa_target = True
            addrid = row.id

            client.put("api/user/me/address/{}", row.id, tables={"address": addresses})

            # mark this new user address as verified
            fname = os.path.join(os.environ["YENOT_2FA_DIR"], f"addrverify--{userid}--{addrid}")
            pin6 = open(fname, "r").read()
            client.put("api/user/me/address/{}/verify", addrid, confirmation=pin6)
    except tools.ytclient.RtxError as e:
        print(e)
        print(f"probably being run the second time")

    with tools.lms_std_client(creds) as client:
        try:
            client.get("api/user/me")
        except tools.ytclient.RtxError as e:
            print(f"Not yet authenticated as client; good ({str(e)})")

    with tools.lms_session(creds={}) as session:
        session.authenticate(**creds)

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
