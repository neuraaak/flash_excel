import polars as pl
import pytest

from flash_excel.io.writer import write_dataframe


@pytest.fixture
def sample_df():
    return pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})


def test_write_dataframe_xlsx(sample_df, tmp_path):
    out = tmp_path / "out.xlsx"
    write_dataframe(sample_df, out, "xlsx")
    assert out.exists()


def test_write_dataframe_csv(sample_df, tmp_path):
    out = tmp_path / "out.csv"
    write_dataframe(sample_df, out, "csv")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "a" in content


def test_write_dataframe_parquet(sample_df, tmp_path):
    out = tmp_path / "out.parquet"
    write_dataframe(sample_df, out, "parquet")
    assert out.exists()


def test_write_dataframe_creates_parent_dir(sample_df, tmp_path):
    out = tmp_path / "nested" / "dir" / "out.xlsx"
    write_dataframe(sample_df, out, "xlsx")
    assert out.exists()


def test_write_dataframe_unknown_fmt_raises(sample_df, tmp_path):
    out = tmp_path / "out.xyz"
    with pytest.raises(ValueError, match="Unsupported format"):
        write_dataframe(sample_df, out, "xyz")
