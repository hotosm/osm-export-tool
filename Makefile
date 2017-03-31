deploy:
	docker pull quay.io/hotosm/osm-export-tool2
	docker-compose rm -f -v
	docker-compose -f docker-compose.production.yml up
