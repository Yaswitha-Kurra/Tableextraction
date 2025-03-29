import pandas as pd
import matplotlib.pyplot as plt

file_path = "output_tables_cleaned.xlsx"

def is_valid_table(df):
    # Consider valid if it has 2+ rows and meaningful content
    if df.shape[0] < 2:
        return False
    if df.applymap(lambda x: str(x).strip() == '').all().all():
        return False
    return True

# Load Excel
excel_file = pd.ExcelFile(file_path)

# Collect valid tables
valid_tables = []
for sheet in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
    if is_valid_table(df):
        valid_tables.append((sheet, df))

# Show valid table list
print("\n📄 Valid Tables Found:")
for i, (sheet, _) in enumerate(valid_tables):
    print(f"{i}: {sheet}")

# Ask user to choose a table
try:
    table_idx = int(input("\nEnter index of table to plot: "))
    selected_sheet, selected_df = valid_tables[table_idx]
except (ValueError, IndexError):
    print("❌ Invalid selection. Exiting...")
    exit()

# Show available columns
print(f"\n✅ Selected Table → {selected_sheet}")
print("Available columns:")
for idx, col in enumerate(selected_df.columns):
    print(f"{idx}: {col}")

try:
    x_idx = int(input("Enter index of column to use as X-axis: "))
    y_idx = int(input("Enter index of column to use as Y-axis: "))
except ValueError:
    print("❌ Invalid input. Exiting...")
    exit()

try:
    x_col = selected_df.columns[x_idx]
    y_col = selected_df.columns[y_idx]
except IndexError:
    print("❌ Column index out of range. Exiting...")
    exit()

# Plot
plt.figure(figsize=(6, 4))
plt.plot(selected_df[x_col], selected_df[y_col], marker='o')
plt.title(f"{selected_sheet}: {x_col} vs {y_col}")
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True)
plt.tight_layout()
filename = f"{selected_sheet}_{x_col}_vs_{y_col}_lineplot.png"
plt.savefig(filename)
plt.close()

print(f"\n✅ Line plot saved: {filename}")
