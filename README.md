# Introduction

Docker compose scripts for full lms Data Suite.

This is not a mono-repo which makes this just a wrapper repo for the actual
sub-projects.  See `git-clone-subs.sh` and `git-status-subs.sh`.

The docker compose configuration in the root starts 3 docker containers:

- An lms server with contact/password management and accounting.
- A postgresql server
- A container for running test scripts.

# WARNING

The passwords in docker-compose.yml should be changed if being used as a
template for production usage.

# Keys

Generate keys as follows for the LMS_CONTACT_KEY and YENOT_AUTH_SIGNING_SECRET
environment variables.

```console
$ docker run --rm -it python /bin/bash
# pip install --upgrade pip
# pip install cryptography
# python -c "import cryptography.fernet; print(f'LMS_CONTACTS_KEY={cryptography.fernet.Fernet.generate_key().decode()}')"
# python -c "import secrets; print(f'YENOT_AUTH_SIGNING_SECRET={secrets.token_urlsafe(32)}')"
```

# Usage

```console
$ sh git-clone-subs.sh
... various git clones of yenot-x ...
$ bash build-docker.sh
... builds a docker image based on the yenot-x clones ...
$ docker rm lms-auto-scripts_db_1 && docker-compose up
$ docker-compose exec -e PG_INIT_DB=postgresql://postgres:abc123@db/postgres -e LMS_ADMIN_DB=postgresql://lmsadmin:very-secret-123@db/lmsdemo -e INIT_DB_PASSWORD=zyx987 web bash /lms/init-database.sh
... creates a new DB & populates schema elements & base data ...
$ docker-compose up --detach
$ bash manual_tests.sh
... test output ...
```
