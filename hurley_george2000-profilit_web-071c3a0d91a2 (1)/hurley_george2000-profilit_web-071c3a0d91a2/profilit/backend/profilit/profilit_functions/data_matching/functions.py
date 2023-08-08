from fuzzywuzzy import process
import pandas as pd


def fuzzy_merge(df_1, df_2, key1, key2, limit=1):
    s = df_2[key2].tolist()
    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit)[0])
    df_1['matches'] = m
    df_1[['matches', 'score']] = pd.DataFrame(df_1['matches'].tolist(), index=df_1.index)
    # m2 = df_1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
    # df_1['matches'] = m2
    return df_1


def do_fuzzy(df1, df2, key1, key2, threshold):
    key1_list = [x.strip() for x in key1.split(',')]
    key2_list = [x.strip() for x in key2.split(',')]
    # df2_columns = [item + '_y' for item in df2.columns.to_list()]
    df2_columns = df2.columns.to_list()
    names_to_change = [x for x in key1_list if x in df2_columns]
    if len(names_to_change) > 0:
        rename_map = dict(zip(names_to_change, [name + '_2' for name in names_to_change]))
        df2.rename(columns=rename_map, inplace=True)
        rename_map = dict(zip(names_to_change, [name + '_1' for name in names_to_change]))
        df1.rename(columns=rename_map, inplace=True)
        key1_list = [name if name not in names_to_change else name + '_1' for name in key1_list]
        key2_list = [name if name not in names_to_change else name + '_2' for name in key2_list]
    df2_columns = df2.columns.to_list()
    df1.loc[:, 'concat_key'] = df1[key1_list].agg(' '.join, axis=1)
    df2.loc[:, 'concat_key'] = df2[key2_list].agg(' '.join, axis=1)
    fuzzy = fuzzy_merge(df1, df2, 'concat_key', 'concat_key')
    correct_match = fuzzy.loc[fuzzy['score'] >= threshold, key1_list+['matches']]
    incorrect_match = fuzzy.loc[fuzzy['score'] < threshold, key1_list+['matches', 'score']]
    df_merged = pd.merge(correct_match, df2, left_on='matches', right_on='concat_key')
    df_errors = pd.merge(incorrect_match, df2, left_on='matches', right_on='concat_key')
    final_columns_correct = key1_list + df2_columns
    final_columns_incorrect = final_columns_correct + ['score']
    df_merged = df_merged.loc[:, final_columns_correct]
    df_errors = df_errors.loc[:, final_columns_incorrect]
    match_count = len(df_merged.index)
    data_count = len(df1.index)
    return match_count, data_count, df_merged, df_errors