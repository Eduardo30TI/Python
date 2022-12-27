import os
from glob import glob
import pandas as pd
import shutil
from getpass import getuser
from datetime import datetime

class GUI:

    def CreateDir(self,caminho: str):

        if(not os.path.exists(caminho)):

            os.mkdir(caminho)

            pass

        pass

    def GetPath(self):

        return os.getcwd()

        pass


    def GetArq(self,caminho: str):

        return os.path.basename(caminho)

        pass

    def GetDir(self,caminho: str):

        caminho=os.path.dirname(caminho)

        arq=self.GetArq(caminho=caminho)

        return arq

        pass

    def PathDir(self,caminho):

        return os.path.dirname(caminho)

        pass

    def UnirPath(self,caminho: str,arquivo: str):

        return os.path.join(caminho,arquivo)

        pass

    def Chdir(self,caminho: str):

        os.chdir(caminho)

        pass

    def Cls(self):

        os.system('cls')

        pass

    def Move(origem: str,destino: str):

        shutil.move(origem,destino)

        pass

    def GetExists(self,caminho: str):

        return os.path.exists(caminho)

        pass


    def GerarTXT(self,caminho: str,arquivo: str,conteudo: str):

        temp_path=os.path.join(caminho,arquivo)

        with open(temp_path,'w') as arq:

            arq.write(conteudo)

            pass

        return os.path.join(caminho,arquivo)

        pass

    def ExecutarScript(self,caminho: str):

        temp_path=self.PathDir(caminho)

        arq=self.GetArq(caminho)

        self.Chdir(temp_path)

        os.system(f'python.exe {arq}')

        pass

    def MapearArq(self,caminho: str,tipo: str):

        temp=[]

        for path,dir,arq in os.walk(caminho):

            for d in dir:

                temp_path=os.path.join(path,d,f'*{tipo}')

                arquivos=glob(temp_path)

                if(len(arquivos)<=0):

                    continue

                temp.append(arquivos[-1])
                
                pass

            pass

        return temp

        pass

    def Arquivos(self,caminho,tipo):

        temp_path=os.path.join(caminho,f'*{tipo}')

        return glob(temp_path)

        pass

    def Retorno(self,conteudo: str):

        opc={'s':True,'n':False}

        resp=''

        while not resp in opc.keys():

            resp=input(conteudo).lower()

            pass

        return opc[resp]

        pass

    def Titulo(self,texto='',linha=0,espaco=0):

        if(texto!='' and linha>0 and espaco>0):

            print(f'{texto:^{espaco}}')

            print('-'*linha)

            pass

        elif(texto!='' and linha<=0 and espaco>0):

            print(f'{texto:^{espaco}}')

            #print('-'*linha)

            pass        

        elif(texto!='' and linha<=0 and espaco<=0):

            print(f'{texto}')

            #print('-'*linha)

            pass    

        elif(texto=='' and linha>0 and espaco<=0):

            #print(f'{texto}')

            print('-'*linha)

            pass            

        pass

    def Menu(self,label: str,*args: list):

        usuario=getuser()

        now=str(datetime(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day,hour=datetime.now().hour,minute=datetime.now().minute,second=datetime.now().second))

        self.Titulo(texto=label,espaco=50)

        self.Titulo(texto=usuario,espaco=50)

        self.Titulo(texto=now,linha=50,espaco=50)

        temp_dict=dict()

        for i,c in enumerate(args[-1]):

            i+=1

            temp_dict[i]=c

            print(f'{i}) {c}')

            pass

        resp=''

        while not resp in temp_dict.keys():

            resp=input('Escolha uma das opções acima: ')

            if(resp.isnumeric()):

                resp=int(resp)

                pass

            pass

        return temp_dict[resp]

        pass

    def RemoverArquivo(self,caminho: str,filtro: str):

        filtro=(f'*{filtro}')

        temp_path=os.path.join(caminho,filtro)

        dados=glob(temp_path)

        if(len(dados)>0):

            for arq in dados:
                
                os.remove(arq)

            pass

        pass

    pass
