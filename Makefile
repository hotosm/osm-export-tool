django_test:
	python manage.py test api.tests jobs.tests tasks.tests



worker:
	PYTHONPATH=../osm-export-tool-python/ DJANGO_SETTINGS_MODULE=core.settings.project dramatiq tasks.task_runners --processes 1 --threads 1