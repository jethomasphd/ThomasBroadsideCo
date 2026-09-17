"""Keep retired branding out of current text and decoded email deliverables."""
from pathlib import Path
from email import policy
from email.parser import BytesParser
import re
import subprocess
import unittest

ROOT=Path(__file__).resolve().parent.parent
RETIRED=re.compile(r'build(?:\s|<br\s*/?>|\\n)+something(?:\s|<br\s*/?>|\\n)+that(?:\s|<br\s*/?>|\\n)+lasts',re.I)

class BrandLanguage(unittest.TestCase):
    def test_current_text_and_email(self):
        paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
        for rel in filter(None,paths):
            path=ROOT/rel
            if not path.exists():continue
            if path.suffix=='.eml':
                msg=BytesParser(policy=policy.default).parsebytes(path.read_bytes())
                content='\n'.join(part.get_content() for part in msg.walk() if part.get_content_type() in ('text/plain','text/html'))
            elif path.suffix in ('.html','.md','.txt','.py','.js','.json','.liquid','.svg','.vtt','.srt'):
                content=path.read_text(encoding='utf-8')
            else:continue
            self.assertIsNone(RETIRED.search(content),rel)

if __name__=='__main__':unittest.main()
