
class Interface:

    def Titulo(texto='',linha=0,espaco=0):

        texto=str(texto).title()

        if(linha==0 and espaco==0):

            print(f'{texto}')

            pass

        elif(linha==0 and espaco>0):

            print(f'{texto:^{espaco}}')

            pass

        elif(linha>0 and espaco==0 and len(texto)==0):

            print('-'*linha)

            pass

        elif(linha>0 and espaco>0):

            print(f'{texto:^{espaco}}')

            print('-'*linha)

            pass

        pass

    def Menu(*args):

        temp_dict=dict()

        for lista in args:

            for indice,valor in enumerate(lista):

                indice+=1

                print(f'{indice}) {valor}')

                temp_dict[indice]=valor

                pass

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

    def Retorno(texto):

        opcao=['s','n']

        resp=''

        while not resp in opcao:

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