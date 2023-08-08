# Generated by Django 3.0.8 on 2020-10-19 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profilit', '0003_auto_20201019_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='explorationdata',
            name='attribute',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='common_values',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='date_percentage',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='numeric_percentage',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='explorationdata',
            name='uniqueness',
            field=models.DecimalField(decimal_places=6, max_digits=20, null=True),
        ),
    ]