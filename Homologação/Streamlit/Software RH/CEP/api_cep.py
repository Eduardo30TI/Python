import requests

class CEP:

    def GetCEP(cep):

        url=f'http://cep.republicavirtual.com.br/web_cep.php?cep={cep}&formato=json'

        while True:

            info=requests.get(url)

            codigo=info.status_code

            if(codigo==200):

                break

            pass

        dados=info.json()

        temp_dict={'cep':cep,'logradouro':(dados['tipo_logradouro'] + ' '+dados['logradouro']),'bairro':dados['bairro'],'cidade':dados['cidade'],'uf':dados['uf']}

        return temp_dict

        pass

    def GetCodigo(cep):

        url=f'http://cep.republicavirtual.com.br/web_cep.php?cep={cep}&formato=json'

        while True:

            info=requests.get(url)

            codigo=info.status_code

            if(codigo>0):

                break

            pass

        return codigo

        pass    
    
    def ValidarCEP(cep):

        cep=str(cep)

        validar=len(cep)

        codigo=f'0{cep}'

        if(validar==8):

            codigo=cep

            pass

        return codigo

        pass

    pass