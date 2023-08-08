import pandas as pd
from django.conf import settings
import sys
from profilit.models import DataFiles


def read_file(file_pk):
    file_path = settings.MEDIA_ROOT + str(DataFiles.objects.get(pk=file_pk))
    file_format = DataFiles.objects.get(pk=file_pk).file_format
    if file_format == 'ex':
        data_file = pd.read_excel(file_path, convert_float=True, na_filter=False, dtype=str)
    elif file_format == 'csv' or 'tx':
        delim = ','
        try:
            data_file = pd.read_csv(file_path, na_filter=False, dtype=str, delimiter=delim, engine='python')
        except pd.errors.ParserError:
            with open(settings.MEDIA_ROOT + '/WARNING.txt', 'w') as fp:
                sys.stderr = fp
                data_file = pd.read_csv(file_path, na_filter=False, dtype=str, engine='python', sep=delim,
                                        error_bad_lines=False)


    return data_file
