#!/bin/sh

if [ ! -z "$LMS_ADMIN_DB" ]; then
	sleep 5

	# Req'd env vars:
	# LMS_ADMIN_DB, PG_INIT_DB, LMS_DB_NAME, LMS_PG_ADMIN, INIT_DB_PASSWORD

	if [ ! -z "$PG_INIT_DB" ]; then
		python /lms/runsql.py $PG_INIT_DB --file /lms/create-users.sql
		python /lms/runsql.py $PG_INIT_DB --sql "CREATE DATABASE $LMS_DB_NAME OWNER $LMS_PG_ADMIN"
	fi
	python /lms/runsql.py $LMS_ADMIN_DB --file /lms/prepare-database.sql
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
