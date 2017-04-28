deploy:
	git pull
	docker pull quay.io/hotosm/osm-export-tool2
	docker-compose rm -f -v
	DOCKER_CLIENT_TIMEOUT=120 COMPOSE_HTTP_TIMEOUT=120 docker-compose -f docker-compose.production.yml up

test:
	nosetests \
	feature_selection/tests/test_feature_selection.py \
	feature_selection/tests/test_sql.py \
	hdx_exports/tests/test_hdx_export_set.py \
	utils/tests/test_manager.py \
	utils/tests/test_integration.py
