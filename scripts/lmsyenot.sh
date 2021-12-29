#!/bin/sh

set -e

YENOT_HOST=0.0.0.0 YENOT_PORT=8088 python /lms/yenot/scripts/yenotserve.py \
	--module=yenot.server.contrib.monitor \
	--module=yenot.server.contrib.pgserver \
	--module=yenot.server.contrib.proxytest \
	--module=yenotauth.server \
	--module=yenot.server.tests \
	--module=lhserver \
	--module=lcserver \
	--module=bitserver \
	--module=yenothtml \
	$LMS_PROD_DB
