import os
from pathlib import Path

import click
import polars as pl

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "data" / "processed"
DATABASE_URL = os.environ["DATABASE_URL"]
QUERY = "SELECT * FROM analytics.orders_features;"


@click.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help="Local output directory to store the features dataframe.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force to overwrite the data previously stored.",
)
@click.pass_context
def save_df(ctx: click.Context, output_dir: Path, force: bool) -> None:

    file_name = "data_raw.parquet"
    file_path = output_dir / file_name

    if file_path.exists() and not force:
        click.secho(f"[INFO] Data already exists at {output_dir}", fg="yellow")
        ctx.exit(0)

    if not DATABASE_URL:
        click.secho(
            "[ERROR] DATABASE_URL environment variable is not set.", err=True, fg="red"
        )
        ctx.exit(1)

    try:
        click.secho("[INFO] Quering Data from DB ...", fg="blue")
        df = pl.read_database_uri(query=QUERY, uri=DATABASE_URL)
        click.secho("[INFO] Query completed successfully.", fg="green")

        output_dir.mkdir(parents=True, exist_ok=True)

        click.secho("[INFO] Writting parquet file ...", fg="blue")
        df.write_parquet(file=file_path, compression="zstd")
        click.secho("[INFO] Data saved successfully.", fg="green")

    except Exception as e:
        click.secho(f"[ERROR] An error has occurred: {e}", err=True, fg="red")
        ctx.exit(1)


if __name__ == "__main__":
    save_df()
