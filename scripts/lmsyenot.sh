#!/bin/sh

set -e

if [ ! -z "$LMS_ADMIN_DB" ]; then
	# Req'd connection string env vars:
	# * PG_INIT_DB: postgres superuser connection string to default db
	# * LMS_ADMIN_DB: lms administrative connection string
	# * LMS_PROD_DB: lms lowered privilege server connection string

	# TODO iterate in init-new-database.py to await server coming up
	sleep 3

	python /lms/init-new-database.py \
		--pg-superuser=$PG_INIT_DB \
		--lms-admin=$LMS_ADMIN_DB \
		--lms-server=$LMS_PROD_DB

	echo "User password of " $INIT_DB_PASSWORD
	. /lms/init-database.sh
fi

YENOT_HOST=0.0.0.0 YENOT_PORT=8088 python /lms/yenot/scripts/yenotserve.py \
	--module=yenotauth.server \
	--module=lhserver \
	--module=lcserver \
	--module=bitserver \
	--module=yenothtml \
	$LMS_PROD_DB
