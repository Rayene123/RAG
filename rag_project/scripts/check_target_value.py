import pandas as pd

# Check Client 104070 TARGET value across all files
print("=" * 80)
print("CHECKING CLIENT 104070 TARGET VALUE")
print("=" * 80)

# Raw data
try:
    df_raw = pd.read_csv('data/raw/application_train.csv')
    client_raw = df_raw[df_raw['SK_ID_CURR'] == 104070]
    if len(client_raw) > 0:
        print(f"\n📁 application_train.csv (RAW):")
        print(f"   TARGET = {client_raw['TARGET'].values[0]}")
    else:
        print(f"\n📁 application_train.csv: Client NOT FOUND")
except Exception as e:
    print(f"\n❌ Error reading application_train.csv: {e}")

# Merged data
try:
    df_merged = pd.read_csv('data/processed/merged_data.csv')
    client_merged = df_merged[df_merged['SK_ID_CURR'] == 104070]
    if len(client_merged) > 0:
        print(f"\n📁 merged_data.csv (AFTER MERGE):")
        print(f"   TARGET = {client_merged['TARGET'].values[0]}")
    else:
        print(f"\n📁 merged_data.csv: Client NOT FOUND")
except Exception as e:
    print(f"\n❌ Error reading merged_data.csv: {e}")

# Preprocessed data
try:
    df_preprocessed = pd.read_csv('data/processed/features_for_rag.csv')
    client_preprocessed = df_preprocessed[df_preprocessed['SK_ID_CURR'] == 104070]
    if len(client_preprocessed) > 0:
        print(f"\n📁 features_for_rag.csv (AFTER PREPROCESSING):")
        print(f"   TARGET = {client_preprocessed['TARGET'].values[0]}")
    else:
        print(f"\n📁 features_for_rag.csv: Client NOT FOUND")
except Exception as e:
    print(f"\n❌ Error reading features_for_rag.csv: {e}")

# Sampled data
try:
    df_sampled = pd.read_csv('data/processed/features_for_rag_sampled.csv')
    client_sampled = df_sampled[df_sampled['SK_ID_CURR'] == 104070]
    if len(client_sampled) > 0:
        print(f"\n📁 features_for_rag_sampled.csv (SAMPLED 10K):")
        print(f"   TARGET = {client_sampled['TARGET'].values[0]}")
    else:
        print(f"\n📁 features_for_rag_sampled.csv: Client NOT FOUND (not in sample)")
except Exception as e:
    print(f"\n❌ Error reading features_for_rag_sampled.csv: {e}")

# Text descriptions
try:
    df_text = pd.read_csv('data/processed/client_texts_for_embedding.csv')
    client_text = df_text[df_text['SK_ID_CURR'] == 104070]
    if len(client_text) > 0:
        print(f"\n📁 client_texts_for_embedding.csv (TEXT CONVERSION):")
        print(f"   TARGET = {client_text['TARGET'].values[0]}")
        text_desc = client_text['text_description'].values[0]
        if 'DEFAULT RISK' in text_desc:
            print(f"   Label in text: DEFAULT RISK")
        elif 'GOOD STANDING' in text_desc:
            print(f"   Label in text: GOOD STANDING")
    else:
        print(f"\n📁 client_texts_for_embedding.csv: Client NOT FOUND")
except Exception as e:
    print(f"\n❌ Error reading client_texts_for_embedding.csv: {e}")

print("\n" + "=" * 80)
