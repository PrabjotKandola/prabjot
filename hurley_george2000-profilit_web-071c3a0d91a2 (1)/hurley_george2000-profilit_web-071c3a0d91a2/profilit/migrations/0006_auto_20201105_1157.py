# Generated by Django 3.0.8 on 2020-11-05 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profilit', '0005_delete_explorationdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='total_failed_entries',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='total_failed_records',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='total_profile',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rulesbasedprofilefiles',
            name='total_records',
            field=models.IntegerField(null=True),
        ),
    ]