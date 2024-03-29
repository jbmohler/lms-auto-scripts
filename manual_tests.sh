#!/bin/bash

set -ex

if [ x"$1" == "xinit" ]; then
	docker-compose exec \
		admin bash /lms/init-database.sh
fi

docker-compose exec tests python /tests/integration_tests.py register_activities
docker-compose exec tests python /tests/integration_tests.py createrole --rolename="Contact Mgmt"
docker-compose exec tests python /tests/integration_tests.py createrole --rolename="Accounting Mgmt"
docker-compose exec tests python /tests/integration_tests.py createuser --name="Fred CFO" --roles="Accounting Mgmt"
docker-compose exec tests python /tests/integration_tests.py createuser --name="George Sales" --roles="Contact Mgmt"
docker-compose exec tests python /tests/integration_tests.py createuser --name="User2 X" --roles="User" --2fa=file
docker-compose exec tests python /tests/integration_tests.py createuser --name="M Owner" --roles="User,Accounting Mgmt,Contact Mgmt" --2fa=file

# create new auditor role
docker-compose exec tests python /tests/integration_tests.py createrole --rolename="Auditor"

# do some 2fa and login tests
docker-compose exec tests python /tests/integration_tests.py login.login_logout
#docker-compose exec tests python /tests/integration_tests.py login.activate_2fa
#docker-compose exec tests python /tests/integration_tests.py login.try_2fa
docker-compose exec tests python /tests/integration_tests.py login.sleep

# do some accounting
docker-compose exec tests python /tests/integration_tests.py trans.create_account_types
docker-compose exec tests python /tests/integration_tests.py trans.create_accounts
docker-compose exec tests python /tests/integration_tests.py trans.create_initial_balances
docker-compose exec tests python /tests/integration_tests.py trans.create_biweekly_paycheck
docker-compose exec tests python /tests/integration_tests.py trans.create_weekly_groceries
docker-compose exec tests python /tests/integration_tests.py trans.create_monthly_mortgage
docker-compose exec tests python /tests/integration_tests.py trans.create_random_automotive
#
# do some contacts
docker-compose exec tests python /tests/integration_tests.py contacts.create_corp_entity
docker-compose exec tests python /tests/integration_tests.py contacts.create_personal_entity
docker-compose exec tests python /tests/integration_tests.py contacts.add_random_contact_bits

# TODO -- do some load testing


# NOTES
#
# - each handler should require a "request" parameter
# - app decorators (get, put, post, patch, delete)
# - consider custom protocol in sanic
