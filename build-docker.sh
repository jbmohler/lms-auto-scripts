# --build-arg CACHE_BUST=$(python -c "import uuid; print(uuid.uuid1().hex)") \
docker build \
	-t lms-demo \
	--build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" \
	--build-arg CACHE_BUST=$1 \
	-f Dockerfile.lms-debug \
	.

pushd postgresql
docker build -t pg-lms-demo .
popd

pushd tests
docker build -t lms-test-suite .
popd
