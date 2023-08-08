# Generated by Django 3.1.3 on 2020-11-24 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profilit', '0008_rulesbasedprofilefiles_total_failed_data_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='completeness',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='conformity',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='uniqueness',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
    ]