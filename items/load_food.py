import pandas as pd
from items.models import Food

def load_data():
    path = r"C:\Users\LSESH\OneDrive\Desktop\project\Food\Food\fooddb_3v.csv"

    df = pd.read_csv(path)

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna("")

    for _, row in df.iterrows():
        Food.objects.get_or_create(
            type=row['type'],
            item=row['item'],
            variant=row['variant'],
            defaults={
                'method': row['method'],
                'nutrients': row['nutrients'],
                'benefits': row['benefits'],
                'hazards': row['hazards']
            }
        )

    print("✅ fooddb_3v.csv loaded into SQLite")
