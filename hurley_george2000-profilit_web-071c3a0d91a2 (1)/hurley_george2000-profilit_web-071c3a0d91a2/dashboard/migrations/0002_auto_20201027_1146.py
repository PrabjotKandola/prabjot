# Generated by Django 3.0.8 on 2020-10-27 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profilit', '0005_delete_explorationdata'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='explorationdata',
            name='attribute',
            field=models.CharField(max_length=150),
        ),
        migrations.CreateModel(
            name='RulesBasedProfilingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.CharField(max_length=150)),
                ('file_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profilit.RulesBasedProfileFiles')),
            ],
            options={
                'verbose_name_plural': 'Exploration data in raw form',
            },
        ),
    ]