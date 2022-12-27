from Interface import Interface
import os
import shutil

submenu=['CxFreeze','PyInstaller','Py2Exe','Nuitka','ZipFile','RemoverPasta']

programas={'CxFreeze':'pip install cx-Freeze','PyInstaller':'pip install pyinstaller','Py2Exe':'pip install py2exe','Nuitka':'pip install Nuitka','ZipFile':'pip install zipfile36','shutil':'pip install pytest-shutil'}

def Instalador(**kwargs):

    temp_dict=kwargs['kwargs']

    for programa in temp_dict.values():

        try:

            os.system(programa)

            programa=programa.split()

            programa=f'pip install --upgrade {programa[-1]}'

            os.system(programa)

            pass

        except:

            continue

        pass

    pass

def Main():
    
    os.system('cls')

    Interface.Titulo('Menu',50,50)

    retorno=Interface.Menu(submenu)

    Interface.Titulo(linha=50)

    globals().get(retorno)()

    resp=Interface.Retorno('Deseja executar o programa novamente?[s/n]: ')

    if(resp):

        Main()

        pass

    pass

def CxFreeze():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        temp=[]

        for arq in os.listdir(caminho):

            if(arq!='main.py'):

                continue

            temp.append(arq)

            pass

        if(len(temp)>0):

            retorno=Interface.Menu(temp)

            os.chdir(caminho)

            os.system(f'cxfreeze {retorno}')

            pass

        pass

    except Exception as erro:

        print('Erro: {}'.format(erro))

        pass

    pass

def Py2Exe():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        temp=[]

        for arq in os.listdir(caminho):

            if(arq!='main.py'):

                continue

            temp.append(arq)

            pass

        if(len(temp)>0):

            retorno=Interface.Menu(temp)

            os.chdir(caminho)

            with open('setup.py','w') as arq:

                arq.writelines('from distutils.core import setup\nimport py2exe\n\nsetup(console=["{0}"])'.format(retorno))

                pass

            os.system(f'python setup.py py2exe')

            RemoverArquivo(caminho,'setup.py')

            pass

        pass

    except Exception as erro:

        print('Erro: {}'.format(erro))

        pass    

    pass

def Nuitka():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        temp=[]

        for arq in os.listdir(caminho):

            if(arq!='main.py'):

                continue

            temp.append(arq)

            pass

        if(len(temp)>0):

            retorno=Interface.Menu(temp)

            os.chdir(caminho)

            resp=Interface.Retorno('Seja inserir um ícone?[s/n]: ')

            if(resp):

                path_base=''

                while path_base=='':

                    path_base=input('Informe o caminho da imagem: ')

                    pass

                temp=[]
                
                for arq in os.listdir(path_base):
                    
                    temp.append(arq)

                    pass

                imagem=Interface.Menu(temp)

                origem=os.path.join(path_base,imagem)

                destino=os.path.join(caminho,imagem)

                shutil.move(origem,destino)
                
                os.system(f'python -m nuitka --onefile --windows-icon-from-ico={imagem} {retorno}')

                pass

            else:

                os.system(f'python -m nuitka --onefile {retorno}')

                pass

            pass

        pass

    except Exception as erro:

        print('Erro: {}'.format(erro))

        pass    


    pass

def PyInstaller():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        temp=[]

        for arq in os.listdir(caminho):

            if(arq!='main.py'):

                continue

            temp.append(arq)

            pass

        if(len(temp)>0):

            retorno=Interface.Menu(temp)

            os.chdir(caminho)

            resp=Interface.Retorno('Seja inserir um ícone?[s/n]: ')

            if(resp):

                path_base=''

                while path_base=='':

                    path_base=input('Informe o caminho da imagem: ')

                    pass

                temp=[]
                
                for arq in os.listdir(path_base):
                    
                    temp.append(arq)

                    pass

                imagem=Interface.Menu(temp)

                origem=os.path.join(path_base,imagem)

                destino=os.path.join(caminho,imagem)

                shutil.copy(origem,destino)
                
                os.system(f'pyinstaller --onefile --icon="{imagem}" --add-data="{imagem};." {retorno}')

                pass

            else:

                os.system(f'pyinstaller --onefile {retorno}')

                pass

            pass

        pass

    except Exception as erro:

        print('Erro: {}'.format(erro))

        pass        

    pass

def RemoverArquivo(caminho,filtro):

    for arq in os.listdir(caminho):

        if(arq!=filtro):
            
            continue

        os.remove(arq)

        pass

    pass

def ZipFile():

    try:

        caminho=''

        while caminho=='':

            caminho=input('Informe o caminho: ')

            pass

        temp=[]

        for pasta in os.listdir(caminho):

            if(pasta.find('.')>0):

                continue

            temp.append(pasta)

            pass


        retorno=Interface.Menu(temp)

        arq=os.path.basename(caminho)

        os.chdir(caminho)

        shutil.make_archive(arq,'zip',f'{retorno}')

        pass


    except Exception as erro:

        print('Erro: {0}'.format(erro))

        pass

    pass

def RemoverPasta():

    try:

        caminho=input('Informe o caminho do arquivo: ')

        temp=[]

        for arq in os.listdir(caminho):

            if(arq.find('.')>=0):

                continue

            temp.append(arq)

            pass

        res=Interface.Menu(temp)

        temp_path=os.path.join(caminho,res)

        shutil.rmtree(temp_path)

        print('Pasta excluída com sucesso!')
        
        pass

    except Exception as erro:

        print(f'Erro: {erro}')

        pass

    pass

if __name__=='__main__':

    Instalador(kwargs=programas)
        
    Main()

    pass