import pandas as pd
import matplotlib.pyplot as plt

file_path = "output_tables_cleaned.xlsx"

# Load Excel file
excel_file = pd.ExcelFile(file_path)

for sheet in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
    
    # Skip empty sheets
    if df.empty:
        continue

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) < 2:
        continue  # Skip if less than 2 numeric columns

    x_col = numeric_cols[0]
    y_col = numeric_cols[1]

    plt.figure(figsize=(6, 4))
    plt.plot(df[x_col], df[y_col], marker='o')
    plt.title(f"{sheet}: {x_col} vs {y_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{sheet}_lineplot.png")
    plt.close()

print("✅ Line plots saved for all valid sheets.")
