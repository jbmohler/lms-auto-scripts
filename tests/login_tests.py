import os
import codecs
import tools


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


def outer(f):
    f()
    # creds = {"username": "fred cfo", "password": "pigeon"}
    # with tools.lms_std_client(creds) as client:
    #    f(client)


def main():
    pass


if __name__ == "__main__":
    main()
