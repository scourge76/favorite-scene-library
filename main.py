# -*- coding: utf-8 -*-
import os
import sys

ADDON_PATH = os.path.dirname(__file__)
LIB_PATH = os.path.join(ADDON_PATH, "resources", "lib")
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

from fsl.router import run

if __name__ == "__main__":
    run()
