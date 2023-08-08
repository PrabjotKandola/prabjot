from . import functions
from django.core.files import File
from profilit.models import MatchFiles, UnmatchedFiles
from dashboard.models import MatchingData
from profilit.backend.profilit.profilit_functions import general
import os
from datetime import datetime
from django.utils import timezone


def main(file_pk_1, file_pk_2, rules_pk, user):
    # Read the files
    df_1 = general.read_file(file_pk_1)
    df_2 = general.read_file(file_pk_2)
    df_1_total = len(df_1.index)
    df_2_total = len(df_2.index)
    df_rules = general.read_file(rules_pk)
    try:
        threshold = int(df_rules['threshold'].values[0])
    except ValueError:
        threshold = 90

    match_count, data_count, df_merged, df_errors = functions.do_fuzzy(
        df_1, df_2, key1=df_rules.key_1.values[0], key2=df_rules.key_2.values[0], threshold=threshold
    )
    now_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    matched_errors_str = 'matched_' + now_str + '.xlsx'
    unmatched_errors_str = 'unmatched_' + now_str + '.xlsx'
    df_merged.to_excel(matched_errors_str, index=True, engine='xlsxwriter')
    df_errors.to_excel(unmatched_errors_str, index=True, engine='xlsxwriter')

    excel_1 = open(matched_errors_str, 'rb')
    date = timezone.now()
    match_data = MatchFiles(
        file=File(excel_1), person=user, date_created=date
        )
    match_data.save()
    excel_1.close()

    excel_2 = open(unmatched_errors_str, 'rb')
    unmatched_data = UnmatchedFiles(
        file=File(excel_2), person=user, date_created=date
    )

    unmatched_data.save()
    excel_2.close()

    if os.path.exists(matched_errors_str):
        os.remove(matched_errors_str)

    if os.path.exists(unmatched_errors_str):
        os.remove(unmatched_errors_str)

    # meta={
    #     'data_file_a_total' : df_1_total,
    #     'data_file_b_total' : df_2_total,
    #     'matched_file' : match_data,
    #     'unmatched_file' : unmatched_data
    # }
    x=MatchingData(data_file_a_total=df_1_total, data_file_b_total=df_2_total,
                 match_count=match_count, data_count=data_count,
                 person=user, date_created=date)

    x.save()
