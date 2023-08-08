from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os
from django.core.validators import FileExtensionValidator


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'data_files/user_{instance.person.id}/{filename}'


class DataFiles(models.Model):
    # Choices
    file_type_names = [('df', 'Data file'), ('rt', 'Rules Template'),
                       ('tt', 'Transformation Template'), ('mt', 'Match template')]
    file_format_names = [('csv', 'CSV'), ('ex', 'Excel'), ('tx', 'TXT')]
    # Table configuration
    file_type = models.CharField(max_length=30, choices=file_type_names)
    file_format = models.CharField(max_length=4, choices=file_format_names)
    file = models.FileField(upload_to=user_directory_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt', 'xlsx'])])
    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Data Files"

    def __str__(self):
        return self.file.name

    def filename(self):
        return os.path.basename(self.file.name)


class ExplorationFiles(models.Model):
    # Table configuration
    file = models.FileField(upload_to=user_directory_path, max_length=500)
    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Exploration Outputs"

    def __str__(self):
        return f'{self.person.username} Exploration Output'

    def filename(self):
        return os.path.basename(self.file.name)

#
# class TestModel(models.Model):
#     test_num = models.IntegerField()
#     something_else = models.IntegerField()
#     # test_foreign = models.OneToOneField(ExplorationFiles, on_delete=models.CASCADE)
#     something_linking = models.ForeignKey(ExplorationFiles, on_delete=models.CASCADE)
#
#     class Meta:
#         verbose_name_plural = "This is testing SQL injection"
#
#     # def __str__(self):
#     #     return f'SQL test created at {self.test_foreign.date_created}' \
#     #            f' by {self.test_foreign.person.username}'


class RulesBasedProfileFiles(models.Model):
    # Table configuration
    file = models.FileField(upload_to=user_directory_path)
    total_records = models.IntegerField(null=True)  # number of records in the dataset
    total_data_points = models.IntegerField(null=True)  # number of data points in the dataset
    total_profile = models.IntegerField(null=True)  # number of possible errors
    total_errors = models.IntegerField(null=True)  # number of errors
    total_failed_data_points = models.IntegerField(null=True)  # number of failed data points
    total_failed_records = models.IntegerField(null=True)  # number of failed data records

    completeness = models.DecimalField(null=True, max_digits=20, decimal_places=6)
    uniqueness = models.DecimalField(null=True, max_digits=20, decimal_places=6)
    conformity = models.DecimalField(null=True, max_digits=20, decimal_places=6)

    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Rules Based Outputs"

    def __str__(self):
        return f'{self.person.username} rules output {self.date_created}'

    def filename(self):
        return os.path.basename(self.file.name)


class TransformedFiles(models.Model):
    # Table configuration
    file = models.FileField(upload_to=user_directory_path, max_length=500)
    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Transform Outputs"

    def __str__(self):
        return f'{self.person.username} transform output {self.date_created}'

    def filename(self):
        return os.path.basename(self.file.name)


# class MatchFiles(models.Model):
#     # Table configuration
#     matched_file = models.FileField(upload_to=user_directory_path)
#     unmatched_file = models.FileField(upload_to=user_directory_path)
#     match_count = models.IntegerField()
#     total_count = models.IntegerField()
#     date_created = models.DateTimeField(default=timezone.now)
#     person = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     class Meta:
#         verbose_name_plural = "Data Match Outputs"
#
#     def __str__(self):
#         return f'{self.person.username} match output {self.date_created}'
#
#     def match_filename(self):
#         return os.path.basename(self.matched_file.name)
#
#     def unmatched_filename(self):
#         return os.path.basename(self.unmatched_file.name)

class MatchFiles(models.Model):
    # Table configuration
    file = models.FileField(upload_to=user_directory_path)
    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Data Match Outputs"

    def __str__(self):
        return f'{self.person.username} match output {self.date_created}'

    def filename(self):
        return os.path.basename(self.file.name)

    file_type = 'matched'


class UnmatchedFiles(models.Model):
    # Table configuration
    file = models.FileField(upload_to=user_directory_path)
    date_created = models.DateTimeField(default=timezone.now)
    person = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Data Unmatched Outputs"

    def __str__(self):
        return f'{self.person.username} unmatched output {self.date_created}'

    def filename(self):
        return os.path.basename(self.file.name)

    file_type = 'unmatched'
