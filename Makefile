baseimage:
	docker build -t quay.io/hotosm/osm-export-tool2-omimimage -f ops/omim_image/Dockerfile .
	docker build -t quay.io/hotosm/osm-export-tool2-baseimage -f ops/base_image/Dockerfile .

django_test:
	python manage.py test api.tests jobs.tests tasks.tests

test:
	nosetests \
	feature_selection/tests/test_feature_selection.py \
	feature_selection/tests/test_sql.py \
	hdx_exports/tests/test_hdx_export_set.py \
	utils/tests/test_manager.py \
	utils/tests/test_integration.py
