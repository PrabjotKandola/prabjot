# Generated by Django 3.1.3 on 2020-11-25 12:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20201116_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='attribute_failed',
            field=models.CharField(max_length=500, verbose_name='Attribute'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='completeness',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='Completeness (%)'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='conformity',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='Conformity (%)'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='total',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='Total (%)'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='total_errors',
            field=models.IntegerField(null=True, verbose_name='Total Errors'),
        ),
        migrations.AlterField(
            model_name='rulesbasedprofilingdata',
            name='uniqueness',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='Uniqueness (%)'),
        ),
    ]
