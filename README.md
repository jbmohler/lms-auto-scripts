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

# Usage

```console
$ sh git-clone-subs.sh
... various git clones of yenot-x ...
$ bash build-docker.sh
... builds a docker image based on the yenot-x clones ...
$ docker rm lms-auto-scripts_db_1 && docker-compose up
$ docker-compose up --detach
$ sh manual_tests.sh
... test output ...
```
