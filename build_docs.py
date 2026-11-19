"""Build document PDFs; run in the package root: python3 -B build_docs.py.

Requires Pandoc, XeLaTeX with xeCJK, DejaVu Serif/Sans Mono and Noto Serif CJK JP.
After rebuilding, regenerate MANIFEST.sha256 over all files except itself:
  python3 -B - <<'END'
  import hashlib
  from pathlib import Path
  p = Path('.')
  files = sorted(f for f in p.rglob('*') if f.is_file() and f.name != 'MANIFEST.sha256' and '.git' not in f.parts)
  (p/'MANIFEST.sha256').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.as_posix()+'\n' for f in files))
  END
Use -B and avoid build/cache files inside this directory. Then run verify.py.
"""
import hashlib
import os
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Stable PDF timestamps for identical Markdown and the same toolchain.
ENV = dict(os.environ, SOURCE_DATE_EPOCH='1793836800', FORCE_SOURCE_DATE='1')
COMMON = ['pandoc', '--standalone', '--pdf-engine=xelatex', '-V', 'geometry:margin=22mm',
          '-V', 'mainfont:DejaVu Serif', '-V', 'monofont:DejaVu Sans Mono',
          '-V', 'CJKmainfont:Noto Serif CJK JP', '-V', 'fontsize:10pt', '-V', 'colorlinks:true']
for sources, output in [(['README.md', 'PROOF.md', 'VERIFICATION-RECORD.md', 'SOURCES.md', 'CHANGELOG.md'], 'PACKAGE.pdf'),
                        (['README.ja.md'], 'README.ja.pdf')]:
    # xdvipdfmx otherwise derives a trailer ID from a temporary path.
    identity = hashlib.sha256(b''.join((ROOT / name).read_bytes() for name in sources)
                              + Path(__file__).read_bytes()).hexdigest()[:32]
    with tempfile.TemporaryDirectory(prefix='dp-docs-') as tmp:
        header = Path(tmp) / 'identity.tex'
        header.write_text('\\special{pdf:trailerid [<' + identity + '><' + identity + '>]}\n')
        subprocess.run([*COMMON, '--include-in-header', str(header), *sources, '-o', output],
                       cwd=ROOT, env=ENV, check=True)
    print(output, flush=True)
