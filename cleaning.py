import pandas as pd
import numpy as np
import re

df = pd.read_csv("/workspaces/amc-research-sprint-lh_gl/data/amcdata_weapons_facilities_V2.csv")

# clean extra spaces and capitalize
df['item'] = df['item'].str.strip().str.capitalize()

# delete all rows where item is 
df = df[df['item'].notna() & (df['item'] != '')]

# clean plurals
df['item'] = df['item'].str.replace(r's$', '', regex=True)

# clean 99 and N/A values
df.replace(['99', np.nan], '', inplace=True)

colunas_alvo = [
    'ban_development',
    'ban_testing',
    'ban_production',
    'ban_acquisition',
    'ban_possession',
    'ban_station',
    'ban_transfer',
    'ban_use',
    'ban_disposal',
    'restriction_development',
    'testing_restriction',       # note: inconsistent naming in the dataset
    'restriction_production',
    'restriction_acquisition',
    'restriction_possession',
    'restriction_transfer',
    'restriction_use',
    'restriction_disposal',
    'obligations_timeframe_type'
]
outras_colunas = [
    'agreement_id',
    'item_type',
    'item',
    'weapon_item_definition',
    'c_weapon_item_definition',
    'timeframe_set_time',
    'timeframe_other',
    'c_obligations_timeframe',
    'timeframe_phases',
    'c_timeframe_phases',
    'c_phases'
]

all_columns_to_keep = outras_colunas + colunas_alvo

df = df[all_columns_to_keep]

# merge descriptions of duplicates by item
def merge_unique_text(series):
    vals = series.replace('', pd.NA).dropna().unique()
    return ' | '.join(sorted(vals)) if len(vals) > 0 else ''

# Apply to both description columns
for col in ['weapon_item_definition', 'c_weapon_item_definition']:
    df[col] = df.groupby('item')[col].transform(merge_unique_text)

# 2. Use um loop para aplicar a lógica em cada uma delas
# for col in colunas_alvo:
#     # Garante que a coluna é numérica (limpeza inicial)
#     df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
#     # Cria a máscara específica para esta coluna
#     mask = df.groupby('item')[col].transform('nunique') > 1
    
#     # Aplica a transformação apenas na coluna atual do loop
#     df.loc[mask, col] = 1

# specific adjust for timeframe since it might imply multiple phases -> adjusts to higher n of phases
# timeframe_phases_mask = df.groupby('item')['timeframe_phases'].transform('nunique') > 1
# df.loc[timeframe_phases_mask, 'timeframe_phases'] = 2

# splitting the dataset to keep all agreements
df['agreement_id'] = df['agreement_id'].astype(str)
df['agreement_id'] = df.groupby('item')['agreement_id'].transform(
    lambda x: ';'.join(sorted(x.replace('', pd.NA).dropna().astype(str).unique()))
)

df = df.drop_duplicates(subset=['item'], keep='first')

df['agreement_id'] = df['agreement_id'].str.split(';')
df_exploded = df.explode('agreement_id')
df_exploded['agreement_id'] = df_exploded['agreement_id'].str.strip()

df_exploded.to_excel('duplicates_result.xlsx', index=False)