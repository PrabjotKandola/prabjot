# Generated by Django 3.0.8 on 2020-10-15 17:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import profilit.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UnmatchedFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=profilit.models.user_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Data Unmatched Outputs',
            },
        ),
        migrations.CreateModel(
            name='TransformedFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=500, upload_to=profilit.models.user_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Transform Outputs',
            },
        ),
        migrations.CreateModel(
            name='RulesBasedProfileFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=profilit.models.user_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Rules Based Outputs',
            },
        ),
        migrations.CreateModel(
            name='MatchFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=profilit.models.user_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Data Match Outputs',
            },
        ),
        migrations.CreateModel(
            name='ExplorationFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=500, upload_to=profilit.models.user_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Exploration Outputs',
            },
        ),
        migrations.CreateModel(
            name='ExplorationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.CharField(max_length=150)),
                ('min_length', models.IntegerField()),
                ('max_length', models.IntegerField()),
                ('min_value', models.DecimalField(decimal_places=6, max_digits=10, null=True)),
                ('max_value', models.DecimalField(decimal_places=6, max_digits=10, null=True)),
                ('completeness', models.DecimalField(decimal_places=6, max_digits=10)),
                ('non_null_count', models.IntegerField()),
                ('uniqueness', models.DecimalField(decimal_places=6, max_digits=10)),
                ('unique_value_count', models.IntegerField()),
                ('common_values', models.CharField(max_length=500)),
                ('numeric_percentage', models.DecimalField(decimal_places=6, max_digits=10)),
                ('date_percentage', models.DecimalField(decimal_places=6, max_digits=10)),
                ('file_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profilit.ExplorationFiles')),
            ],
            options={
                'verbose_name_plural': 'Exploration data in raw form',
            },
        ),
        migrations.CreateModel(
            name='DataFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(choices=[('df', 'Data file'), ('rt', 'Rules Template'), ('tt', 'Transformation Template'), ('mt', 'Match template')], max_length=30)),
                ('file_format', models.CharField(choices=[('csv', 'CSV'), ('ex', 'Excel'), ('tx', 'TXT')], max_length=4)),
                ('file', models.FileField(upload_to=profilit.models.user_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv', 'txt', 'xlsx'])])),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Data Files',
            },
        ),
    ]