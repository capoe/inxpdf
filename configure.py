#! /usr/bin/env python
import os
pypath = os.path.join(os.getcwd())
path = os.path.join(os.getcwd(), "bin")
ofs = open('./bin/INXPDFRC', 'w')
ofs.write('''\
#! /bin/bash
export PYTHONPATH="${{PYTHONPATH}}:{pypath:s}"
export PATH="${{PATH}}:{path:s}"
'''.format(pypath=pypath, path=path))
ofs.close()
