# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Electron backend sidecar (spaCy, KeyBERT, LaTeX-free API)."""
import os

from PyInstaller.utils.hooks import collect_all, copy_metadata

_SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH))
_NLTK_DATA = os.path.join(
    _SPEC_DIR, "app", "utils", "non_code_analysis", "nltk_data"
)

datas = [('app/static', 'app/static')]
# Tree-sitter / parse_code_utils JSON (namespace package breaks importlib.resources.open in frozen app)
for _json in (
    'treesitter_import_keywords.json',
    'import_patterns_regex.json',
    'library.json',
    'language_mapping.json',
):
    _jp = os.path.join(_SPEC_DIR, 'app', 'shared', _json)
    if os.path.isfile(_jp):
        datas.append((_jp, 'app/shared'))
# Grammar .js files for extract_rule_names (same cwd issue as JSON; not auto-collected)
_GRAMMARS = os.path.join(_SPEC_DIR, "app", "shared", "grammars")
_APP_ROOT = os.path.join(_SPEC_DIR, "app")
if os.path.isdir(_GRAMMARS):
    for _root, _, _files in os.walk(_GRAMMARS):
        for _f in _files:
            if not _f.endswith(".js"):
                continue
            _abs = os.path.join(_root, _f)
            _dest = os.path.relpath(_root, _APP_ROOT).replace(os.sep, "/")
            datas.append((_abs, _dest))
if os.path.isdir(_NLTK_DATA):
    datas.append((_NLTK_DATA, "nltk_data"))
binaries = []
hiddenimports = ['unicodedata']

# Distribution metadata (importlib.metadata) — required by transformers / tqdm at runtime
for _pkg in (
    'tqdm',
    'keybert',
    'transformers',
    'sentence-transformers',
    'tokenizers',
    'huggingface-hub',
    'filelock',
    'regex',
    'requests',
    'packaging',
    'numpy',
):
    try:
        datas += copy_metadata(_pkg)
    except Exception:
        pass
tmp_ret = collect_all('pygount')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('en_core_web_sm')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('thinc')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('spacy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('keybert')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sentence_transformers')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('transformers')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['app/sidecar_main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend-sidecar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX often breaks or strips macOS dylibs; leaves _internal without libpython*.dylib.
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='backend-sidecar',
)
