import pathlib, pefile, sys
root = pathlib.Path(sys.argv[1]); src = pefile.PE(str(root / 'PySide6' / (sys.argv[2] if len(sys.argv) > 2 else 'QtCore.pyd')))
for dep in src.DIRECTORY_ENTRY_IMPORT:
    name = dep.dll.decode(); hits = list(root.rglob(name))
    if not hits: continue
    dst = pefile.PE(str(hits[0])); exports = {x.name for x in dst.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
    missing = [x.name.decode(errors='replace') for x in dep.imports if x.name and x.name not in exports]
    print(name, str(hits[0]), 'missing', len(missing), missing[:3])
