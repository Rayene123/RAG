import pandas as pd

print("=" * 80)
print("UNDERSTANDING THE TARGET FIELD")
print("=" * 80)

# Load dataset
df = pd.read_csv('data/raw/application_train.csv')

print(f"\n📊 Dataset: application_train.csv")
print(f"   Total records: {len(df):,}")
print(f"\n🎯 TARGET Field Distribution:")
print(df['TARGET'].value_counts().sort_index())

target_0_pct = df[df['TARGET'] == 0].shape[0] / len(df) * 100
target_1_pct = df[df['TARGET'] == 1].shape[0] / len(df) * 100

print(f"\n   TARGET = 0: {df[df['TARGET']==0].shape[0]:,} clients ({target_0_pct:.1f}%)")
print(f"   TARGET = 1: {df[df['TARGET']==1].shape[0]:,} clients ({target_1_pct:.1f}%)")

print(f"\n💡 INTERPRETATION:")
print(f"   This is the 'Home Credit Default Risk' dataset from Kaggle")
print(f"   TARGET measures REPAYMENT OUTCOME (not loan acceptance)")
print(f"")
print(f"   TARGET = 0 → Client did NOT default → PAID BACK the loan ✅")
print(f"   TARGET = 1 → Client DID default → FAILED to pay back the loan ❌")
print(f"")
print(f"   Note: ~92% paid back successfully, ~8% defaulted")
print(f"   This is after loans were already APPROVED and given to clients")

print("\n" + "=" * 80)
print("CHECKING A SPECIFIC CLIENT")
print("=" * 80)

client_id = 104070
client = df[df['SK_ID_CURR'] == client_id]

if len(client) > 0:
    target = client['TARGET'].values[0]
    print(f"\nClient {client_id}:")
    print(f"   TARGET = {target}")
    if target == 0:
        print(f"   ✅ This client PAID BACK their loan successfully")
    else:
        print(f"   ❌ This client DEFAULTED (did not pay back)")
else:
    print(f"\nClient {client_id} not found in dataset")

print("\n" + "=" * 80)
