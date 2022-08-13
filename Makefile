dev:
	docker build --rm -f Dockerfile -t jb_hugo:latest .
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest

deploy-prod:
	docker build -t jb-jbcom .
	docker-compose -f ~/docker-compose.yml up -d jb-jbcom
	docker image prune -af