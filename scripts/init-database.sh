#!/bin/sh

# Req'd connection string env vars:
# * PG_INIT_DB: postgres superuser connection string to default db
# * LMS_ADMIN_DB: lms administrative connection string
# * LMS_PROD_DB: lms lowered privilege server connection string
# * INIT_DB_PASSWORD: Password of Admin LMS User

python /lms/init-new-database.py \
	--pg-superuser=$PG_INIT_DB \
	--lms-admin=$LMS_ADMIN_DB \
	--lms-server=$LMS_PROD_DB

echo "Creating 'admin' user with  password " $INIT_DB_PASSWORD
python /lms/yenot/scripts/init-database.py \
	--ddl-script=/lms/yenot-auth/schema/authentication.sql \
	--ddl-script=/lms/yenot-lmshacc/schema/lmshacc.sql \
	--ddl-script=/lms/yenot-lmscontacts/schema/contacts.sql \
	--ddl-script=/lms/yenot-lmsdatabits/schema/databits.sql \
	--module=lhserver \
	--module=lcserver \
	--module=bitserver \
	--module=yenotauth.server \
	--user=admin \
	$LMS_ADMIN_DB
