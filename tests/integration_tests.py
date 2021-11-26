import os
import argparse
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


def sleep():
    import time

    while True:
        time.sleep(4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="lms Integration Test Suite")
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    subparsers.add_parser("sleep")
    a = subparsers.add_parser("createrole")
    a.add_argument("--rolename", "-r")

    b = subparsers.add_parser("register_activities")

    c = subparsers.add_parser("createuser")
    c.add_argument("--name", "-n")
    c.add_argument("--roles", "-r", help="comma delimited role name list")

    c = subparsers.add_parser("trans.create_account_types")
    c = subparsers.add_parser("trans.create_accounts")
    c = subparsers.add_parser("trans.create_initial_balances")
    c = subparsers.add_parser("trans.create_biweekly_paycheck")
    c = subparsers.add_parser("trans.create_weekly_groceries")
    c = subparsers.add_parser("trans.create_monthly_mortgage")
    c = subparsers.add_parser("trans.create_random_automotive")
    c = subparsers.add_parser("contacts.create_corp_entity")
    c = subparsers.add_parser("contacts.create_personal_entity")
    c = subparsers.add_parser("contacts.add_random_contact_bits")

    args = parser.parse_args()

    if args.command == "sleep":
        sleep()
    elif args.command == "register_activities":
        import tools

        tools.register_all_activities()
    elif args.command == "createrole":
        import create_role

        create_role.outer(args.rolename)
    elif args.command == "createuser":
        import create_users

        create_users.outer(args.name, args.roles.split(","))
    elif args.command.startswith("trans."):
        import create_accounting

        create_accounting.outer(
            getattr(create_accounting, args.command[len("trans.") :])
        )
    elif args.command.startswith("contacts."):
        import create_contacts

        create_contacts.outer(
            getattr(create_contacts, args.command[len("contacts.") :])
        )
    else:
        main()
