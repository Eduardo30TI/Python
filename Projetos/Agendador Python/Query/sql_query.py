from SqLite import SQL

tabela={

    'Arquivo':"""
    
    CREATE TABLE IF NOT EXISTS arquivo(

        codigo SMALLINT NOT NULL,
        caminho TEXT NOT NULL,
        pasta VARCHAR(250) NOT NULL

    )
    
    """,

    'Configuracao':"""
    
    CREATE TABLE IF NOT EXISTS configuracao(

        codigo SMALLINT NOT NULL,
        tipo VARCHAR(250) NOT NULL,
        semana VARCHAR(250) NOT NULL,
        tempo SMALLINT NOT NULL,
        atualizar SMALLINT NOT NULL,
        dt_prox VARCHAR(250) NOT NULL

    )
    
    
    """

}

class GetSQL(SQL):

    def __init__(self, banco):
        super().__init__(banco)

        self.sql=SQL(banco)

        self.codigo=0

        self.arquivo=''

        self.pasta=''

        self.tipo=''

        self.semana=''

        self.tempo=0

        self.atualizador=0

        self.dt_prox=None

        pass


    def BaseQuery(self):

        query={

            'Código':"""
            
            SELECT MAX(codigo) FROM arquivo
            
            """,

            'Validar':"""
            
            SELECT COUNT(*) FROM arquivo WHERE caminho='{0}'
            
            """.format(self.arquivo),

            'InserirArquivo':"""
            
            INSERT INTO arquivo (codigo,caminho,pasta) VALUES({0},'{1}','{2}')
            
            """.format(self.codigo,self.arquivo,self.pasta),

            'AlterarArquivo':"""
            
            UPDATE arquivo
            SET caminho='{0}',
            pasta='{1}'
            WHERE caminho='{0}'
            
            """.format(self.arquivo,self.pasta),

            'DeleteArquivo':"""
            
            DELETE FROM arquivo WHERE codigo={0}
            
            """.format(self.codigo),

            'InserirConfiguracao':"""
            
            INSERT INTO configuracao (codigo,tipo,semana,tempo,atualizar,dt_prox) VALUES({0},'{1}','{2}',{3},{4},'{5}')
            
            """.format(self.codigo,self.tipo,self.semana,self.tempo,self.atualizador,self.dt_prox),

            'AlterarConfiguracao': """
            
            UPDATE configuracao
            SET tipo='{1}',
            semana='{2}',
            tempo={3},
            atualizar={4},
            dt_prox='{5}'
            WHERE codigo={0}
            
            """.format(self.codigo,self.tipo,self.semana,self.tempo,self.atualizador,self.dt_prox),

            'DeleteConfiguracao': """
            
            DELETE FROM configuracao WHERE codigo={0}
            
            """.format(self.codigo),

            'ConsultaArquivo':"""
            
            SELECT codigo,caminho,pasta 
            FROM arquivo
                        
            """,
            'ConsultaConfiguracao':"""
            
            SELECT codigo,tipo,semana,tempo,dt_prox
            FROM configuracao
            WHERE codigo={0}
            
            """.format(self.codigo),

            'ValidarConfiguracao':"""
            
            SELECT COUNT(*) FROM configuracao WHERE codigo={0}
            
            """.format(self.codigo),

            'Dados':"""
            
            SELECT arquivo.codigo,caminho,tipo,semana,atualizar,tempo,dt_prox as dt_prox
            FROM arquivo
            INNER JOIN configuracao ON arquivo.codigo=configuracao.codigo
            
            """,

            'AtualizacaoHora':"""
            
            UPDATE configuracao
            SET dt_prox='{1}'
            WHERE codigo={0}
            
            """.format(self.codigo,self.dt_prox)
            
        }

        return query

        pass

    def CriarTabela(self):

        try:
            
            conectando=self.sql.Conexao()

            for tab in tabela.values():

                self.sql.Salvar(tab,conectando)

                pass

            pass


        except Exception as erro:

            print(f'Erro: {erro}')

            pass

        pass


    pass