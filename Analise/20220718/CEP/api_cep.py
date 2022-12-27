import requests


class CEP:

    def GetCEP(cep):

        url=f'viacep.com.br/ws/{cep}/json/'

        while True:

            info=requests.get(url)

            codigo=info.status_code

            if(codigo==200):

                break

            pass

        return info.json()

        pass

    pass