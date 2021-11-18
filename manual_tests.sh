docker-compose exec tests python /tests/integration_tests.py register_activities
docker-compose exec tests python /tests/integration_tests.py createrole --rolename="Contact Mgmt"
docker-compose exec tests python /tests/integration_tests.py createrole --rolename="Accounting Mgmt"
docker-compose exec tests python /tests/integration_tests.py createuser --name="Fred CFO" --roles="Accounting Mgmt"
docker-compose exec tests python /tests/integration_tests.py createuser --name="George Sales" --roles="Contact Mgmt"

# do some accounting
docker-compose exec tests python /tests/integration_tests.py trans.create_account_types
docker-compose exec tests python /tests/integration_tests.py trans.create_accounts

# do some contacts
docker-compose exec tests python /tests/integration_tests.py contacts.create_corp_entity
docker-compose exec tests python /tests/integration_tests.py contacts.create_personal_entity
