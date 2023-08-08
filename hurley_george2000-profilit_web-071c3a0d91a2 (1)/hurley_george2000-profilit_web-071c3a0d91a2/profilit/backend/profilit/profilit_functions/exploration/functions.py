import pandas as pd
import numpy as np
import re


def exploration_profile(data):
    output_columns = ['min_length', 'max_length', 'min_value', 'max_value', 'completeness', 'non_null_count',
                      'uniqueness',
                      'unique_value_count', 'common_values', 'numeric_percentage', 'date_percentage']
    data_with_nan = data.replace("",np.nan)
    basic_output = pd.DataFrame(index=data.columns, columns=output_columns)
    for column in data.columns:
        col_data = data_with_nan.loc[:, column].dropna().astype(str)
        if len(col_data) == 0:  #  prevents divide by zero errors
            continue
        basic_output.loc[column, 'min_value'] = col_data[col_data.str.isnumeric()].astype(float).min()  # Only find min value of numbers
        basic_output.loc[column, 'max_value'] = col_data[col_data.str.isnumeric()].astype(float).max()
        basic_output.loc[column, 'min_length'] = col_data.str.len().min()
        basic_output.loc[column, 'max_length'] = col_data.str.len().max()
        basic_output.loc[column, 'unique_value_count'] = col_data.nunique()
        value_and_count = ''
        for x in col_data.value_counts()[:3].items():
            value_and_count += str(x)
        basic_output.loc[column, 'common_values'] = value_and_count
        col_numeric_bool = col_data.str.isnumeric()
        basic_output.loc[column, 'numeric_percentage'] = 100 * col_numeric_bool.sum()/len(col_data)
        phone_regex = r'^([\+][0-9]*|[\+][\(][0-9]*[\)]|[\+][\s0-9]*[\(][0-9]+[\)]|[\d]*[\(][\+][0-9]*[\)]' \
        r'|[\d]*[\(][0-9]+[\)]|[0][0-9\-\s]*)([\d\-\s]*)$'
        pattern = re.compile(phone_regex)
        invalid = col_data.apply(lambda x: bool(pattern.match(x)))
        basic_output.loc[column, 'date_percentage'] = 100 * pd.notnull(
            pd.to_datetime(col_data[~(col_numeric_bool | invalid)], errors='coerce')).sum() / len(col_data)

    del col_data

    basic_output.loc[:, 'non_null_count'] = data_with_nan.count().values.tolist()
    basic_output.loc[:, 'completeness'] = 100 * basic_output['non_null_count']/len(data.index)
    basic_output.loc[:, 'uniqueness'] = 100 * basic_output['unique_value_count']\
        .div(basic_output['non_null_count']
             .replace(0, np.nan))
    basic_output.index.name = 'attribute'
    basic_output.loc[:, 'completeness'] = basic_output['completeness'].astype(float).round(3)
    basic_output.loc[:, 'uniqueness'] = basic_output['uniqueness'].astype(float).round(3)
    basic_output.loc[:, 'numeric_percentage'] = basic_output['numeric_percentage'].astype(float).round(3)
    basic_output.loc[:, 'date_percentage'] = basic_output['date_percentage'].astype(float).round(3)
    print(basic_output)
    return basic_output

