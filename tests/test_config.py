from flash_excel.config import load_app_config, save_app_config


def test_load_app_config_defaults_locale(monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    result = load_app_config()
    assert result["locale"] == "en"


def test_save_and_reload_locale(monkeypatch, tmp_path):
    cfg_file = tmp_path / "app.config.yaml"
    monkeypatch.setattr("flash_excel.config.APP_CONFIG", cfg_file)
    save_app_config("blue-gray", "dark", "fr")
    result = load_app_config()
    assert result["locale"] == "fr"
