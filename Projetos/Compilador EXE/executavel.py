import os
import shutil
import getpass
import datetime

tipo_executavel={1:'PyInstaller',2:'CxFreeze',3:'ExecutarScript',4:'Nuitka',5:'Py2Exe'}

def Main():

    os.system('cls')

    ano=str(datetime.datetime.today().year)

    mes=str(datetime.datetime.today().month)

    dia=str(datetime.datetime.today().day)

    if(len(ano)==1):

        ano=(f'0{ano}')

        pass

    elif(len(mes)==1):

        mes=(f'0{mes}')

        pass

    elif(len(dia)==1):

        dia=(f'0{dia}')

        pass

    data=(f'{dia}/{mes}/{ano}')

    usuario=getpass.getuser()

    Texto(titulo='menu',espaco=50,centralizar=True)

    Texto(titulo=f'hoje é {data}',espaco=50,centralizar=True)

    Texto(titulo=f'usuário logado é {usuario}',linha=50,espaco=50,centralizar=True)

    for i,menu in tipo_executavel.items():

        print('{0}) {1}'.format(i,menu))

        pass

    opc=''

    while not opc in tipo_executavel.keys():

        opc=input('Escolha uma das opções acima: ')

        if(opc.isnumeric()==True):

            opc=int(opc)

            if(opc in tipo_executavel.keys()):

                break

            pass

        pass

    tipo=tipo_executavel[opc]

    globals().get(tipo)()

    resp=Retorno('Deseja executar o programa novamente?[s/n]: ')

    if(resp=='s'):

        Main()

        pass

    else:

        print('Processo finalizado!')

        pass

    pass

def Texto(titulo='',linha=0,espaco=0,centralizar=False):

    titulo=str(titulo).capitalize()

    if(centralizar==True):

        if(linha==0):

            print('{0:^{1}}'.format(titulo,espaco))

            pass

        else:

            print('{0:^{1}}'.format(titulo,espaco))

            print('-'*linha)

            pass

        pass

    elif(centralizar==False and titulo!=''):

        if(linha==0):

            print('{0:^{1}}'.format(titulo,espaco))

            pass

        else:

            print('{0:^{1}}'.format(titulo,espaco))

            print('-'*linha)

            pass

        pass

    else:

        print('-'*linha)

        pass

    pass

def Retorno(texto):

    opcao=['s','n']

    resp=''

    while not resp in opcao:

        resp=input(texto).lower()

        if(resp in opcao):

            break

        pass

    return resp

    pass

def PyInstaller():

    try:

        Texto(linha=50)

        caminho=input('Informe o caminho onde está o executável: ')

        temp=dict()

        codigo=0

        for lista in os.listdir(caminho):

            if(lista=='main.py'):

                codigo+=1

                print('{0}) {1}'.format(codigo,lista))

                temp[codigo]=lista

                pass

            pass
        
        opc=''

        while not opc in temp.keys():

            opc=input('Escolha uma das opções acima: ')

            if(opc.isnumeric()==True):

                opc=int(opc)

                if(opc in temp.keys()):

                    break

                pass

            pass

        arquivo=temp[opc]

        os.chdir(caminho)

        path_name=input('Informe o nome da pasta: ')

        if(path_name==''):

            nome=str(arquivo).capitalize()

            nome=nome[:nome.find('.')]

            path_name=nome
            
            pass

        else:

            path_name=path_name

            pass

        console=Retorno('Deseja mostrar o console?[s/n]: ')

        resp_icone=Retorno('Deseja inserir um icone na aplicação?[s/n]: ')

        if(resp_icone=='s'):

            icone=''

            while icone=='':

                icone=input('Informe o caminho do icone: ')

                if(icone!=''):

                    break

                pass

            img_icone=os.path.basename(icone)

            destino=os.path.join(caminho,img_icone)

            shutil.copy(icone,destino)

            if(console=='s'):
            
                os.system('pyinstaller --name={0} --onefile --icon={2} {1}'.format(path_name,arquivo,img_icone))

                pass

            else:

                os.system('pyinstaller --name={0} --onefile --noconsole --icon={2} {1}'.format(path_name,arquivo,img_icone))        

                pass

            pass

        else:

            if(console=='s'):
            
                os.system('pyinstaller --name={0} --onefile {1}'.format(path_name,arquivo))

                pass

            else:

                os.system('pyinstaller --name={0} --onefile --noconsole {1}'.format(path_name,arquivo))

                pass


            pass
        
        temp_path=os.path.join(caminho,'dist')

        for lista in os.listdir(temp_path):

            if(lista.find('.exe')>0):

                os.chdir(temp_path)

                shutil.make_archive(f'{nome}','zip','./',f'{lista}')

                pass

            pass

        os.chdir(temp_path)

        for lista in os.listdir():

            if(lista.find('.zip')>0):

                origem=os.path.join(temp_path,lista)

                destino=os.path.join(caminho,lista)

                shutil.move(origem,destino)

                pass

            pass

        os.chdir(caminho)

        temp_tipo=['.py','.zip']

        for lista in os.listdir():

            nome=str(lista)

            extensao=nome

            nome=nome[:nome.find('.')]

            extensao=extensao[len(nome):]

            if(extensao in temp_tipo):

                continue
            
            if(lista.find('.')>0):

                os.remove(lista)

                pass

            else:

                shutil.rmtree(lista)

                pass

            pass

        print('Arquivo criado e zipado com sucesso')

        pass

    except:

        os.system('pip install pyinstaller')

        Main()

        pass

    pass

def ExecutarScript():

    try:

        Texto(linha=50)

        caminho=input('Informe o caminho onde está o executável: ')

        temp=dict()

        for i,lista in enumerate(os.listdir(caminho)):

            i+=1

            if(lista=='main.py'):

                print('{0}) {1}'.format(i,lista))

                temp[i]=lista

                pass

            pass
        
        opc=''

        while not opc in temp.keys():

            opc=input('Escolha uma das opções acima: ')

            if(opc.isnumeric()==True):

                opc=int(opc)

                if(opc in temp.keys()):

                    break

                pass

            pass

        arquivo=temp[opc]

        os.chdir(caminho)
        
        os.system('python {0}'.format(arquivo))

        pass

    except:

        Main()

        pass

    pass

def Nuitka():

    try:

        Texto(linha=50)

        caminho=input('Informe o caminho onde está o executável: ')

        temp=dict()

        codigo=0

        for lista in os.listdir(caminho):

            if(lista=='main.py'):

                codigo+=1

                print('{0}) {1}'.format(codigo,lista))

                temp[codigo]=lista

                pass

            pass
        
        opc=''

        while not opc in temp.keys():

            opc=input('Escolha uma das opções acima: ')

            if(opc.isnumeric()==True):

                opc=int(opc)

                if(opc in temp.keys()):

                    break

                pass

            pass

        arquivo=temp[opc]

        os.chdir(caminho)

        one_file=Retorno('Deseja criar um único arquivo?[s/n]: ')

        if(one_file=='s'):

            resp_icone=Retorno('Deseja inserir um icone na aplicação?[s/n]: ')

            if(resp_icone=='s'):

                icone=input('Informe o caminho do icone: ')

                img_icone=os.path.basename(icone)

                destino=os.path.join(caminho,img_icone)

                shutil.copy(icone,destino)
                            
                os.system('python -m nuitka --follow-imports --standalone --windows-icon-from-ico={1} --onefile {0}'.format(arquivo,img_icone))

                pass

            else:

                os.system('python -m nuitka --follow-imports --standalone --onefile {0}'.format(arquivo))

                pass

            pass

        else:


            resp_icone=Retorno('Deseja inserir um icone na aplicação?[s/n]: ')

            if(resp_icone=='s'):

                icone=input('Informe o caminho do icone: ')

                img_icone=os.path.basename(icone)

                destino=os.path.join(caminho,img_icone)

                shutil.copy(icone,destino)
                            
                os.system('python -m nuitka --follow-imports --standalone --windows-icon-from-ico={1} {0}'.format(arquivo,img_icone))

                pass

            else:

                os.system('python -m nuitka --follow-imports --standalone {0}'.format(arquivo))

                pass

            pass
        
        print('Arquivo criado e zipado com sucesso')

        pass

    except:

        os.system('pip install nuitka')

        Main()

        pass

    pass

def CxFreeze():

    try:

        Texto(linha=50)

        caminho=input('Informe o caminho onde está o executável: ')

        temp=dict()

        codigo=0

        for lista in os.listdir(caminho):

            if(lista=='main.py'):

                codigo+=1

                print('{0}) {1}'.format(codigo,lista))

                temp[codigo]=lista

                pass

            pass
        
        opc=''

        while not opc in temp.keys():

            opc=input('Escolha uma das opções acima: ')

            if(opc.isnumeric()==True):

                opc=int(opc)

                if(opc in temp.keys()):

                    break

                pass

            pass

        arquivo=temp[opc]

        os.chdir(caminho)

        temp_config={'nome':'','versão':'','descrição':''}

        for indice in temp_config.keys():

            campo=''

            while campo=='':

                campo=input(f'{indice}: ')

                if(campo!=''):

                    break

                pass

            temp_config[indice]=campo

            pass

        with open('setup.py','w') as arq:
            
            arq.writelines('import sys\nfrom cx_Freeze import setup,Executable\n\nbase=None\n\nif(sys.platform=="Win32"):\n\tbase="Win32GUI"\n\tpass\n\nexecutables=[Executable("{0}",base=base)]\n\nsetup(name="{1}",version="{2}",description="{3}",executables=executables)'.format(arquivo,temp_config['nome'],temp_config['versão'],temp_config['descrição']))

            pass
       
        os.system('python setup.py build')

        for lista in os.listdir():

            nome=str(arquivo).capitalize()

            nome=nome[:nome.find('.')]

            if(lista.find('.')<0):
                
                shutil.make_archive(f'{nome}','zip','./',f'{lista}')

                pass

            pass
        
        tipo=['.py','.zip']

        for lista in os.listdir():

            nome=str(lista)

            extensao=nome

            nome=nome[:nome.find('.')]

            extensao=extensao[len(nome):]

            if(lista!='setup.py' and extensao in tipo):

                continue

            if(lista.find('.')<0):

                shutil.rmtree(lista)

                pass

            else:

                os.remove(lista)

                pass

            pass

        print('Arquivo criado e zipado com sucesso')

        pass

    except:

        os.system('pip install cx_Freeze')

        Main()

        pass

    pass

def Py2Exe():

    try:

        Texto(linha=50)

        caminho=input('Informe o caminho onde está o executável: ')

        temp=dict()

        codigo=0

        for lista in os.listdir(caminho):

            nome=str(lista)

            extensao=nome

            nome=nome[:nome.find('.')]

            extensao=extensao[len(nome):]

            if(lista=='main.py'):

                codigo+=1

                print('{0}) {1}'.format(codigo,lista))

                temp[codigo]=lista

                pass

            pass
        
        opc=''

        while not opc in temp.keys():

            opc=input('Escolha uma das opções acima: ')

            if(opc.isnumeric()==True):

                opc=int(opc)

                if(opc in temp.keys()):

                    break

                pass

            pass

        arquivo=temp[opc]

        os.chdir(caminho)

        with open('setup.py','w') as arq:

            arq.write("from distutils.core import setup\nimport py2exe\n\nsetup(console=['{0}'])".format(arquivo))

            pass

        os.system('python setup.py py2exe')

        nome=str(arquivo).capitalize()

        nome=nome[:nome.find('.')]

        os.chdir(caminho)

        for lista in os.listdir():

            if(lista.find('.')<0):

                shutil.make_archive(f'{nome}','zip','./',f'{lista}')
                
                pass

            pass

        tipo=['.py','.zip']

        os.chdir(caminho)

        for lista in os.listdir():

            nome=str(lista)

            extensao=nome

            nome=nome[:nome.find('.')]

            extensao=extensao[len(nome):]

            if(extensao in tipo and lista!='setup.py'):

                continue

            if(lista.find('.')>0):

                os.remove(lista)

                pass

            else:

                shutil.rmtree(lista)

                pass
  
            pass

        print('Arquivo criado e zipado com sucesso')

        pass

    except:

        os.system('pip install py2exe')

        Main()

        pass

    pass

Main()