from ConectionSQL import SQL
import pandas as pd

querys={
    
    'Cliente':
    
    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,
    
    'Vendedor':
    
    """
    
    SELECT * FROM netfeira.vw_vendedor
    
    """,
    
    'Supervisor':
    
    """
    
    SELECT * FROM netfeira.vw_supervisor
    
    """,
    
    'Segmento':
    
    """
    
    SELECT * FROM netfeira.vw_segmento
    
    """,
    
    'Devolucao':
    
    """
    
    DECLARE @DIA SMALLINT,@ANO SMALLINT, @MES SMALLINT

    --MES
    IF DAY(GETDATE())>1

        SET @MES=MONTH(GETDATE())

    ELSE

        SET @MES=MONTH(DATEADD(M,-1,GETDATE()))


    --ANO

    IF MONTH(GETDATE())>1

        SET @ANO=YEAR(GETDATE())

    ELSE

        SET @ANO=YEAR(DATEADD(YEAR,-1,GETDATE()))

    --DIA

    SET @DIA=DAY(DATEADD(D,-1,GETDATE()))

    IF DAY(GETDATE())>1

        SELECT * FROM netfeira.vw_devolucao
        WHERE YEAR([Data de Entrada])=@ANO AND MONTH([Data de Entrada])=@MES AND DAY([Data de Entrada])=@DIA

    ELSE

        SELECT * FROM netfeira.vw_devolucao
        WHERE YEAR([Data de Entrada])=@ANO AND MONTH([Data de Entrada])=@MES

    
    """,
    
    'Produto':
    
    """
    
    SELECT SKU,Produto,Fabricante,Departamento,Seção,Categoria,Linha FROM netfeira.vw_produto
    
    """
    
}


class Query(SQL):

    def __init__(self, usuario, senha, database, server):
        super().__init__(usuario, senha, database, server)

        sql=SQL(usuario,senha,database,server)

        self.conectando=sql.ConexaoSQL()
        
        pass

    def CriarTabela(self):
        
        tabelas_df=dict()

        for tabela,query in querys.items():
            
            tabelas_df[tabela]=pd.read_sql(query,self.conectando)
            
            pass

        return tabelas_df

        pass

    pass