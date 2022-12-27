import requests

class CNPJ:

    def __init__(self,cnpj):

        self.cnpj=cnpj

        pass

    def ValidarCNPJ(self):

        cnpj=str(self.cnpj)

        validar=True if len(cnpj)==14 and cnpj.isnumeric() else False

        return validar

        pass

    def DigCNPJ(self):

        cnpj=str(self.cnpj)

        contagem=len(cnpj)-2

        digito=cnpj[contagem:]

        return digito

        pass

    def AnalisarCNPJ(self):

        cnpj_base=str(self.cnpj)

        contagem=len(cnpj_base)-2

        cnpj_base=cnpj_base[:contagem]

        loop=0

        algorismo=[5,4,3,2,9,8,7,6]

        for i in range(0,2):

            if(i==1):

                algorismo.remove(6)

                algorismo.insert(0,6)

                pass

            indice=0

            total=0

            for i,num in enumerate(cnpj_base):

                i+=1

                contagem=len(algorismo)

                val=algorismo[indice]

                res=int(val)*int(num)

                total+=res
                                            
                if(i>=contagem):

                    indice=(i-1)-contagem

                    pass

                indice+=1

                pass

            resto=11-(total%11)

            cnpj_base=(f'{cnpj_base}{resto}')

            pass

        status='VALIDO' if cnpj_base==self.cnpj else 'CNPJ INVALIDO'

        return status

        pass

    def GetCNPJ(self):

        while True:

            url=(f'https://receitaws.com.br/v1/cnpj/{self.cnpj}')

            requisicao=requests.get(url)

            codigo=requisicao.status_code

            if(codigo==200):

                break

            pass

        return requisicao.json()

        pass

    def GetDados(self):

        cnpj=str(self.cnpj)

        while True:

            url=(f'https://minhareceita.org/{cnpj}')

            requisicao=requests.get(url)

            codigo=requisicao.status_code

            if(codigo==200 or codigo!=200):

                break

            pass

        return requisicao.json()

        pass
    
    def GetDadosSituacao(self,dados):
        
        return dados['descricao_situacao_cadastral']

        pass

    def GetCNPJSituacao(self,dados):

        return dados['situacao']

        pass

    def TipoPessoa(self):

        cnpj=str(self.cnpj)

        validar='PESSOA JURÍDICA' if len(cnpj)==14 and cnpj.isnumeric() else 'PESSOA FÍSICA'

        return validar

        pass

    def FormatarCNPJ(self):

        cnpj=str(self.cnpj)

        cnpj='{}.{}.{}/{}-{}'.format(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])

        return cnpj

        pass

    def FormatarCPF(self):

        cnpj=str(self.cnpj)

        cnpj='{}.{}.{}-{}'.format(cnpj[:3],cnpj[3:6],cnpj[6:9],cnpj[9:11])

        return cnpj

        pass    

    def GetCodigo(self):

        cnpj=str(self.cnpj)

        url=(f'https://minhareceita.org/{cnpj}')

        requisicao=requests.get(url)

        codigo=requisicao.status_code

        return codigo

        pass

    pass