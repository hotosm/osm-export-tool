django_test:
	python manage.py test api.tests jobs.tests tasks.tests

test_auth:
	docker exec hotosm-export-tool-app python manage.py test ui.tests.test_auth_status -v 2

test:
	docker exec hotosm-export-tool-app pytest hdx_exports/tests/test_hdx_export_set.py

test_all:
	docker exec hotosm-export-tool-app python manage.py test api.tests jobs.tests tasks.tests ui.tests -v 2

worker:
	PYTHONPATH=../osm-export-tool-python/ DJANGO_SETTINGS_MODULE=core.settings.project dramatiq tasks.task_runners --processes 1 --threads 1