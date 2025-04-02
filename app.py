import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

EXCEL_FILE = "output_tables_cleaned.xlsx"
TABLE_INFO_FILE = "table_info.json"
RENAME_FILE = "table_renames.json"
STATIC_FOLDER = "static"

# Load table info
with open(TABLE_INFO_FILE, "r", encoding="utf-8") as f:
    TABLE_INFO = json.load(f)

# Load table renames
if os.path.exists(RENAME_FILE):
    with open(RENAME_FILE, "r", encoding="utf-8") as f:
        TABLE_RENAMES = json.load(f)
else:
    TABLE_RENAMES = {}

def get_valid_tables():
    excel_file = pd.ExcelFile(EXCEL_FILE)
    valid = []
    for sheet in excel_file.sheet_names:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine='openpyxl')
        if df.shape[0] > 1 and not df.applymap(lambda x: str(x).strip() == '').all().all():
            valid.append(sheet)
    return valid

def get_columns(sheet):
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine='openpyxl')
    df.columns = df.columns.str.strip().str.replace('\r', ' ').str.replace('\n', ' ')
    return df.columns.tolist()

@app.route("/", methods=["GET", "POST"])
def index():
    tables = get_valid_tables()
    columns = []
    plot_path = ""
    selected_table = request.form.get("table") or request.args.get("table")
    table_html = ""
    table_info = ""
    table_caption = ""
    renamed_table_name = ""

    if selected_table:
        columns = get_columns(selected_table)
        df = pd.read_excel(EXCEL_FILE, sheet_name=selected_table, engine='openpyxl')
        df.columns = df.columns.str.strip().str.replace('\r', ' ').str.replace('\n', ' ')
        table_html = df.to_html(index=False)
        table_info = TABLE_INFO.get(selected_table, {}).get("info", "")
        table_caption = TABLE_INFO.get(selected_table, {}).get("caption", "")
        renamed_table_name = TABLE_RENAMES.get(selected_table, "")
        renamed_table_name = TABLE_RENAMES.get(selected_table, "")
        original_caption = TABLE_INFO.get(selected_table, {}).get("caption", "")

        if renamed_table_name:
            table_caption = renamed_table_name
        else:
            table_caption = original_caption



        graph_type = request.form.get("graph_type")
        if graph_type == "heatmap":
            numeric_df = df.select_dtypes(include='number')
            if numeric_df.shape[1] < 2:
                plot_path = ""
                table_info += " ⚠️ (Not enough numeric columns for heatmap)"
            else:
                plt.figure(figsize=(8, 6))
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
                plt.title(f"{selected_table}: Heatmap")

                if not os.path.exists(STATIC_FOLDER):
                    os.makedirs(STATIC_FOLDER)
                plot_path = f"{STATIC_FOLDER}/{selected_table}_heatmap.png"
                plt.savefig(plot_path)
                plt.close()

        elif "x_col" in request.form and "y_col" in request.form:
            x_col = request.form.get("x_col")
            y_col = request.form.get("y_col")

            plt.figure(figsize=(6, 4))
            if graph_type == 'line':
                plt.plot(df[x_col], df[y_col], marker='o')
            elif graph_type == 'bar':
                plt.bar(df[x_col], df[y_col])
            elif graph_type == 'scatter':
                plt.scatter(df[x_col], df[y_col])

            plt.title(f"{selected_table}: {x_col} vs {y_col}")
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.grid(True)
            plt.tight_layout()

            if not os.path.exists(STATIC_FOLDER):
                os.makedirs(STATIC_FOLDER)
            plot_path = f"{STATIC_FOLDER}/{selected_table}_{x_col}_vs_{y_col}_{graph_type}.png"
            plt.savefig(plot_path)
            plt.close()

    return render_template("index.html", tables=tables, columns=columns,
                           selected_table=selected_table, plot=plot_path,
                           table_html=table_html, table_info=table_info,
                           table_caption=table_caption, renamed_table_name=renamed_table_name)

@app.route("/rename", methods=["POST"])
def rename_table():
    global TABLE_RENAMES
    table = request.form.get("table")
    new_name = request.form.get("new_name")
    if table and new_name:
        TABLE_RENAMES[table] = new_name
        with open(RENAME_FILE, "w", encoding="utf-8") as f:
            json.dump(TABLE_RENAMES, f, indent=2, ensure_ascii=False)
        flash(f"✅ Table name updated to: {new_name}", "success")
    return redirect(url_for('index', table=table))

if __name__ == "__main__":
    app.run(debug=True)
