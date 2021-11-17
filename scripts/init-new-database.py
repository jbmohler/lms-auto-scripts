import argparse
import urllib.parse
import psycopg2
import psycopg2.errors
import psycopg2.extensions

CREATE_USERS = """
-- create lms generic user roles
CREATE ROLE {lmsadmin};
ALTER ROLE {lmsadmin}
    WITH INHERIT NOCREATEROLE 
    LOGIN PASSWORD '{lmsadmin_password}';
CREATE ROLE {lmsserver};
ALTER ROLE {lmsserver}
    WITH INHERIT NOCREATEROLE NOCREATEDB
    LOGIN PASSWORD '{lmsserver_password}';
"""

DIGITAL_OCEAN_NOSU_WORKAROUND = """
GRANT {lmsadmin} to {pgsu};
"""

CREATE_DB = """
CREATE DATABASE {lmsdbname} OWNER {lmsadmin};
"""

PREP_DATABASE = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

ALTER DEFAULT PRIVILEGES FOR ROLE {lmsadmin}
    GRANT USAGE ON SCHEMAS TO {lmsserver};
ALTER DEFAULT PRIVILEGES FOR ROLE {lmsadmin}
    GRANT SELECT,INSERT,UPDATE,DELETE ON TABLES TO {lmsserver};
ALTER DEFAULT PRIVILEGES FOR ROLE {lmsadmin}
    GRANT EXECUTE ON FUNCTIONS TO {lmsserver};
ALTER DEFAULT PRIVILEGES FOR ROLE {lmsadmin}
    GRANT SELECT,UPDATE,USAGE ON SEQUENCES TO {lmsserver};
"""


def connect_args(dburl):
    result = urllib.parse.urlsplit(dburl)

    kwargs = {"dbname": result.path[1:]}
    if result.hostname != None:
        kwargs["host"] = result.hostname
    if result.port != None:
        kwargs["port"] = result.port
    if result.username != None:
        kwargs["user"] = result.username
    if result.password != None:
        kwargs["password"] = result.password

    return kwargs


def exec_str(conn, s):
    with conn.cursor() as cursor:
        cursor.execute(s)
        # auto commit


def main(args):
    sucfg = connect_args(args.pg_superuser)
    admcfg = connect_args(args.lms_admin)
    srvcfg = connect_args(args.lms_server)

    configs = [sucfg, admcfg, srvcfg]

    if len(set((c["host"], c["port"]) for c in configs)) != 1:
        raise RuntimeError("All 3 connect strings must point to the same server")

    if len(set(c["user"] for c in configs)) != 3:
        raise RuntimeError("All the usernames must be different")

    if sucfg["dbname"] == admcfg["dbname"] or admcfg["dbname"] != srvcfg["dbname"]:
        raise RuntimeError(
            "PG superuser must be default postgres & the 2 LMS connect string must be the same"
        )

    config = {
        "pgsu": sucfg["user"],
        "lmsadmin": admcfg["user"],
        "lmsserver": srvcfg["user"],
        "lmsadmin_password": admcfg["password"],
        "lmsserver_password": srvcfg["password"],
        "lmsdbname": srvcfg["dbname"],
    }

    conn = psycopg2.connect(**sucfg)
    try:
        print(f"Creating users {config['lmsadmin']} and {config['lmsserver']}")

        try:
            exec_str(conn, CREATE_USERS.format(**config))
        except psycopg2.errors.DuplicateObject:
            print("Skipped -- Users already created")
        if sucfg["user"] == "doadmin":
            # This is stinky, but digital ocean does not expose a super-user
            print(f"Making doadmin fake SU a {config['lmsadmin']}")
            exec_str(conn, DIGITAL_OCEAN_NOSU_WORKAROUND.format(**config))
        conn.commit()
    finally:
        conn.close()

    # connect to the SU dtabase with the lms admin user
    conn = psycopg2.connect(**sucfg)
    try:
        conn.autocommit = True
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        print(f"Creating database {config['lmsdbname']}")
        exec_str(conn, CREATE_DB.format(**config))
    finally:
        conn.close()

    conn = psycopg2.connect(**admcfg)
    try:
        print(f"Preparing database defaults {config['lmsdbname']}")
        exec_str(conn, PREP_DATABASE.format(**config))
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pg-superuser")
    parser.add_argument("--lms-admin")
    parser.add_argument("--lms-server")

    main(parser.parse_args())
