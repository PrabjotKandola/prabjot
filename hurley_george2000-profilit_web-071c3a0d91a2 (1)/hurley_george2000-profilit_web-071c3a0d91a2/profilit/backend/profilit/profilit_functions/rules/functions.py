# -*- coding: utf-8 -*-
"""
@author: Arthur Dodson
"""

import pandas as pd
import numpy as np
import re
import math
from profilit.backend.profilit.profilit_functions.rules import metrics
rules_output_columns = ['attribute_failed', 'rule_id', 'error_message', 'metrics', 'error_value']


def check_rules_template(data, rules):
    rules = rules.apply(lambda x: x.str.strip())
    rules = rules[~(rules == '').all(axis=1)]
    error_output = pd.DataFrame(columns=['rule_id', 'error_message'])
    q = BusinessRuleAttributes(data)
    rule_types = [x for x in dir(q) if x[:2] != '__']

    for index, row in rules.iterrows():
        print(row)
        rule_type = row['rule_type']
        if rule_type not in rule_types:
            error_output = error_output.append(pd.DataFrame([{'rule_id': row['rule_id'],
                                                              'error_message': 'Rule type \'{}\' is not valid'.format(
                                                                  rule_type)}]))
        else:
            error_output = error_output.append(
                pd.DataFrame([{'rule_id': row['rule_id'], 'error_message':getattr(q, row['rule_type'])(row)}])
        )
    error_output = error_output[error_output['error_message'] != '']
    return error_output


def run_all_business_rules(data, rules, data_id):
    rules = rules.apply(lambda x: x.str.strip())
    rules = rules[~(rules == '').all(axis=1)]
    output_columns = [data_id] + rules_output_columns
    error_output = pd.DataFrame(columns=output_columns)
    q = BusinessRules(data, data_id, output_columns)

    # Dataframe for counting number of rule types tested against each attribute
    metric_df = pd.DataFrame(
        data=0, columns=['conformity', 'completeness', 'uniqueness'], index=rules['attribute'].unique()
    )
    for index, row in rules.iterrows():
        metric_id = getattr(metrics, row['rule_type'])
        metric_df.loc[row['attribute'], metric_id] += 1
        error_output = error_output.append(getattr(q, row['rule_type'])(row))

    del q, output_columns
    metric_df.loc[:, 'total'] = metric_df.sum(axis=1)

    error_output = error_output.drop_duplicates()
    table = pd.pivot_table(error_output.loc[:, ['attribute_failed', 'metrics']], index=['attribute_failed'],
                           columns=['metrics'], aggfunc='size')
    data_length = len(data.index)
    total_errors = table.sum(axis=1)
    table.loc[:, 'total'] = total_errors
    print('table 1 = ', table)
    print('metric count = ', metric_df.loc[:, table.columns] * data_length)
    table = table.div(metric_df.loc[:, table.columns] * data_length, fill_value=0)
    table = 1 - table
    table = (table * 100).round(3)
    table.loc[:, 'total_errors'] = total_errors
    total_errors_metric = table.sum(axis=0)/metric_df.sum(axis=0)
    table.index.name = 'attribute_failed'
    print('table 2 = ', table)
    meta = {'total_records': data_length,
            'total_data_points': data_length * len(data.columns),
            'total_errors': len(error_output.index),
            'total_profile': data_length * len(rules.index),
            'total_failed_data_points': len(error_output.drop_duplicates([data_id, 'attribute_failed']).index),
            'total_failed_records': len(error_output.loc[:, data_id].unique()),
            'completeness': total_errors_metric['completeness'].round(3),
            'uniqueness': total_errors_metric['uniqueness'].round(3),
            'conformity': total_errors_metric['conformity'].round(3)}
    return error_output, table, meta


class BusinessRules:
    # Every rule must have an ID
    def __init__(self, data_file, data_id, output_columns):
        self.data_df = data_file  # all data in str format
        self.data_id = data_id
        self.output_columns = output_columns

    def error_compilation(self, failed, data_id, error_attribute, rule_row, metric, attribute_name):
        errors_to_add = failed.loc[:, [data_id, error_attribute]]
        errors_to_add.columns = [data_id, 'error_value']
        errors_to_add.loc[:, 'error_message'] = rule_row['error_message']
        errors_to_add.loc[:, 'rule_id'] = rule_row['rule_id']
        errors_to_add.loc[:, 'metrics'] = metric
        errors_to_add.loc[:, 'attribute_failed'] = attribute_name
        errors_to_add = errors_to_add[self.output_columns]
        # errors_to_add = pd.concat([errors_to_add, failed.drop(data_id, axis=1)], axis=1)
        return errors_to_add

    ####################### MANDATORY RULES ############################

    def check_mandatory(self, rule_row):
        metric = 'completeness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        failed = data[data[attribute] == '']
        # failed = data.loc[(data[attribute] == '').values, :]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def check_uniqueness(self, rule_row):
        metric = 'uniqueness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        condition = rule_row['condition']
        if condition.lower() == 'include blanks':
            duplicates = data[attribute].duplicated(keep=False)
        else:
            duplicates = (data.loc[:, attribute] != '') & (data.loc[:, attribute].duplicated(keep=False))

        failed = data[duplicates]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def check_min_length(self, rule_row):
        """
        :param rule_row: Contains the attribute and minimum length criterion.
        :return: Any errors which are below the minimum length.
        """
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        min_length = rule_row['min_value'].strip()
        condition = rule_row['condition']
        if condition.lower() == 'include blanks':
            invalid = data[attribute].str.len() < int(min_length)
        else:
            invalid = (data[attribute] != '') & (data[attribute].str.len() < int(min_length))
        failed = data[invalid]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    # types of conditions a2 is equal; a2 is in; a2 not equal; a2 is null, a2 isnt null

    def check_mandatory_conditional(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        condition_attribute = rule_row['condition_attribute(s)']
        condition_value = rule_row['value(s)']
        condition = rule_row['condition'].strip()
        # print('condition attribute = ',condition_attribute)
        if (condition == "equal"):
            valid_records = data[condition_attribute] == condition_value
        elif (condition.lower() == "not equal"):
            valid_records = data[condition_attribute] != condition_value
        elif (condition == "is null"):
            valid_records = data[condition_attribute] == ""
        elif (condition == "not null"):
            valid_records = data[condition_attribute] != ""
        records_to_check = data[valid_records]
        is_mandatory = records_to_check[attribute] == ""
        failed = records_to_check[is_mandatory]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def check_valid_values(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        valid_values = rule_row['value(s)']
        case_sensitive = rule_row['condition']
        if case_sensitive.strip().lower() == 'ignore case':
            valid_values = [x.strip().lower() for x in valid_values.split(',')]
            is_not_valid = ~data[attribute].str.lower().isin(valid_values)
        else:
            valid_values = [x.strip() for x in valid_values.split(',')]
            is_not_valid = ~data[attribute].isin(valid_values)
        failed = data[is_not_valid]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def check_against_regex(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        regex_pattern = rule_row['regex']
        if rule_row['whitespace_trim'].lower() == 'no':
            pass
        else:
            data.loc[:, attribute] = data[attribute].str.strip()
        pattern = re.compile(regex_pattern)
        is_valid = data[attribute].apply(lambda x: bool(pattern.match(x)))
        failed = data[~is_valid]
        failed = failed[failed[attribute] != '']  # ignore blanks
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    # check max length
    def check_max_length(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        max_len = rule_row['max_value'].strip()
        failed = data[(data[attribute].str.len() > int(max_len))]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def must_be_the_same_as(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute.strip()] + attributes
        failed = data[attributes].nunique(axis=1, dropna=True)
        failed = data[failed != 1]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def uniqueness_across_attributes(self, rule_row):
        metric = 'uniqueness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        attributes = [x.strip() for x in attribute.split(',')] + attributes
        condition = rule_row['condition']

        if condition.lower() == 'include blanks':
            n_unique = data[attributes].nunique(axis=1)
            failed = data[n_unique < data[attributes].shape[1]]
        else:
            n_unique = data[attributes].replace('', np.nan).nunique(axis=1)
            failed = data[n_unique + (data[attributes] == '').sum(axis=1) < data[attributes].shape[1]]

        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    # check if the field is alphabetic spaces = y or n
    def check_if_alphabetic(self, rule_row):
        if (rule_row['condition'] == 'spaces'):
            rule_row['regex'] = r'^[A-Za-z\s]+$'
            errors_to_add = self.check_against_regex(rule_row)
        else:
            rule_row['regex'] = r'^[A-Za-z]+$'
            errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if the field is alphabetic
    def check_if_numeric(self, rule_row):
        if (rule_row['condition'] == 'spaces'):
            rule_row['regex'] = r'^[0-9\s]+$'
            errors_to_add = self.check_against_regex(rule_row)
        else:
            rule_row['regex'] = r'^[0-9]+$'
            errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if valid UK Company house Registeration
    def check_if_company_reg(self, rule_row):
        rule_row['regex'] = r'^[0-9]{5,8}$|^(OC|LP|SC|SO|SL|NI|NC|NL|R|AC|CE|CS|FC|FE|GE|GN|GS|IC|IP|NA|NF|NO|NP|NR|' \
                            r'NV|NZ|PC|RO|RC|RS|SA|SE|SF|SG|SI|SP|SR|SZ|SO|ES)([0-9]{6})$|^R[0-9]{7}$'
        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if valid AWRS Num
    def check_if_AWRS(self, rule_row):
        rule_row['regex'] = r'[A-Za-z/s]{4}[0-9\s]{9}'
        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if valid VAT Number
    def check_if_VAT(self, rule_row):
        rule_row['regex'] = r'([0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{2})|(GB)([0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{2}|[0-9]{9}' \
                            r'\s{1}[0-9]{3}|GD[0-4][0-9]{2}|HA[5-9][0-9]{2})$'

        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if the postcode is valid, this is the UK governoment provided regex,
    # some false positives will arise such as AA
    def check_if_valid_postcode(self, rule_row):
        rule_row['regex'] = r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|' \
                            r'(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})'
        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if the email address is valid
    def check_if_valid_email(self, rule_row):
        rule_row['regex'] = r'^([a-zA-Z0-9][a-zA-Z0-9._%+-]{0,61}|[a-zA-Z0-9]?)([a-zA-Z0-9][a-zA-Z0-9_%+-]@[a-zA-Z0' \
                            r'-9_%+-]|[a-zA-Z0-9]@[a-zA-Z0-9_%+-])(?:[a-zA-Z0-9-.]' \
                            r'(?:[a-zA-Z0-9-]{0,62}[a-zA-Z0-9])?\.){1,8}[a-zA-Z]{2,63}$'

        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check if the phone number is valid
    def check_if_valid_phonenumber(self, rule_row):
        rule_row['regex'] = r'^([\+][0-9]*|[\+][\(][0-9]*[\)]|[\+][\s0-9]*[\(][0-9]+[\)]|[\d]*[\(][\+][0-9]*[\)]' \
                            r'|[\d]*[\(][0-9]+[\)]|[0][0-9\-\s]*)([\d\-\s]*)$'

        errors_to_add = self.check_against_regex(rule_row)
        # errors_to_add = errors_to_add[errors_to_add.loc[:, 'error_value'] != '']
        return errors_to_add

    # check the length
    def check_length_in_range(self, rule_row):
        failed_min = self.check_min_length(rule_row)
        failed_max = self.check_max_length(rule_row)
        if failed_min is not None or failed_max is not None:
            errors_to_add = pd.concat([failed_min, failed_max])
            errors_to_add = errors_to_add[errors_to_add['error_value'] != '']
            return errors_to_add

    def conditional_check_against_regex(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id

        trig_attribute = rule_row['attribute'].strip()  # 'a1  , a2,a3'

        rule_2 = rule_row['rule_type_2']

        #  Attribute, value and condition grouping one
        attribute_list_1 = rule_row['condition_attribute(s)'].strip()
        attribute_list_1 = [x.strip() for x in attribute_list_1.split(',')]
        condition_1 = rule_row['condition']
        value_1 = rule_row['condition_value(s)_1']
        value_1 = [x.strip() for x in value_1.split(',')]
        dict_1 = {'attributes': attribute_list_1, 'condition': condition_1, 'values': value_1}

        #  Attribute, value and condition grouping two
        attribute_list_2 = rule_row['condition_attribute(s)_2'].strip()
        attribute_list_2 = [x.strip() for x in attribute_list_2.split(',')]
        condition_2 = rule_row['condition_2']
        value_2 = rule_row['condition_value(s)_2']
        value_2 = [x.strip() for x in value_2.split(',')]
        dict_2 = {'attributes': attribute_list_2, 'condition': condition_2, 'values': value_2}

        #  Attribute, value and condition grouping three
        attribute_list_3 = rule_row['condition_attribute(s)_3'].strip()
        attribute_list_3 = [x.strip() for x in attribute_list_3.split(',')]
        condition_3 = rule_row['condition_3']
        value_3 = rule_row['condition_value(s)_3']
        value_3 = [x.strip() for x in value_3.split(',')]
        dict_3 = {'attributes': attribute_list_3, 'condition': condition_3, 'values': value_3}

        dictionaries = [dict_1, dict_2, dict_3]

        #  Get rule_type_2 and find all occurances trig_attribute does not match regex
        rule_row['rule_type'] = rule_2
        print(rule_2)
        print(rule_row)
        x = getattr(self, rule_2)(rule_row)
        if isinstance(x, type(pd.DataFrame())):
            x = data.index.isin(x.index.values)
        else:
            x = False

        for d in dictionaries:
            if d['attributes'][0] == '':
                continue
            elif len(d['attributes']) == 1:
                y = data[d['attributes'][0]].isin(d['values'])
            else:
                y = data.loc[:, d['attributes']].isin(d['values']).any(axis=1)

            if d['condition'].lower() == 'not equal':
                x = x & ~y
            else:
                x = x & y  # instances where y in value_2 but x is not

        failed = data[x]

        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=trig_attribute,
                                          rule_row=rule_row, metric=metric, attribute_name=trig_attribute)

    def conditional_entry_must_be(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        trig_attribute_list = rule_row['attribute'].strip()  # 'a1  , a2,a3'
        trig_attribute_list = [x.strip() for x in trig_attribute_list.split(',')]  # ['a1', 'a2', 'a3']
        values = rule_row['value(s)']
        values = [x.strip() for x in values.split(',')]

        attribute_list_1 = rule_row['condition_attribute(s)'].strip()
        attribute_list_1 = [x.strip() for x in attribute_list_1.split(',')]
        condition_1 = rule_row['condition']
        value_1 = rule_row['condition_value(s)_1']
        value_1 = [x.strip() for x in value_1.split(',')]
        dict_1 = {'attributes': attribute_list_1, 'condition': condition_1, 'values': value_1}

        attribute_list_2 = rule_row['condition_attribute(s)_2'].strip()
        attribute_list_2 = [x.strip() for x in attribute_list_2.split(',')]
        condition_2 = rule_row['condition_2']
        value_2 = rule_row['condition_value(s)_2']
        value_2 = [x.strip() for x in value_2.split(',')]
        dict_2 = {'attributes': attribute_list_2, 'condition': condition_2, 'values': value_2}

        attribute_list_3 = rule_row['condition_attribute(s)_3'].strip()
        attribute_list_3 = [x.strip() for x in attribute_list_3.split(',')]
        condition_3 = rule_row['condition_3']
        value_3 = rule_row['condition_value(s)_3']
        value_3 = [x.strip() for x in value_3.split(',')]
        dict_3 = {'attributes': attribute_list_3, 'condition': condition_3, 'values': value_3}

        dictionaries = [dict_1, dict_2, dict_3]

        if len(trig_attribute_list) == 1:
            x = data[trig_attribute_list[0]].isin(values)
        else:
            if rule_row['All or Any'] == 'All':
                x = data.loc[:, trig_attribute_list].isin(values).all(axis=1)
            else:
                x = data.loc[:, trig_attribute_list].isin(values).any(axis=1)

        x = ~x  # Errors will only occur when x is NOT in value_1

        for d in dictionaries:
            if d['attributes'][0] == '':
                continue
            elif len(d['attributes']) == 1:
                y = data[d['attributes'][0]].isin(d['values'])
            else:
                y = data.loc[:, d['attributes']].isin(d['values']).any(axis=1)

            if d['condition'].lower() == 'not equal':
                x = x & ~y
            else:
                x = x & y  # instances where y in value_2 but x is not

        failed = data[x]

        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=trig_attribute_list[0],
                                          rule_row=rule_row,
                                          metric=metric, attribute_name=', '.join(trig_attribute_list))

    def conditional_entry_must_not_be(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        trig_attribute_list = rule_row['attribute'].strip()  # 'a1  , a2,a3'
        trig_attribute_list = [x.strip() for x in trig_attribute_list.split(',')]  # ['a1', 'a2', 'a3']
        values = rule_row['value(s)']
        values = [x.strip() for x in values.split(',')]

        attribute_list_1 = rule_row['condition_attribute(s)'].strip()
        attribute_list_1 = [x.strip() for x in attribute_list_1.split(',')]
        condition_1 = rule_row['condition']
        value_1 = rule_row['condition_value(s)_1']
        value_1 = [x.strip() for x in value_1.split(',')]
        dict_1 = {'attributes': attribute_list_1, 'condition': condition_1, 'values': value_1}

        attribute_list_2 = rule_row['condition_attribute(s)_2'].strip()
        attribute_list_2 = [x.strip() for x in attribute_list_2.split(',')]
        condition_2 = rule_row['condition_2']
        value_2 = rule_row['condition_value(s)_2']
        value_2 = [x.strip() for x in value_2.split(',')]
        dict_2 = {'attributes': attribute_list_2, 'condition': condition_2, 'values': value_2}

        attribute_list_3 = rule_row['condition_attribute(s)_3'].strip()
        attribute_list_3 = [x.strip() for x in attribute_list_3.split(',')]
        condition_3 = rule_row['condition_3']
        value_3 = rule_row['condition_value(s)_3']
        value_3 = [x.strip() for x in value_3.split(',')]
        dict_3 = {'attributes': attribute_list_3, 'condition': condition_3, 'values': value_3}

        dictionaries = [dict_1, dict_2, dict_3]

        #  potential errors when x is equal to one of the values
        if len(trig_attribute_list) == 1:
            x = data[trig_attribute_list[0]].isin(values)
        else:
            if rule_row['All or Any'] == 'All':
                x = data.loc[:, trig_attribute_list].isin(values).all(axis=1)
            else:
                x = data.loc[:, trig_attribute_list].isin(values).any(axis=1)

        for d in dictionaries:
            if d['attributes'][0] == '':
                continue
            elif len(d['attributes']) == 1:
                y = data[d['attributes'][0]].isin(d['values'])
            else:
                y = data.loc[:, d['attributes']].isin(d['values']).any(axis=1)

            if d['condition'].lower() == 'not equal':
                x = x & ~y
            else:
                x = x & y  # instances where y in value_2 but x is not

        failed = data[x]

        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=trig_attribute_list[0],
                                          rule_row=rule_row,
                                          metric=metric, attribute_name=', '.join(trig_attribute_list))

    def either_one_must_equal(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)'].strip()
        value = rule_row['value(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute] + attribute_list
        # check if attributes equal a value and if any of them do, then the rule passes. hence failed = ~passed
        failed = data[~((data[attributes] == value).any(axis=1))]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def mandatory_at_least_one(self, rule_row):
        metric = 'completeness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute] + attribute_list
        failed = data[(data[attributes] == '').all(axis=1)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    # MANDATORY ONE PER TYPE  # list of attributes vs list of values... all must be present
    def mandatory_one_per_type(self, rule_row):
        metric = 'uniqueness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        values = rule_row['value(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        values = [x.strip() for x in values.split(',')]
        attributes = [attribute] + attribute_list
        failed = data[attributes].nunique(axis=1) < len(values)  # any duplicates fail
        failed = data[failed | (~data[attributes].isin(values)).any(axis=1)]  # anything not in valid values fails
        # failed = failed[failed[attribute] != '']  # ignoring blanks
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    # ONLY ONE (CONDITIONAL)
    def only_one_conditional(self, rule_row):
        metric = 'uniqueness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        values = rule_row['value(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        values = [x.strip() for x in values.split(',')]
        trigger_att = data[attribute]
        cond_att = data[attribute_list]
        is_not_valid = (trigger_att.isin(values)) & (cond_att == '').any(axis=1)
        failed = data[is_not_valid]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def entry_contains(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        value = rule_row['value(s)'].strip()
        failed = data[data[attribute].str.contains(value)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def entry_does_not_contain(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        value = rule_row['value(s)'].strip()
        failed = data[~data[attribute].str.contains(value)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def entry_begins_with(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        value = rule_row['value(s)'].strip()
        failed = data[data[attribute].str.startswith(value)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def entry_ends_with(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        value = rule_row['value(s)'].strip()
        failed = data[data[attribute].str.endswith(value)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def not_a_date(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        df = pd.DataFrame(data=data[attribute], columns=[attribute, 'is_not_date'])
        df.is_not_date = pd.isnull(pd.to_datetime(df[attribute], errors='coerce'))
        failed = data[df.is_not_date].reset_index(drop=True)
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def greater_than(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        condition_attribute = rule_row['condition_attribute(s)'].strip()
        failed = data[data[attribute] < data[condition_attribute]]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def lesser_than(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        condition_attribute = rule_row['condition_attribute(s)'].strip()
        failed = data[data[attribute] > data[condition_attribute]]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def uniqueness_within_supplier(self, rule_row):
        metric = 'uniqueness'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute] + attribute_list
        failed = data[data[attributes].duplicated()].sort_values(by=attribute).reset_index(drop=True)
        failed = failed[failed[attribute] != '']  # ignoring blanks
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def value_between(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        max_value = rule_row['max_value'].strip()
        min_value = rule_row['min_value'].strip()
        data.loc[:, attribute] = data[attribute].str.strip()  # strip any whitespace around strings
        data_to_check = data.loc[data[attribute] != '', attribute]  # not a mandatory check so ignoring blanks
        data_to_check = pd.to_numeric(data_to_check, errors='coerce')
        not_between = ~data_to_check.between(float(min_value), float(max_value))
        failed = data.loc[not_between[not_between].index, :].sort_index()
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def conditional_sum(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        data_to_check = data.loc[:, [attribute] + attribute_list]
        data_to_check.apply(lambda column: pd.to_numeric(column, errors='coerce'))
        failed = data[~(data_to_check[attribute] == data_to_check.loc[:, attribute_list].sum(axis=1))]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def total_sum(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        attribute_list = rule_row['condition_attribute(s)']
        condition_value = float(rule_row['value(s)'].strip())
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute] + attribute_list
        data_to_check = data.loc[:, attributes]
        data_to_check = data_to_check.apply(lambda column: pd.to_numeric(column, errors='coerce'))
        failed = data[~(data_to_check.loc[:, attributes].sum(axis=1) - condition_value).between(-0.000001, 0.000001)]
        failed = failed[~(failed.loc[:, attributes] == '').all(axis=1)]  # ignore rows which are all blank
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def check_divisibility(self, rule_row):
        metric = 'conformity'
        #  checking divisibility of dataframe to precision of 6 decimal places
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        condition_value = float(rule_row['value(s)'].strip())
        data.loc[:, attribute] = data[attribute].str.strip()  # strip any whitespace around strings
        data = data[data[attribute] != '']  # not a mandatory check so ignoring blanks
        data_to_check = data.loc[:, attribute]
        data_to_check = pd.to_numeric(data_to_check, errors='coerce')
        recurring_decimal = data_to_check.apply(lambda x: math.modf(x / condition_value)[0])
        not_divisible = ~(
                recurring_decimal.between(-0.000001, 0.000001) | recurring_decimal.between(0.999999, 1.000001))
        failed = data.loc[not_divisible[not_divisible].index, :].sort_index()
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)

    def value_close_to(self, rule_row):
        metric = 'conformity'
        data = self.data_df
        data_id = self.data_id
        attribute = rule_row['attribute'].strip()
        condition_attr = rule_row['condition_attribute(s)'].strip()
        max_value = float(rule_row['max_value'].strip())
        min_value = float(rule_row['min_value'].strip())
        data_to_check = data.loc[:, [attribute, condition_attr]].apply(
            lambda column: pd.to_numeric(column, errors='coerce'))
        failed = data[~(data_to_check[attribute].sub(data_to_check[condition_attr]).between(min_value, max_value))]
        failed = failed[~(failed.loc[:, [attribute, condition_attr]] == '').all(axis=1)]
        if failed.size > 0:
            return self.error_compilation(failed=failed, data_id=data_id, error_attribute=attribute, rule_row=rule_row,
                                          metric=metric,
                                          attribute_name=attribute)



class BusinessRuleAttributes:
    # Every rule must have an ID
    def __init__(self, data_file):
        self.data_attributes = data_file.columns  # all data in str format

    def check_mandatory(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found.'.format(attribute)
        return error_message

    def check_uniqueness(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found.'.format(attribute)
        return error_message

    def check_min_length(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        min_len = rule_row['min_value']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if min_len.isnumeric() == False:
            error_message = error_message + 'The min_value \'{}\' is not a number.'.format(min_len)
        return error_message

    # types of conditions a2 is equal; a2 is in; a2 not equal; a2 is null, a2 isnt null

    def check_mandatory_conditional(self, rule_row):
        # condition_value can be anything and hence cannot be an error?
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        condition_attribute = rule_row['condition_attribute(s)']
        condition = rule_row['condition']
        condition_value = rule_row['value(s)']
        condition_list = ['equal', 'not equal', 'is null', 'not null']
        attributes = [x.strip() for x in condition_attribute.split(',')]

        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)

        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attributes \'{}\' can\'t be found. '.format(a)

        if condition_value == '':
            error_message += 'The condition must be one of \'{}\'. '.format(
                condition_list)
        if condition not in condition_list:
            error_message += 'The condition must be one of \'{}\'. '.format(
                condition_list)

        return error_message

    #############  TO DO ###################
    def check_valid_values(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        valid_values = rule_row['value(s)']

        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if valid_values == '':
            error_message += 'The valid values \'{}\' are empty '.format(valid_values)

        return error_message

    def check_against_regex(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes

        attribute = rule_row['attribute']
        regex_pattern = rule_row['regex']

        try:
            re.compile(regex_pattern)
            is_valid = True
        except re.error:
            is_valid = False

        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if regex_pattern == '':
            error_message += 'The regex pattern \'{}\' is empty. '.format(regex_pattern)
        if not is_valid:
            error_message += 'The regex pattern \'{}\' is invalid. '.format(regex_pattern)

        return error_message

    # check max length
    def check_max_length(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        max_len = rule_row['max_value']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if max_len.isnumeric() == False:
            error_message += 'The max length \'{}\' is not a number. '.format(max_len)
        return error_message

    def must_be_the_same_as(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attributes \'{}\' can\'t be found. '.format(a)
        return error_message

    def uniqueness_across_attributes(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attributes \'{}\' can\'t be found. '.format(a)
        return error_message

    # check if the field is alphabetic spaces = y or n
    def check_if_alphabetic(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        condition = rule_row['condition']
        condition_list = ['spaces', '']
        if attribute not in data_attributes:
            error_message += 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if condition not in condition_list:
            error_message += 'The condition must be one of the following \'{}\'. '.format(
                condition_list)
        return error_message

    # check if the field is alphabetic
    def check_if_numeric(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        condition = rule_row['condition']
        condition_list = ['equal', 'not equal', 'null', 'not null', 'spaces', '']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if condition not in condition_list:
            error_message += 'The condition must be one of \'{}\'. '.format(
                condition_list)
        return error_message

    # check if valid UK Company house Registeration
    def check_if_company_reg(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check if valid AWRS Num
    def check_if_AWRS(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check if valid VAT Number
    def check_if_VAT(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check if the postcode is valid
    def check_if_valid_postcode(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check if the email address is valid
    def check_if_valid_email(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check if the phone number is valid
    def check_if_valid_phonenumber(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    # check the length
    def check_length_in_range(self, rule_row):
        min_len = rule_row['min_value']
        max_len = rule_row['max_value']
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if min_len.isnumeric() == False:
            error_message += 'The minimun length \'{}\' is not a number. '.format(min_len)
        if max_len.isnumeric() == False:
            error_message += 'The maximum length \'{}\' is not a number. '.format(max_len)
        if (min_len.isnumeric() & max_len.isnumeric()):
            if min_len > max_len:
                error_message += "The maximum length '" + max_len + "' must be greater than or equal to the minimum length '" \
                                 + min_len + "'"
        return error_message

    # IF THIS = X THEN THAT = Y (VALUE_MUST_BE)  #sort syntax
    def conditional_entry_must_be(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_2 = rule_row['condition_attribute(s)']
        attribute_3 = rule_row['condition_attribute(s)_2']
        attribute_4 = rule_row['condition_attribute(s)_3']
        attributes = [x.strip() for x in attribute.split(',')]
        attributes_2 = [x.strip() for x in attribute_2.split(',')]
        attributes_3 = [x.strip() for x in attribute_3.split(',')]
        attributes_4 = [x.strip() for x in attribute_4.split(',')]
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attributes \'{}\' can\'t be found. '.format(a)
        for a in attributes_2:
            if a not in data_attributes:
                error_message += 'The conditional_attribute(s) \'{}\' can\'t be found. '.format(a)
        if attribute_3!='':
            for a in attributes_3:
                if a not in data_attributes:
                    error_message += 'The conditional_attributes_2 \'{}\' can\'t be found. '.format(a)
        if attribute_4!='':
            for a in attributes_4:
                if a not in data_attributes:
                    error_message += 'The conditional_attributes_3 \'{}\' can\'t be found. '.format(a)
        return error_message

    def conditional_entry_must_not_be(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_2 = rule_row['condition_attribute(s)']
        attribute_3 = rule_row['condition_attribute(s)_2']
        attribute_4 = rule_row['condition_attribute(s)_3']
        attributes = [x.strip() for x in attribute.split(',')]
        attributes_2 = [x.strip() for x in attribute_2.split(',')]
        attributes_3 = [x.strip() for x in attribute_3.split(',')]
        attributes_4 = [x.strip() for x in attribute_4.split(',')]
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attributes \'{}\' can\'t be found. '.format(a)

        for a in attributes_2:
            if a not in data_attributes:
                error_message += 'The conditional_attribute(s) \'{}\' can\'t be found. '.format(a)
        if attribute_3 != '':
            for a in attributes_3:
                if a not in data_attributes:
                    error_message += 'The conditional_attributes_2 \'{}\' can\'t be found. '.format(a)
        if attribute_4 != '':
            for a in attributes_4:
                if a not in data_attributes:
                    error_message += 'The conditional_attributes_3 \'{}\' can\'t be found. '.format(a)
        return error_message

    def either_one_must_equal(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        value = rule_row['value(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if value == '':
            error_message += 'The first conditional value  \'{}\' is empty. '.format(value)
        return error_message

    # MANDATORY ONE PER TYPE  # list of attributes vs list of values... all must be present
    def mandatory_one_per_type(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        values = rule_row['value(s)'].split(',')
        attribute_list = [x.strip() for x in attribute_list.split(',')]
        attributes = [attribute] + attribute_list
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if len(values) != len(attributes):
            error_message += 'The total number of attributes (\'{}\') does not equal the ' \
                             'number of condition_value(s) (\'{}\').'.format(len(attributes), len(values))
        return error_message

    # ONLY ONE (CONDITIONAL)
    def only_one_conditional(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        value = rule_row['value(s)']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if value == '':
            error_message += 'The condition value  \'{}\' is empty. '.format(value)
        return error_message

    def entry_contains(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        value = rule_row['value(s)']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if value == '':
            error_message += 'The condition value  \'{}\' is empty. '.format(value)
        return error_message

    def entry_does_not_contain(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        value = rule_row['value(s)']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if value == '':
            error_message += 'The condition value  \'{}\' is empty. '.format(value)
        return error_message

    def entry_begins_with(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        value = rule_row['value(s)']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if value == '':
            error_message += 'The condition value  \'{}\' is empty. '.format(value)
        return error_message

    def entry_ends_with(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        value = rule_row['value(s)']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if value == '':
            error_message += 'The condition value  \'{}\' is empty. '.format(value)
        return error_message

    def not_a_date(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        return error_message

    def uniqueness_within_supplier(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        return error_message

    def mandatory_at_least_one(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        return error_message

    def greater_than(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        return error_message

    def lesser_than(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        return error_message

    def value_between(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        max_value = rule_row['max_value']
        min_value = rule_row['min_value']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if min_value.isnumeric() == False:
            error_message += 'The minimun length \'{}\' is not a number. '.format(min_value)
        if max_value.isnumeric() == False:
            error_message += 'The maximum length \'{}\' is not a number. '.format(max_value)
        return error_message

    def conditional_sum(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        return error_message

    def total_sum(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        condition_value = rule_row['value(s)'].strip()
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if condition_value.isfloat() == False:
            error_message += 'The condition value \'{}\' is not a float. '.format(condition_value)
        return error_message

    def check_divisibility(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        condition_value = rule_row['value(s)'].strip()
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        if condition_value.isfloat() == False:
            error_message += 'The condition value \'{}\' is not a float. '.format(condition_value)
        return error_message

    def value_close_to(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        attribute_list = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in attribute_list.split(',')]
        max_value = rule_row['max_value'].strip()
        min_value = rule_row['min_value'].strip()
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if max_value.isfloat() == False:
            error_message += 'The maximum value \'{}\' is not a float. '.format(max_value)
        if min_value.isfloat() == False:
            error_message += 'The minimum value \'{}\' is not a float. '.format(min_value)
        return error_message

    def conditional_check_against_regex(self, rule_row):
        error_message = ''
        data_attributes = self.data_attributes
        attribute = rule_row['attribute']
        rule_types = [x for x in dir(BusinessRuleAttributes) if x[:2] != '__']
        rule_type_2 = rule_row['rule_type_2']
        condition_attribute = rule_row['condition_attribute(s)']
        attributes = [x.strip() for x in condition_attribute.split(',')]
        condition_value = rule_row['condition_value(s)_1']
        if attribute not in data_attributes:
            error_message = 'The attribute \'{}\' can\'t be found. '.format(attribute)
        for a in attributes:
            if a not in data_attributes:
                error_message += 'The attribute \'{}\' can\'t be found. '.format(a)
        if rule_type_2 not in rule_types:
            error_message += 'The second rule type \'{}\' can\'t be found. '.format(rule_type_2)
        if condition_value == '':
            error_message += 'The condition value \'{}\' is empty. '.format(condition_value)
        return error_message



def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
