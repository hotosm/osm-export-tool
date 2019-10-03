django_test:
	python manage.py test api.tests jobs.tests tasks.tests

test:
	nosetests hdx_exports/tests/test_hdx_export_set.py
