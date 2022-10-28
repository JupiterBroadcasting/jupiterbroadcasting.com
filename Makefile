help:
		@echo "Jupiter Broadcasting Hugo Project"
		@echo 
		@echo "Help for using this Makefile"
		@echo
		@echo "For detailed help about this project please visit:"
		@echo "https://github.com/JupiterBroadcasting/jupiterbroadcasting.com"
		@echo
		@echo "------------------------------------------------------------------"
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m - %s\n", $$1, $$2}'
 
dev-build: ## Generate the development docker container
	docker build --rm -f Dockerfile.dev -t qgis_hugo_dev:latest .

dev: dev-build ## Run the development hugo container
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 qgis_hugo_dev:latest

dev-metrics: dev-build ## Run the development hugo container with metrics
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 qgis_hugo_dev:latest serve -D --bind 0.0.0.0 --templateMetrics --templateMetricsHints

deploy-prod: ## Deploy everything to production
	docker build -t qgis.org .
	docker-compose -f ~/docker-compose.yml up -d qgis_hugo_prod
	docker image prune -af

tests: ## Run the test suite
	docker build --rm -f Dockerfile.tests -t jb_tests:latest .
	docker run --rm --net=host --user 1000:1000 --volume "$${PWD}":/app -w /app jb_tests:latest
