#  Copyright (c) 2023.
#

from django.db import migrations, connection


def disable_foreign_keys(apps, schema_editor):
    for table in connection.introspection.get_table_names(apps):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE '
                'WHERE REFERENCED_TABLE_NAME = %s',
                (table,)
            )
            for row in cursor:
                cursor.execute('ALTER TABLE %s DROP CONSTRAINT %s', (table, row[0]))


class Migration(migrations.Migration):
    dependencies = [
        ('your_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(disable_foreign_keys),
    ]
