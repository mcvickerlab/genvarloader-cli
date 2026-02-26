from importlib.metadata import version
from pathlib import Path

from cyclopts import App

app = App(
    help_on_error=True,
    version=f"[magenta]genvarloader[/magenta] {version('genvarloader')}"
    + f"\n[cyan]genvarloader-cli[/cyan] {version('genvarloader-cli')}",
    version_format="rich",
)


@app.default
@app.command
def write(
    output: Path,
    bed: Path,
    variants: Path | None = None,
    bigwig_table: Path | None = None,
    track_name: str | None = None,
    samples: list[str] | Path | None = None,
    max_jitter: int | None = None,
    overwrite: bool = False,
    max_mem: int | str = "1G",
    extend_to_length: bool = True,
):
    """Write a genvarloader dataset.

    Args:
        output: Path to the output dataset, should end with .gvl by convention.
        bed: Path to a BED6+ file specifying the regions to write.
        variants: Path to genetic variants, can be a VCF, PGEN, or SVAR file.
        bigwig_table: Path to a table containing sample names and paths to bigWig files for those samples.
            It must have columns "sample" and "path".
        track_name: Name of the track to write. If not provided, it will be the name of the bigwig table without the extension.
        samples: List of sample names to write. If not provided, all samples in the bigwig table will be written.
        max_jitter: Maximum jitter to add to the variants, in base pairs. Defaults to 0.
        overwrite: Overwrite the output dataset if it already exists.
        max_mem: Maximum memory to use for the dataset, in bytes. Defaults to 1GB. Can be a string like "1G" or "1000M".
        extend_to_length: Whether to continue reading/writing variants until all haplotypes have a length at least as
            long as the intervals in bed. Otherwise, deletions can cause the length of haplotypes to be less than the
            intervals in bed. This can be disabled if having haplotypes shorter than the intervals is acceptable, in which
            case they will be padded with reference bases when appropriate. Disabling this also reduces the amount of data
            read/written and is faster to run.
    """
    import genvarloader as gvl

    if bigwig_table is not None:
        if track_name is None:
            track_name = bigwig_table.stem
        bigwigs = gvl.BigWigs.from_table(track_name, bigwig_table)
    else:
        if track_name is not None:
            raise ValueError(
                f"Track name {track_name} provided but no bigwig table provided."
            )
        bigwigs = None

    if isinstance(samples, Path):
        with open(samples, "r") as f:
            samples = [line.strip() for line in f.readlines()]

    gvl.write(
        output,
        bed,
        variants,
        bigwigs,
        samples,
        max_jitter,
        overwrite,
        max_mem,
        extend_to_length,
    )


if __name__ == "__main__":
    app()
