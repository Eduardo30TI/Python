class Moeda:

    def FormatarMoeda(valor):
        a = "{:,.2f}".format(float(valor))
        b = a.replace(',','v')
        c = b.replace('.',',')
        return c.replace('v','.')

        pass

    pass