import sys
from cx_Freeze import setup,Executable

base=None

if(sys.platform=="win32"):

	base="Win32GUI"

	pass


executables=[Executable("envio_falta.py",base=base)]


setup(name="Teste",version="1.0",description="t",executables=executables)