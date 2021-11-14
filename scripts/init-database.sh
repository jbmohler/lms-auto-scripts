#!/bin/sh

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
