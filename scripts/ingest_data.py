import os
from pathlib import Path
from typing import Dict, List, LiteralString, cast

import polars as pl
import psycopg
from psycopg import sql

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_DIR = BASE_DIR / "sql" / "ingestion"
DATA_DIR = BASE_DIR / "data" / "raw"
DATABASE_URL = os.environ["DATABASE_URL"]


def is_table_populated(conn_url: str, schema_name: str, table_name: str) -> bool:
    query = sql.SQL("SELECT EXISTS (SELECT 1 FROM {}.{} LIMIT 1);").format(
        sql.Identifier(schema_name), sql.Identifier(table_name)
    )
    try:
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                res = cursor.fetchone()
                return res[0] if res else False
    except Exception:
        return False


def ingest_data(
    table_name: str, data_path: Path, query_path: Path, conn_url: str
) -> None:
    if is_table_populated(conn_url, "olist", table_name):
        print(f"[INFO] The relation 'olist.{table_name}' has data, skipping")
        return

    print(f"[INFO] Ingesting data from {data_path.name} to olist.{table_name}...")
    df = pl.read_parquet(data_path)
    query_str = load_query(query_path)

    try:
        with psycopg.connect(conn_url) as conn:
            with conn.cursor() as cursor:
                query_str = cast(LiteralString, query_str)
                with cursor.copy(statement=sql.SQL(query_str)) as copy:
                    for row in df.iter_rows():
                        copy.write_row(row)
            conn.commit()
        print(
            f"[SUCCESS] Data ingestion completed succesfully for relation olist.{table_name}."
        )

    except Exception as e:
        print(f"[ERROR] Fail in data ingestion for '{table_name}': {e}")


def get_files(base_dir: Path) -> Dict[str, Path]:
    files = list(base_dir.glob("*"))
    if not files:
        raise FileNotFoundError(f"File not found at '{base_dir}'")

    ext = files[0].suffix.lower()

    if ext == ".sql":
        return get_table_from_query_path(files)
    elif ext == ".parquet":
        return get_table_from_data_path(files)
    else:
        raise ValueError(f"File extension not supported '{ext}'. Use .parquet or .sql")


def get_table_from_data_path(files: List[Path]) -> Dict[str, Path]:
    table_paths = {}
    for file in files:
        name = file.stem.replace("olist_", "").replace("_dataset", "")
        if name == "product_category_name_translation":
            name = "category_translation"
        elif name == "order_payments":
            name = "payments"
        table_paths[name] = file

    return table_paths


def get_table_from_query_path(files: List[Path]) -> Dict[str, Path]:
    return {file.stem: file for file in files}


def load_query(path: Path) -> str:
    if path.suffix.lower() != ".sql":
        raise ValueError(f"File '{path}' does not have extension .sql")
    return path.read_text(encoding="utf-8")


def main():
    data_files = get_files(DATA_DIR)
    query_files = get_files(QUERIES_DIR)

    for table_name, data_path in data_files.items():
        if table_name in query_files:
            query_path = query_files[table_name]
            ingest_data(table_name, data_path, query_path, DATABASE_URL)
        else:
            print(f"[WARNING] No SQL query for '{table_name}'")


if __name__ == "__main__":
    main()
