deploy:
	docker pull quay.io/hotosm/osm-export-tool2
	docker-compose rm -f -v
	DOCKER_CLIENT_TIMEOUT=120 COMPOSE_HTTP_TIMEOUT=120 docker-compose -f docker-compose.production.yml up
