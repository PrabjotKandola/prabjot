from django.db import models
from profilit.models import ExplorationFiles, RulesBasedProfileFiles, MatchFiles, UnmatchedFiles
from django.contrib.auth.models import User
from django.utils import timezone


class ExplorationData(models.Model):
    # Table configuration
    attribute = models.CharField(max_length=150)
    min_length = models.IntegerField(null=True)
    max_length = models.IntegerField(null=True)
    min_value = models.DecimalField(null=True, max_digits=32, decimal_places=16)
    max_value = models.DecimalField(null=True, max_digits=32, decimal_places=16)
    completeness = models.DecimalField(verbose_name='Completeness (%)',
                                       null=True, max_digits=6, decimal_places=3
                                       )
    non_null_count = models.IntegerField(verbose_name='Non-null count', null=True)
    uniqueness = models.DecimalField(
        verbose_name='Uniqueness (%)',
        null=True, max_digits=6, decimal_places=3
    )
    unique_value_count = models.IntegerField(null=True)
    common_values = models.CharField(null=True, max_length=500)
    numeric_percentage = models.DecimalField(
        verbose_name='Numeric percentage (%)',
        null=True, max_digits=6, decimal_places=3
    )
    date_percentage = models.DecimalField(
        verbose_name='Numeric percentage (%)',
        null=True, max_digits=6, decimal_places=3
    )
    file_set = models.ForeignKey(ExplorationFiles, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Exploration data in raw form"

    def __str__(self):
        return f'Exploration data in raw form created at {self.file_set.date_created}' \
               f' by {self.file_set.person.username}'


class RulesBasedProfilingData(models.Model):
    # Table configuration
    attribute_failed = models.CharField(max_length=500, verbose_name='Attribute')
    completeness = models.DecimalField(null=True, verbose_name='Completeness (%)', max_digits=6, decimal_places=3)
    uniqueness = models.DecimalField(null=True, verbose_name='Uniqueness (%)', max_digits=6, decimal_places=3)
    conformity = models.DecimalField(null=True, verbose_name='Conformity (%)', max_digits=6, decimal_places=3)
    total = models.DecimalField(null=True, verbose_name='Total (%)', max_digits=6, decimal_places=3)
    total_errors = models.IntegerField(null=True, verbose_name='Total Errors')
    date_created = models.DateTimeField(default=timezone.now, verbose_name='Date Created')
    file_set = models.ForeignKey(RulesBasedProfileFiles, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Exploration data in raw form"

    def __str__(self):
        return f'Exploration data in raw form created at {self.file_set.date_created}' \
               f' by {self.file_set.person.username}'


class RuleTemplateErrors(models.Model):
    rule_id = models.CharField(max_length=100)
    error_message = models.CharField(max_length=500)
    person = models.ForeignKey(User, on_delete=models.CASCADE)


class MetricWeighting(models.Model):
    completeness = models.IntegerField(default=1)
    uniqueness = models.IntegerField(default=1)
    conformity = models.IntegerField(default=1)
    person = models.OneToOneField(User, on_delete=models.CASCADE)


class MatchingData(models.Model):
    data_file_a_total = models.IntegerField(null=True)
    data_file_b_total = models.IntegerField(null=True)
    match_count = models.IntegerField(null=True)
    data_count = models.IntegerField(null=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Matching data in raw form created at {self.file_set.date_created}' \
               f' by {self.file_set.person.username}'
    def name(self):
        return 'Matching_data_'+str(self.date_created.strftime('%Y-%m-%d_%H-%M-%S'))




