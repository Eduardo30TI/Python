import os
from glob import glob


class Remover:

    def RemoverArquivo(filtro):

        filtro=(f'*{filtro}')

        temp_path=os.path.join(os.getcwd(),filtro)

        dados=glob(temp_path)

        for arq in dados:
            
            os.remove(arq)

        pass

    pass