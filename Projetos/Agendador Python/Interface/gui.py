import os

class Interface:

    def __init__(self):

        pass

    def Titulo(self,linha=0,espaco=0,texto=''):

        if(texto=='' and espaco==0 and linha!=0):

            print('-'*linha)

            pass
        
        elif(texto!='' and espaco==0 and linha==0):

            print(f'{texto}')

            pass

        elif(texto!='' and espaco!=0 and linha==0):

            print(f'{texto:^{espaco}}')

            pass

        elif(texto!='' and espaco==0 and linha!=0):

            print(f'{texto}')

            print('-'*linha)

            pass

        else:

            print(f'{texto:^{espaco}}')

            print('-'*linha)            

            pass

        pass

    def Menu(self,**kwargs):

        temp_dict=dict()

        for indice,submenu in kwargs['kwargs'].items():

            temp_dict[indice]=submenu

            print(f'{indice}) {submenu}')

            pass

        resp=''

        while not resp in temp_dict.keys():

            resp=input('Escolha uma das opções acima: ')

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

        opcao=['s','n']

        while resp=='':

            resp=input(texto).lower()

            if(resp in opcao):

                break

            pass

        if(resp=='s'):

            resp=True

            pass

        else:

            resp=False

            pass

        return resp

        pass

    pass