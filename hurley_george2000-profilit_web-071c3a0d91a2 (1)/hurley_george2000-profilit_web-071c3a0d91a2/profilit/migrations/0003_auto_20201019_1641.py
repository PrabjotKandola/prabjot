# Generated by Django 3.0.8 on 2020-10-19 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profilit', '0002_auto_20201019_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='explorationdata',
            name='max_length',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='min_length',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='non_null_count',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='unique_value_count',
            field=models.IntegerField(null=True),
        ),
    ]
