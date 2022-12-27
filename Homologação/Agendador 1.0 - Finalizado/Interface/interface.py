import os
from glob import glob
import shutil
from getpass import getuser
from datetime import datetime

from setuptools import Command


class GUI:

    def Titulo(self,texto='',linha=0,espaco=0):

        if(texto!='' and linha>0 and espaco>0):

            print(f'{texto:^{espaco}}')

            print('-'*linha)

            pass

        elif(texto!='' and linha<=0 and espaco>0):

            print(f'{texto:^{espaco}}')

            pass

        elif(texto!='' and linha<=0 and espaco<=0):

            print(texto)

            pass

        else:

            print('-'*linha)

            pass

        pass


    def Menu(self,titulo,*args):

        usuario=getuser()

        data=datetime.strftime(datetime.now(),'%d/%m/%Y %H:%M:%S')

        self.Titulo(texto=titulo,linha=0,espaco=50)

        self.Titulo(texto=usuario,linha=0,espaco=50)

        self.Titulo(texto=data,linha=50,espaco=50)

        temp_dict=dict()
        
        for key,value in enumerate(args[-1]):

            key+=1

            print(f'{key}) {value}')

            temp_dict[key]=value

            pass

        self.Titulo(linha=50)

        resp=''

        while not resp in temp_dict.keys():

            resp=input('Escolha uma das oções acima: ')

            if(resp.isnumeric()):

                resp=int(resp)

                if(resp in temp_dict.keys()):

                    break

                pass

            pass

        return temp_dict[resp]

        pass


    def Retorno(self,texto):

        resp=''

        opc={

            's':True,

            'n':False
        }

        while not resp in opc.keys():

            resp=input(texto).lower()

            if(resp in opc.keys()):

                break
            
            pass

        return opc[resp]

        pass

    def Mapear(self,caminho,filtro):

        temp=[]

        for path,dir,arq in os.walk(caminho):

            for d in dir:

                tipo=(f'*{filtro}')

                temp_path=os.path.join(path,d,tipo)

                arquivos=glob(temp_path)

                if(len(arquivos)<=0):

                    continue

                temp.append(arquivos[-1])                

                pass

            pass

        return temp

        pass

    def GetArquivo(self,caminho):

        return os.path.basename(caminho)

        pass

    def GetDir(self,caminho):

        arq=os.path.basename(caminho)

        path_base=caminho

        cont=len(path_base)-(len(arq)+1)

        path_base=path_base[:cont]

        return path_base

        pass

    def UnirCaminho(self,path_dir,arq_name):

        return os.path.join(path_dir,arq_name)

        pass

    def CriarPasta(self,caminho,dir_name):

        temp_path=self.UnirCaminho(caminho,dir_name)

        if(not os.path.exists(temp_path)):

            os.mkdir(temp_path)

            pass

        print('Pasta criada com sucesso!')

        pass

    def Copiar(self,path_origem,path_destino):

        shutil.copy(path_origem,path_destino)

        pass

    def Mover(self,path_origem,path_destino):

        shutil.move(path_origem,path_destino)

        pass

    def Limpar(self):

        os.system('cls')

        pass

    def ScriptExe(self,caminho,comando):
        
        temp_path=self.GetDir(caminho)

        os.chdir(temp_path)

        os.system(comando)
        
        pass

    def TestarScript(self):

        caminho=''

        while caminho=='':

            caminho=input('Informe o caminho: ')

            pass

        tipo='main.py'

        temp_path=os.path.join(caminho,tipo)

        command=(f'python {tipo}')

        self.ScriptExe(caminho=temp_path,comando=command)

        pass


    pass