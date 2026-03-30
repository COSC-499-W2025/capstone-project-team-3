# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Electron backend sidecar (spaCy, KeyBERT, LaTeX-free API)."""
import os

from PyInstaller.utils.hooks import collect_all, copy_metadata


def _repo_root_containing_app_shared(spec_path: str) -> str:
    """
    Directory that contains app/shared (and app/sidecar_main.py).

    SPECPATH is often relative to the shell cwd; dirname(abspath(SPECPATH)) can then
    point at a parent folder (e.g. Desktop/COSC 499) instead of capstone-project-team-3.
    """
    start = os.path.dirname(os.path.abspath(spec_path))
    d = start
    for _ in range(12):
        if os.path.isdir(os.path.join(d, "app", "shared")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    try:
        for name in sorted(os.listdir(start)):
            sub = os.path.join(start, name)
            if os.path.isdir(sub) and os.path.isdir(os.path.join(sub, "app", "shared")):
                return sub
    except OSError:
        pass
    raise FileNotFoundError(
        "backend-sidecar.spec: cannot find app/shared (searched from %r). "
        "cd into the repository root (folder containing app/shared) and run: "
        "pyinstaller backend-sidecar.spec" % start
    )


_SPEC_DIR = _repo_root_containing_app_shared(SPECPATH)
_NLTK_DATA = os.path.join(
    _SPEC_DIR, "app", "utils", "non_code_analysis", "nltk_data"
)

_STATIC_DIR = os.path.join(_SPEC_DIR, "app", "static")
if not os.path.isdir(_STATIC_DIR):
    raise FileNotFoundError(
        "backend-sidecar.spec: app/static not found at %s" % _STATIC_DIR
    )
datas = [(_STATIC_DIR, "app/static")]
# Learning recommendations (learning_recommendations.CATALOG_PATH → _MEIPASS/app/data/...)
_CATALOG_JSON = os.path.join(_SPEC_DIR, 'app', 'data', 'course_catalog.json')
if os.path.isfile(_CATALOG_JSON):
    datas.append((_CATALOG_JSON, 'app/data'))
# Tree-sitter JSON + grammar .js: must land under _MEIPASS/app/shared/ (parse_code_utils._shared_package_dir).
# Dest must be "app/shared/..." — not "shared/..." (older grammar loop used relpath to app/ and broke frozen paths).
_SHARED_ROOT = os.path.join(_SPEC_DIR, 'app', 'shared')
_TS_REQUIRED_JSON = (
    'treesitter_import_keywords.json',
    'import_patterns_regex.json',
    'library.json',
    'language_mapping.json',
)
_SKIP_SHARED_DIRS = frozenset({'test_data', 'text'})
for _name in _TS_REQUIRED_JSON:
    _jp = os.path.join(_SHARED_ROOT, _name)
    if not os.path.isfile(_jp):
        raise FileNotFoundError(
            'backend-sidecar.spec: missing %s (required for tree-sitter / import analysis)' % _jp
        )
for _root, _dirnames, _filenames in os.walk(_SHARED_ROOT):
    _dirnames[:] = [d for d in _dirnames if d not in _SKIP_SHARED_DIRS]
    _rel = os.path.relpath(_root, _SHARED_ROOT)
    _dest = 'app/shared' if _rel in ('.', '') else os.path.join('app/shared', _rel).replace('\\', '/')
    for _f in _filenames:
        if _f.endswith('.pyc'):
            continue
        # Runtime needs JSON config + tree-sitter grammars (.js). Skip bundled Python samples.
        if _f.endswith('.py'):
            continue
        _abs = os.path.join(_root, _f)
        datas.append((_abs, _dest))
if os.path.isdir(_NLTK_DATA):
    datas.append((_NLTK_DATA, "nltk_data"))
binaries = []
# app.api_app / app.data.db imported inside `if __name__ == "__main__"` after SIDECAR_LISTENING.
hiddenimports = ['unicodedata', 'app.api_app', 'app.data.db']

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
    [os.path.join(_SPEC_DIR, 'app', 'sidecar_main.py')],
    pathex=[_SPEC_DIR],
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
