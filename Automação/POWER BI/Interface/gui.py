class Interface:

    def Titulo(texto='',espaco=0,linha=0):

        texto=str(texto).title()

        if(texto!='' and espaco>0 and linha>0):

            print(f'{texto:^{espaco}}')

            print('-'*linha)

            pass

        elif(texto!='' and espaco>0 and linha<=0):

            print(f'{texto:^{espaco}}')

            pass

        elif(texto=='' and espaco<=0 and linha>0):

            print('-'*linha)

            pass         

        pass


    def Menu(*args):

        temp_dict=dict()

        for key,value in enumerate(args[-1]):

            key+=1

            print(f'{key}) {value}')

            temp_dict[key]=value

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

        opc={'s':True,'n':False}

        resp=''

        while not resp in opc.keys():

            resp=input(texto).lower()

            if(resp in opc.keys()):

                break

            pass

        return opc[resp]

        pass


    pass