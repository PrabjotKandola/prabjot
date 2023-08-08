from django import forms
from .models import DataFiles


class UploadDataForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = DataFiles
        fields = ['file_type', 'file_format', 'file']


class YourForm(forms.ModelForm):
    class Meta:
        model = DataFiles
        fields = ['file']
        labels = {'file': 'Select File'}

    file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))


class ExplorationForm(forms.Form):
    files = forms.ModelChoiceField(label='Please select a file.', queryset=DataFiles.objects.all())


class ProfileForm(forms.Form):
    data_files = forms.ModelChoiceField(
        label='Please select a data file.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
    rules_template = forms.ModelChoiceField(
        label='Please select a your profiling rules.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
    data_id = forms.CharField(
        max_length=500, help_text='Pick the primary key to identify the errors in the error report '
                                  '(if this is left empty, the first column will be used).',
        required=False
    )


class TransformForm(forms.Form):
    data_files = forms.ModelChoiceField(
        label='Please select a data file.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
    transform_template = forms.ModelChoiceField(
        label='Please select a your transformation rules.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view


class MatchingForm(forms.Form):
    data_files_1 = forms.ModelChoiceField(
        label='Please select a data file.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
    data_files_2 = forms.ModelChoiceField(
        label='Please select a data file.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
    match_template = forms.ModelChoiceField(
        label='Please select a your data matching rules.',
        queryset=DataFiles.objects.all()
    )  # Initiating queryset, set as user dependent in view
