# Generated by Django 3.0.8 on 2020-11-12 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20201112_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='completeness',
            field=models.DecimalField(decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='conformity',
            field=models.DecimalField(decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='total',
            field=models.DecimalField(decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='uniqueness',
            field=models.DecimalField(decimal_places=6, max_digits=8, null=True),
        ),
    ]
