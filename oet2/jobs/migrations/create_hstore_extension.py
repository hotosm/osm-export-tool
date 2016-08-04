from django.contrib.postgres.operations import HStoreExtension
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        HStoreExtension(),
    ]
