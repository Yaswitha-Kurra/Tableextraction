import camelot
import pandas as pd

def is_junk_table(df):
    # Check if table has only 1 row and header is numeric
    if df.shape[0] <= 1:
        header = df.iloc[0].tolist()
        if all(str(cell).strip().isdigit() for cell in header):
            return True
    # Table fully empty
    if df.applymap(lambda x: str(x).strip() == '').all().all():
        return True
    return False

# Read tables
tables = camelot.read_pdf("test1.pdf", pages='all', flavor='lattice')

valid_count = 0

with pd.ExcelWriter("output_tables_cleaned.xlsx") as writer:
    for i, table in enumerate(tables):
        df = table.df
        if not is_junk_table(df):
            # Take first row as header
            new_header = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df.columns = new_header
            valid_count += 1
            sheet_name = f"Table_{valid_count}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"{valid_count} valid tables extracted and saved with proper column names to 'output_tables_cleaned.xlsx'")
