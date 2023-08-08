from . import functions
from django.core.files import File
from profilit.backend.profilit.profilit_functions import general
import os
from dashboard.models import RulesBasedProfileFiles, RulesBasedProfilingData, RuleTemplateErrors
from profilit.backend.profilit.Configuration import database_config
from sqlalchemy import String, Integer, Float
from datetime import datetime
import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter


def main(file_pk, rules_pk, data_id, user):
    df_file = general.read_file(file_pk)
    df_rules = general.read_file(rules_pk)

    if data_id not in df_file.columns:
        data_id = df_file.columns[0]
    rules_error_report = functions.check_rules_template(df_file, df_rules)

    engine = database_config.config()

    if not rules_error_report.empty:
        rules_error_report.columns = rules_error_report.columns.str.lower()
        rules_error_report.loc[:, 'person_id'] = user.pk
        rules_error_report.to_sql(
            RuleTemplateErrors._meta.db_table, con=engine, if_exists='append', chunksize=500, index=False,
            dtype={
                'rule_id': String, 'error_message': String, 'person_id': Integer
            }
        )

    else:
        error_report, table, meta = functions.run_all_business_rules(df_file, df_rules, data_id)
        now_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        error_name = 'error_output_'+now_str+'.xlsx'
        error_report.to_excel(error_name, index=False, engine='xlsxwriter')

        with open(error_name, 'rb') as excel:
            file = RulesBasedProfileFiles(file=File(excel), person=user, **meta)
            file.save()
            current_date = file.date_created
            id_for_foreignkey = file.id

        if os.path.exists(error_name):
            os.remove(error_name)

        psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
        table.loc[:, 'date_created'] = current_date
        table.loc[:, 'file_set_id'] = id_for_foreignkey

        table.to_sql(
            RulesBasedProfilingData._meta.db_table, con=engine, if_exists='append', chunksize=500,
            dtype={
                'attribute_failed': String,
                'completeness': Float,
                'uniqueness': Float,
                'conformity': Float,
                'total': Float,
                'total_errors': Integer,
                'file_set_id': Integer
            }
        )
