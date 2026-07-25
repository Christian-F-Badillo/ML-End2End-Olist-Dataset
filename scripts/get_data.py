from pathlib import Path

import click
import kagglehub
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"


def process_and_convert_to_parquet(downloaded_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for csv_file in downloaded_dir.glob("*.csv"):
        parquet_filename = f"{csv_file.stem}.parquet"
        dest_parquet = output_dir / parquet_filename

        if not dest_parquet.exists():
            df = pl.read_csv(csv_file, try_parse_dates=True)
            df.write_parquet(dest_parquet, compression="snappy")


@click.command()
@click.option(
    "--dataset",
    default="olistbr/brazilian-ecommerce",
    help="Dataset ID from Kaggle (e.g. user/dataset).",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help="Local output directory to store the dataset.",
)
@click.pass_context
def download_dataset(ctx: click.Context, dataset: str, output_dir: Path):

    if output_dir.exists() and any(output_dir.glob("*.parquet")):
        click.secho(f"[INFO] Data already exists at '{output_dir}'", fg="yellow")
        ctx.exit(0)

    output_dir.mkdir(parents=True, exist_ok=True)
    click.secho(f"[INFO] Downloading dataset: {dataset}...", fg="cyan")

    try:
        downloaded_path = kagglehub.dataset_download(dataset)
        downloaded_dir = Path(downloaded_path)

        click.secho("[INFO] Converting data to parquet format...", fg="blue")
        process_and_convert_to_parquet(downloaded_dir, output_dir)

        click.secho(f"[INFO] Dataset saved at: {output_dir.resolve()}", fg="green")

    except Exception as e:
        click.secho(
            f"[ERROR] Error during download/conversion: {e}", fg="red", err=True
        )
        ctx.exit(1)


if __name__ == "__main__":
    download_dataset()
