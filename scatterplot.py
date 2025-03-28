import pandas as pd
import matplotlib.pyplot as plt

file_path = "output_tables_cleaned.xlsx"

excel_file = pd.ExcelFile(file_path)  # No need to specify engine

for sheet in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
    
    # Skip empty sheets
    if df.empty:
        continue

    # Check for numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) < 2:
        continue

    x_col = numeric_cols[0]
    y_col = numeric_cols[1]

    plt.figure(figsize=(6, 4))
    plt.scatter(df[x_col], df[y_col])
    plt.title(f"{sheet}: {x_col} vs {y_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{sheet}_scatter.png")
    plt.close()

print("✅ Scatter plots saved successfully.")
