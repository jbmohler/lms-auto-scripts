import mecolm
import tools


def create_user(client, username, roles):
    payload = client.get("/api/users/list")
    current_users = payload.main_table()

    if "User" not in roles:
        roles = roles[:] + ["User"]

    if username.upper() not in [r.username for r in current_users.rows]:
        usertemplate = client.get("/api/user/new")

        usertab = usertemplate.main_table()
        user = usertab.rows[0]
        user.username = username
        user.password = "pigeon"

        roletab = usertemplate.named_table('roles:universe')
        role_selected = [r.id for r in roletab.rows if r.role_name in roles]
        for rid in role_selected:
            user.roles.toggle(rid, True)

        client.put(f"/api/user/{user.id}", files={"user": usertab.as_http_post_file()})
    else:
        user = [r for r in current_users.rows if r.username == username.upper()][0]
        payload = client.get(f"/api/user/{user.id}")
        usertab = payload.main_table()
        user = usertab.rows[0]
        roletab = payload.named_table("roles:universe")

        role_universe = [r.id for r in roletab.rows]
        role_selected = [r.id for r in roletab.rows if r.role_name in roles]

        for rid in role_selected:
            user.roles.toggle(rid, True)
        print(
            f"Assign user {user.username} to {len(user.roles.add)} roles ({', '.join(roles)})"
        )

        client.put(
            "/api/userroles/by-roles",
            files={"users": usertab.as_http_post_file(inclusions=['id', 'roles'])},
            data={"roles": ",".join(role_universe)},
        )

    payload = client.get(f"/api/user/{user.id}")
    usertab = payload.main_table()
    print(f"User: {usertab.rows[0].username}")
    userroles = payload.named_table("roles")
    roles_check = [r.role_name for r in userroles.rows]
    assert set(roles_check).issuperset(roles)
    for role in userroles.rows:
        print(role)


def outer(name, roles):
    with tools.lms_std_client() as client:
        create_user(client, name, roles)


def main():
    pass


if __name__ == "__main__":
    main()
