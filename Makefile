django_test:
	python manage.py test api.tests jobs.tests tasks.tests

test:
	nosetests \
	feature_selection/tests/test_feature_selection.py \
	feature_selection/tests/test_sql.py \
	hdx_exports/tests/test_hdx_export_set.py \
	utils/tests/test_utils.py \
	utils/tests/test_integration.py
