from flash_excel.ui.api import FlashExcelAPI


def test_resolve_keeps_extension():
    result = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "keep", "folder": "./output/", "pattern": "{name}_clean"},
    )
    assert result.endswith("clients_clean.xlsx")


def test_resolve_changes_extension():
    result = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "csv", "folder": "./output/", "pattern": "{name}_clean"},
    )
    assert result.endswith("clients_clean.csv")


def test_resolve_custom_pattern():
    result = FlashExcelAPI._resolve_output_path(
        "/data/export_2024.xlsx",
        {"format": "keep", "folder": "/out/", "pattern": "processed_{name}"},
    )
    assert "processed_export_2024" in result


def test_resolve_output_format_returned():
    path, fmt = FlashExcelAPI._resolve_output_path(
        "/data/clients.xlsx",
        {"format": "parquet", "folder": "./out/", "pattern": "{name}"},
        return_fmt=True,
    )
    assert fmt == "parquet"
    assert path.endswith(".parquet")
