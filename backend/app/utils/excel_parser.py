# backend/app/utils/excel_parser.py
# Чтение Excel-выгрузки товаров из Битрикса.
# Ожидаемые колонки (на русском, регистр не важен): название/наименование,
# описание, артикул, цена, категория. Лишние колонки просто игнорируются.

from io import BytesIO
import pandas as pd

_COLUMN_MAP = {
    "название": "name",
    "наименование": "name",
    "описание": "description",
    "артикул": "sku",
    "цена": "price",
    "категория": "category",
}

_REQUIRED = ["name", "description", "sku", "price", "category"]


def parse_excel(file_bytes: bytes) -> list[dict]:
    df = pd.read_excel(BytesIO(file_bytes))
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns=_COLUMN_MAP)

    for col in _REQUIRED:
        if col not in df.columns:
            df[col] = 0.0 if col == "price" else ""

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    for col in ("name", "description", "sku", "category"):
        df[col] = df[col].fillna("").astype(str)

    # выкидываем строки без названия — явный мусор/пустые строки в файле
    df = df[df["name"].str.strip() != ""]

    return df[_REQUIRED].to_dict("records")
