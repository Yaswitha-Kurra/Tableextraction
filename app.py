import matplotlib
matplotlib.use('Agg')  # To avoid MacOS GUI errors

from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

EXCEL_FILE = "output_tables_cleaned.xlsx"
STATIC_FOLDER = "static"

# Function to get valid tables
def get_valid_tables():
    excel_file = pd.ExcelFile(EXCEL_FILE)
    valid = []
    for sheet in excel_file.sheet_names:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine='openpyxl')
        if df.shape[0] > 1 and not df.applymap(lambda x: str(x).strip() == '').all().all():
            valid.append(sheet)
    return valid

# Function to get cleaned column names
def get_columns(sheet):
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine='openpyxl')
    df.columns = df.columns.str.strip().str.replace('\r', ' ').str.replace('\n', ' ')
    return df.columns.tolist()

# Route
@app.route("/", methods=["GET", "POST"])
def index():
    tables = get_valid_tables()
    columns = []
    plot_path = ""
    selected_table = None
    table_html = ""

    if request.method == "POST":
        selected_table = request.form.get("table")

        if selected_table:
            columns = get_columns(selected_table)

            # Load dataframe & clean headers
            df = pd.read_excel(EXCEL_FILE, sheet_name=selected_table, engine='openpyxl')
            df.columns = df.columns.str.strip().str.replace('\r', ' ').str.replace('\n', ' ')
            table_html = df.to_html(index=False)

        if "x_col" in request.form and "y_col" in request.form and "graph_type" in request.form:
            x_col = request.form.get("x_col")
            y_col = request.form.get("y_col")
            graph_type = request.form.get("graph_type")

            df = pd.read_excel(EXCEL_FILE, sheet_name=selected_table, engine='openpyxl')
            df.columns = df.columns.str.strip().str.replace('\r', ' ').str.replace('\n', ' ')

            # Create the plot based on the selected graph type
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

            # Save plot
            if not os.path.exists(STATIC_FOLDER):
                os.makedirs(STATIC_FOLDER)
            plot_path = f"{STATIC_FOLDER}/{selected_table}_{x_col}_vs_{y_col}_{graph_type}.png"
            plt.savefig(plot_path)
            plt.close()

            return render_template("index.html", tables=tables, columns=columns,
                                   selected_table=selected_table, plot=plot_path, table_html=table_html)

        return render_template("index.html", tables=tables, columns=columns, selected_table=selected_table, table_html=table_html)

    return render_template("index.html", tables=tables, columns=columns)

if __name__ == "__main__":
    app.run(debug=True)
