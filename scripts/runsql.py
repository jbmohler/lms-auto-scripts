import argparse
import urllib.parse
import psycopg2
import psycopg2.extensions


def connect(dburl):
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

    conn = psycopg2.connect(**kwargs)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def exec_str(conn, s):
    with conn.cursor() as cursor:
        cursor.execute(s)
        # auto commit


def exec_file(conn, filename):
    sql = open(filename, "r").read()
    exec_str(conn, sql)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dburl")
    parser.add_argument("--file")
    parser.add_argument("--sql")

    args = parser.parse_args()

    conn = connect(args.dburl)

    try:
        if args.file:
            exec_file(conn, args.file)
        if args.sql:
            exec_str(conn, args.sql)
    finally:
        conn.close()
