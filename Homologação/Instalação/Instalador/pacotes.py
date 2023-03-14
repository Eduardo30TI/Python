import os
from glob import glob

class Pacote:

    def Instalador():

        temp_path=os.path.join(os.getcwd(),'*.txt')

        caminho=glob(temp_path)

        with open(caminho[-1],'r') as arq:
            
            for a in arq.readlines():

                try:

                    comando=a.strip().split()

                    comando=f'pip install --upgrade {comando[-1]}'
                    
                    os.system(a.strip())

                    os.system(comando)
                    
                    pass

                except:

                    continue

                pass

            pass

        pass

    pass