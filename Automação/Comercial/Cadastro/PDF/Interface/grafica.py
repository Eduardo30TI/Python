import os
from glob import glob
from getpass import getuser

class GUI():

    def Titulo(self,texto='',espaco=0,linha=0):

        if texto!='' and espaco>0 and linha>0:

            print(f'{texto:^{espaco}}')

            print('-'*linha)

            pass

        elif texto!='' and espaco>0 and linha<=0:

            print(f'{texto:^{espaco}}')

            #print('-'*linha)

            pass


        elif texto!='' and espaco<=0 and linha<=0:

            print(f'{texto:^{espaco}}')

            #print('-'*linha)

            pass

        elif texto!='' and espaco<=0 and linha>0:

            print(texto)

            print('-'*linha)

            pass


        else:

            print('-'*linha)

            pass

        pass

    def Menu(self,menu: list):

        temp_dict=dict()

        for i,val in enumerate(menu):

            i+=1

            print(f'{i}) {val}')

            temp_dict[i]=val

            pass

        while True:

            resp=input('Escolha uma das opções acima: ')

            if resp.isnumeric():

                resp=int(resp)

                if resp in temp_dict.keys():

                    break

                pass

            pass

        return temp_dict[resp]

        pass

    def Retorno(self,texto: str):

        opc={'s':True,'n':False}

        while True:

            resp=input(texto).lower()

            if resp in opc.keys():

                break

            pass

        return opc[resp]

        pass

    def Cls(self):

        os.system('cls')

        pass

    def Chdir(self,path):

        os.chdir(path)

        pass

    def ListDir(self,path):

        return os.listdir(path)

        pass

    def MapArq(self,path,tipo):

        lista=[]

        for path,dir,arqs in os.walk(path):

            for d in dir: 

                print(d)

                temp_path=os.path.join(path,d,tipo)
                
                arquivos=glob(temp_path)

                if len(arquivos)<=0:

                    continue

                lista.append(arquivos[-1])

                pass

            pass

        return lista

        pass


    def GetCWD(self):

        return os.getcwd()

        pass

    def PathJoin(self,path_orig,path_dir):

        path=os.path.join(path_orig,path_dir)

        return path

        pass

    def PathUser(self):

        usuario=getuser()

        path=self.GetCWD()

        count=path.find(usuario)

        path=path[:count]

        path=self.PathJoin(path,usuario)

        return path

        pass

    def PathDir(self,path):

        return os.path.dirname(path)

        pass

    def BaseName(self,path):

        return os.path.basename(path)

        pass

    def GetUser(self):

        return getuser()

        pass

    def PathExists(self,path):

        return os.path.exists(path)

        pass

    def MkDir(self,path):
        
        if not os.path.exists(path):

            os.makedirs(path)

            pass

        pass


    def ExecuteScript(self,path,path_base):

        path_dir=self.PathDir(path)

        self.Chdir(path_dir)

        arq=self.BaseName(path)

        os.system(f'python {arq}')
        
        self.Chdir(path_base)

        pass

    def Arquivos(self,path,tipo):

        temp_path=os.path.join(path,tipo)

        arquivos=glob(temp_path)

        return arquivos

        pass

    pass