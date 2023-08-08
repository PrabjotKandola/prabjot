# -*- coding: utf-8 -*-
"""
@author: DPARNELL/ADODSON
"""
from ast import literal_eval
import pandas as pd
import numpy as np


def run_all_transform_rules(data, rules):
    rules = rules.apply(lambda x: x.str.strip())
    rules = rules[~(rules == '').all(axis=1)]
    q = TransformRules(data)
    for index, row in rules.iterrows():
        getattr(q, row['rule_type'])(row)

    return q.data_df


class TransformRules:
    # Every rule must have an ID
    def __init__(self, data_file):
        self.data_df = data_file  # all data in str format

    def uppercase(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].str.upper()

    def lowercase(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].str.lower()

    def upper_first_of_each_word(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].str.title()

    def upper_first_letter(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].str.capitalize()

    # refdata attribute is a key value pair dict ie {2:"1000",3:"27"}
    def replace_reference_data(self, rule_row):
        attribute = rule_row['attribute']
        ref_data = rule_row['ref_data']
        replace_map = literal_eval(ref_data)
        replace_map = dict([str(a), str(x)] for a, x in replace_map.items())
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].replace(replace_map)

    def replace_null(self, rule_row):
        attribute = rule_row['attribute']
        new_null = rule_row['new_null']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].replace('', new_null)

    def remove_spaces(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].str.replace(' ', '')

    def decimal_place(self, rule_row):
        attribute = rule_row['attribute']
        num_of_dp = rule_row['num_of_dp']
        dp = str(num_of_dp)
        dp_format = '{:.' + dp + 'f}'
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].astype('float').map(dp_format.format).astype(
            'str')

    def format_number_comma_dp(self, rule_row):
        attribute = rule_row['attribute']
        num_of_dp = rule_row['num_of_dp']
        dp = str(num_of_dp)
        dp_format = '{:,.' + dp + 'f}'
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].astype('float').map(dp_format.format).astype(
            'str')

    def mask_with_format(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].apply(lambda x: mask_string_keepformat(x))

    def unmask_with_format(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].apply(lambda x: unmask_string_keepformat(x))

    def mask_without_format(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].apply(lambda x: mask_string_anyascii(x))

    def unmask_without_format(self, rule_row):
        attribute = rule_row['attribute']
        self.data_df.loc[:, attribute] = self.data_df.loc[:, attribute].apply(lambda x: unmask_string_anyascii(x))


def shift_number(number, shift, pos):
    # special chars
    if (number < 65):
        adjusted = number - 32
        if (pos == True):
            number = adjusted + shift
            shifted = number % 33
        elif (pos == False):
            number = adjusted - shift
            shifted = number % 33
        shifted = shifted + 32
    # uppercase
    elif (number > 64 and number < 91):
        adjusted = number - 65
        if (pos == True):
            number = adjusted + shift
            shifted = number % 26
        elif (pos == False):
            number = adjusted - shift
            shifted = number % 26
        shifted = shifted + 65
    # lower case
    elif (number > 96 and number < 123):
        adjusted = number - 97
        if (pos == True):
            number = adjusted + shift
            shifted = number % 26
        elif (pos == False):
            number = adjusted - shift
            shifted = number % 26
        shifted = shifted + 97
    # last special chars
    elif (number > 122):
        adjusted = number - 123
        if (pos == True):
            number = adjusted + shift
            shifted = number % 26
        elif (pos == False):
            number = adjusted - shift
            shifted = number % 26
        shifted = shifted + 123
    return shifted
    # using a shift cipher where k = 17  keeps format of caps,lower,numbers,special


def mask_string_keepformat(string):
    word_ascii_list = [ord(c) for c in str(string)]
    list_shifted = [shift_number(x, 17, True) for x in word_ascii_list]
    shifted_word = ''.join([chr(c) for c in list_shifted])
    return shifted_word
    shifted_word = ''
    return shifted_word


def unmask_string_keepformat(string):
    word_ascii_list = [ord(c) for c in str(string)]
    list_shifted = [shift_number(x, 17, False) for x in word_ascii_list]
    shifted_word = ''.join([chr(c) for c in list_shifted])
    return shifted_word
    shifted_word = ''
    return shifted_word


###################################################################################

###################################################################################
# using a shift cipher where k = 17 does not keep format of caps,lower,numbers,special
def mask_string_anyascii(string):
    word_ascii_list = [ord(c) for c in str(string)]
    list_shifted = [(x + 10) % 128 for x in word_ascii_list]
    shifted_word = ''.join([chr(c) for c in list_shifted])
    return shifted_word


def unmask_string_anyascii(string):
    word_ascii_list = [ord(c) for c in string]
    list_shifted = [(x - 10) % 128 for x in word_ascii_list]
    shifted_word = ''.join([chr(c) for c in list_shifted])
    return shifted_word

    # print(mask_string_keepformat("ze>LO"))
    # print(unmask_string_keepformat("jo'VY"))