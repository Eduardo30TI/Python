import sys
from cx_Freeze import setup,Executable

base=None

if(sys.platform=="Win32"):
	base="Win32GUI"
	pass

executables=[Executable("executador.py",base=base)]

setup(name="Compilador Python",version="1.0",description="Executador de script python",executables=executables)