import re
import tools
import mecolm


def create_role(client, rolename, endpoints):
    options = client.get("/api/roles/list")

    roletab = options.main_table()
    if rolename not in [r.role_name for r in roletab.rows]:
        # the role by this name does not exist, create it
        roletemplate = client.get("/api/role/new")

        roletab = roletemplate.named_table("role")
        row = roletab.rows[0]
        row.role_name = rolename

        client.put(f"/api/role/{row.id}", files={"role": roletab.as_http_post_file()})
        print(f"Created role {row.role_name}")
    else:
        row = [r for r in roletab.rows if r.role_name == rolename][0]

    options = client.get("/api/activities/list")
    acttab = options.main_table()

    def matches(ep):
        for regexp in endpoints:
            if re.match(regexp, ep.url):
                return True
        return False

    links = mecolm.simple_table(["id", "permissions"])
    for endpoint in acttab.rows:
        if matches(endpoint):
            with links.adding_row() as r2:
                r2.id = endpoint.id
                r2.permissions = [{"roleid": row.id, "permitted": True}]

    print(f"PUT roleactivities/by-roles with {len(links.rows)} rows")
    client.put(
        "/api/roleactivities/by-roles",
        files={"roleactivities": links.as_http_post_file()},
        data={"roles": row.id},
    )

    payload = client.get(f"/api/role/{row.id}")
    roletab = payload.main_table()
    print(f"User: {roletab.rows[0].role_name}")
    payload = client.get("/api/activities/by-role", role=row.id)
    for activity in payload.main_table().rows:
        print(activity)


def setup_auditor_role(client, rolename):
    payload = client.get("/api/roles/list")
    roles = payload.main_table()
    payload = client.get("/api/users/list")
    users = payload.main_table()

    def find(table, column, value):
        return [row for row in table.rows if getattr(row, column) == value][0]

    accounting = find(roles, "role_name", "Accounting Mgmt")
    contacts = find(roles, "role_name", "Contact Mgmt")
    auditor = find(roles, "role_name", rolename)
    user2 = find(users, "username", "USER2 X")

    payload = client.get("/api/userroles/by-users", users=user2.id)
    role_matrix = payload.main_table()

    save = role_matrix.duplicate(
        rows=[row for row in role_matrix.rows if row.role_name == rolename]
    )

    for row in save.rows:
        row.users.toggle(user2.id, True)

    client.put("/api/userroles/by-users", users=user2.id, tables={"roles": save})


def outer(rolename):
    matches = []
    if rolename == "Contact Mgmt":
        matches = ["api/persona.*"]
    if rolename == "Accounting Mgmt":
        matches = [
            "api/account.*",
            "api/journal.*",
            "api/transaction.*",
            "api/gledger.*",
            "api/static_settings",
        ]

    with tools.lms_std_client() as client:
        create_role(client, rolename, matches)

        if rolename == "Auditor":
            # set up user User2 X as auditor and set auditor to have lots of read-only roles
            setup_auditor_role(client, rolename)


def main():
    with tools.lms_std_client() as client:
        create_role(client, "Contact Mgmt", ["api/persona.*"])


if __name__ == "__main__":
    main()
