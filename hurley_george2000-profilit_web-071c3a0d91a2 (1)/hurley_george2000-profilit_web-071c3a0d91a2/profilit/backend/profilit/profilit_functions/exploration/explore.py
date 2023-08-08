from . import functions
from django.core.files import File
from dashboard.models import ExplorationData, ExplorationFiles
from profilit.backend.profilit.profilit_functions import general
import os
from sqlalchemy import Integer, String, Float
import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter
from profilit.backend.profilit.Configuration import database_config
from datetime import datetime


def main(file_pk, user):

    df_file = general.read_file(file_pk)
    processed_file = functions.exploration_profile(df_file)
    now_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    output_str = 'explore_output_' + now_str + '.xlsx'
    processed_file.to_excel(output_str, index=True)

    with open(output_str, 'rb') as excel:
        exp_file = ExplorationFiles(file=File(excel), person=user)
        exp_file.save()
        id_for_foreignkey = exp_file.id

    psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
    processed_file.loc[:, 'file_set_id'] = id_for_foreignkey
    print(id_for_foreignkey)
    if os.path.exists(output_str):
        os.remove(output_str)

    engine = database_config.config()
    processed_file.to_sql(
        ExplorationData._meta.db_table, con=engine, if_exists='append', chunksize=500,
        dtype={
            'attribute': String, 'min_length': Integer, 'max_length': Integer, 'min_value': Float,
            'max_value': Float, 'completeness': Float, 'non_null_count': Integer, 'uniqueness': Float,
            'unique_value_count': Integer, 'common_values': String, 'numeric_percentage': Float,
            'date_percentage': Float, 'file_set_id': Integer
        }
    )

