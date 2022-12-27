def Numero(valor):

    a = "{:,.0f}".format(int(valor))
    b = a.replace(',','v')
    c = b.replace('.',',')
    valor=c.replace('v','.')

    print(valor) 

    pass

Numero(1500000)