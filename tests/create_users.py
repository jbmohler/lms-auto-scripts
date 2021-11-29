import mecolm
import tools


def create_user(client, username, roles):
    payload = client.get("/api/users/list")
    current_users = payload.main_table()

    if username.upper() not in [r.username for r in current_users.rows]:
        usertemplate = client.get("/api/user/new")

        usertab = usertemplate.main_table()
        user = usertab.rows[0]
        user.username = username
        user.password = "pigeon"
        user.pin = "1928"
        user.target_2fa = {"file": None}

        client.put(f"/api/user/{user.id}", files={"user": usertab.as_http_post_file()})
    else:
        user = [r for r in current_users.rows if r.username == username.upper()][0]

    if "User" not in roles:
        roles = roles[:] + ["User"]

    options = client.get("/api/roles/list")
    roletab = options.main_table()
    role_universe = [r.id for r in roletab.rows]
    role_selected = [r.id for r in roletab.rows if r.role_name in roles]

    links = mecolm.simple_table(["id", "role_list"])
    with links.adding_row() as r2:
        r2.id = user.id
        r2.role_list = role_selected
        print(
            f"Assign user {user.username} to {len(r2.role_list)} roles ({', '.join(roles)})"
        )

    client.put(
        "/api/userroles/by-roles",
        files={"userroles": links.as_http_post_file()},
        data={"roles": ",".join(role_universe)},
    )

    payload = client.get(f"/api/user/{user.id}")
    usertab = payload.main_table()
    print(f"User: {usertab.rows[0].username}")
    for role in payload.named_table("roles").rows:
        print(role)


def outer(name, roles):
    with tools.lms_std_client() as client:
        create_user(client, name, roles)


def main():
    pass


if __name__ == "__main__":
    main()
