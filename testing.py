import camelot
import pdfplumber
import pandas as pd
import json
import re

def is_junk_table(df):
    if df.shape[0] <= 1:
        header = df.iloc[0].tolist()
        if all(str(cell).strip().isdigit() for cell in header):
            return True
    if df.applymap(lambda x: str(x).strip() == '').all().all():
        return True
    return False

tables = camelot.read_pdf("test1.pdf", pages='all', flavor='lattice')
valid_count = 0
table_info_dict = {}

with pd.ExcelWriter("output_tables_cleaned.xlsx") as writer, pdfplumber.open("test1.pdf") as pdf:
    for i, table in enumerate(tables):
        df = table.df
        if not is_junk_table(df):
            new_header = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df.columns = new_header
            valid_count += 1
            sheet_name = f"Table_{valid_count}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Extract proper caption logic
            page_num = table.page - 1
            page = pdf.pages[page_num]
            top, left, bottom, right = table._bbox

            full_text = page.extract_text() or ""
            caption = "No caption found."
            info_text = ""

            if full_text:
                lines = full_text.split("\n")
                for line in lines:
                    line_clean = line.strip()
                    if re.match(r"(?i)table\s*\d+", line_clean):
                        # Check Y-position to ensure it's before table
                        words = page.extract_words()
                        for word in words:
                            if line_clean.startswith(word["text"]) and float(word["top"]) < top:
                                caption = line_clean
                                break

                # For info, grab all text except caption
                info_lines = [l for l in lines if l.strip() != caption]
                info_text = " ".join(info_lines)

            table_info_dict[sheet_name] = {
                "info": info_text if info_text else "No additional information found.",
                "caption": caption
            }

with open("table_info.json", "w", encoding="utf-8") as f:
    json.dump(table_info_dict, f, indent=2, ensure_ascii=False)

print(f"{valid_count} valid tables extracted.")
print("Table information & captions saved to 'table_info.json'.")
