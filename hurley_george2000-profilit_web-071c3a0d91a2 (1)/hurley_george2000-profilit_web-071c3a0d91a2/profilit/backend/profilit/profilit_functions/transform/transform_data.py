from . import functions
from django.core.files import File
from profilit.models import TransformedFiles
from profilit.backend.profilit.profilit_functions import general
from datetime import datetime


def main(file_pk, transform_rules_pk, user):
    df_file = general.read_file(file_pk)
    df_transform_rules = general.read_file(transform_rules_pk)
    df_transformed = functions.run_all_transform_rules(df_file, df_transform_rules)
    now_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    transformed_str = 'transformed_' + now_str + '.xlsx'
    df_transformed.to_excel(transformed_str, index=True, engine='xlsxwriter')

    with open(transformed_str, 'rb') as excel:
        transformed_output = TransformedFiles(file=File(excel), person=user)
        transformed_output.save()
