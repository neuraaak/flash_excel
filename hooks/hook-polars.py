from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("polars")
datas_, binaries_, hiddenimports_ = collect_all("_polars_runtime_32")
datas += datas_
binaries += binaries_
hiddenimports += hiddenimports_
