"""
main.py - Application's starting and ending points.
Copyright (C) 2019, 2020  ache2014

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ache2014@gmail.com
"""

import os
import sys

import logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
FH_PATH = 'logs/main.log'
if not os.path.exists(FH_PATH):
        os.makedirs(os.path.dirname(FH_PATH), exist_ok=True)
fh = logging.FileHandler(FH_PATH)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2.QtGui import QIcon
from mainwindow import MainWindow


if __name__ == "__main__":
    appctxt = ApplicationContext()
    
    window = MainWindow(appctxt=appctxt)
    window.show()
    
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
