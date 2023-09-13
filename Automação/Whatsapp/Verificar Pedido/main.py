from Acesso import Login
from Query import Query
from Moeda import Moeda
import pandas as pd
import os
from glob import glob
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'pedidos':

    """

	SELECT a.[Tipo de Operação],A.Origem,A.[Data de Faturamento],a.[ID Usuário],a.Usuário,a.Situação,a.Pedido,
	a.[ID Cliente],c.[Nome Fantasia],
	a.[ID Vendedor],v.Vendedor,
	c.Principal,b.Vendedor AS [Carteira],
	s.Equipe,s.Supervisor,s.[DDD Sup],s.[Telefone Sup],
	a.Total,a.MIX
	FROM (

		SELECT ped.[Tipo de Operação],ped.Origem,ped.[Data de Faturamento],ped.[ID Usuário],u.Usuário,u.[E-mail Usuário],
		ped.Pedido,ped.Situação,ped.[ID Cliente],
		ped.[ID Vendedor],
		CASE WHEN ped.[ID Vendedor]=c.[ID Vendedor] THEN 1 ELSE 0 END AS [Verificar],
		SUM(ped.[Total Venda]) AS Total,COUNT(ped.SKU) AS [MIX]
		FROM netfeira.vw_targetestatistico ped
		LEFT JOIN netfeira.vw_carteira c ON ped.[ID Cliente]=c.[ID Cliente] AND ped.[ID Vendedor]=c.[ID Vendedor]
		INNER JOIN netfeira.vw_usuario u ON ped.[ID Usuário]=u.[ID Usuário]
		WHERE ped.[Tipo de Operação]<>'OUTROS'
		GROUP BY ped.[Data de Faturamento],ped.[ID Usuário],u.Usuário,
		ped.Pedido,ped.Situação,ped.[ID Cliente],
		ped.[ID Vendedor],c.[ID Vendedor],ped.Origem,u.[E-mail Usuário],ped.[Tipo de Operação]

	)a
	INNER JOIN netfeira.vw_cliente c ON a.[ID Cliente]=c.[ID Cliente]
	INNER JOIN netfeira.vw_vendedor v ON a.[ID Vendedor]=v.[ID Vendedor]
	INNER JOIN netfeira.vw_vendedor b ON c.Principal=b.[ID Vendedor]
	INNER JOIN netfeira.vw_supervisor s ON b.[ID Equipe]=s.[ID Equipe]
	WHERE a.Verificar=0
	AND a.[Data de Faturamento]=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)
	ORDER BY a.[Data de Faturamento]

    """
}

def main():

    df=sql.CriarTabela(kwargs=querys)

    temp_df=pd.DataFrame()
    temp_path=os.path.join(os.getcwd(),'memoria.csv')
    arq=glob(temp_path)

    if len(arq)>0:

        temp_df=pd.read_csv(temp_path,encoding='UTF-8')
        lista=temp_df['Pedido'].unique().tolist()

        df['pedidos']=df['pedidos'].loc[~df['pedidos']['Pedido'].isin(lista)]

        pass

    whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])
    
    temp_dict=dict()

    if len(df['pedidos'])>0:

        for i in df['pedidos'].index.tolist():

            temp_dict['pedido']=df['pedidos'].loc[i,'Pedido']
            temp_dict['total']=Moeda.FormatarMoeda(df['pedidos'].loc[i,'Total'])
            temp_dict['mix']=Moeda.Numero(df['pedidos'].loc[i,'MIX'])

            temp_dict['ddd']=df['pedidos'].loc[i,'DDD Sup']
            temp_dict['telefone']=df['pedidos'].loc[i,'Telefone Sup']

            temp_dict['vend_ped']=str(df['pedidos'].loc[i,'Vendedor']).title()
            temp_dict['carteira']=str(df['pedidos'].loc[i,'Carteira']).title()
            temp_dict['supervisor']=str(df['pedidos'].loc[i,'Supervisor']).title()

            temp_dict['origem']=str(df['pedidos'].loc[i,'Origem']).capitalize()
            temp_dict['operacao']=str(df['pedidos'].loc[i,'Tipo de Operação']).capitalize()

            temp_dict['user']=str(df['pedidos'].loc[i,'Usuário']).title()

            mensagem=f'Verificar\nTipo de Pedido: {temp_dict["operacao"]} -  Origem do Pedido: {temp_dict["origem"]}\n\nOlá {temp_dict["supervisor"]} identifiquei que o pedido: {temp_dict["pedido"]} foi digitado mas o vendedor da venda não bate com o que está associado no cadastro do cliente. Abaixo contém o detalhe do pedido:\n\n\t.Vendedor do Pedido: *{temp_dict["vend_ped"]}*\n\t.Vendedor da Carteira: *{temp_dict["carteira"]}*\n\t.Total do Pedido: *R$ {temp_dict["total"]}*\n\t.Usuário Responsável: *{temp_dict["user"]}*'

            whatsapp_df.loc[len(whatsapp_df)]=[temp_dict['supervisor'],temp_dict['ddd'],temp_dict['telefone'],mensagem,'']

            #break

            pass
        
        whatsapp_df.to_excel('whatsapp.xlsx',index=False)
        temp_df=pd.concat([temp_df,df['pedidos']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path,index=False,encoding='UTF-8')

        pass

    pass


if __name__=='__main__':

    if datetime.now().month==1 and datetime.now().day==1 and datetime.now().hour==8:
        
        temp_df=pd.DataFrame()
        temp_path=os.path.join(os.getcwd(),'memoria.csv')
        arq=glob(temp_path)

        if len(arq)>0:

            os.remove(temp_path)

            pass

        pass

    else:

        main()

        pass

    pass