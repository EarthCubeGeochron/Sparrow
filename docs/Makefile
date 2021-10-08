build:
	cd .. && docs/.ci/1-build-images

push:
	cd .. && ./docs/.ci/3-push-images

staging: build
	docker run -p 3000:3000 ghcr.io/earthcubegeochron/sparrow/documentation-site:latest