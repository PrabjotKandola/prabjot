# Generated by Django 3.1.3 on 2020-11-25 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_auto_20201125_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='completeness',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='Completeness (%)'),
        ),
    ]
