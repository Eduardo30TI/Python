from Acesso import Login
from Query import Query
import os
from glob import glob
import pandas as pd
from datetime import datetime

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

querys={

    'motor':

    """

    WITH TabBase AS (

        SELECT * 
        FROM (

            SELECT b.nu_ped,b.dt_data,b.situacao,r.dt_montagem,r.nu_rom 
            FROM (

                SELECT * FROM (

                    SELECT ped.nu_ped,it.situacao,nf.nu_nf_emp_fat,
                    CONVERT(DATETIME,CAST(COALESCE(nf.dt_emis,ped.dt_cad) AS DATE),101) AS dt_data
                    FROM ped_vda ped
                    INNER JOIN it_pedv it ON ped.nu_ped=it.nu_ped AND ped.cd_emp=it.cd_emp AND it.situacao IN ('AB','FA')
                    LEFT JOIN nota nf ON ped.cd_emp=nf.cd_emp AND ped.nu_ped=nf.nu_ped AND it.nu_nf=nf.nu_nf
                    GROUP BY ped.nu_ped,it.situacao,nf.nu_nf_emp_fat,CONVERT(DATETIME,CAST(COALESCE(nf.dt_emis,ped.dt_cad) AS DATE),101)

                )a
                WHERE a.dt_data=CONVERT(DATETIME,CAST(GETDATE() AS DATE),101)

            )b
            INNER JOIN it_rom i ON b.nu_ped=i.nu_ped
            INNER JOIN romaneio r ON i.nu_rom=r.nu_rom

        )c
        PIVOT(COUNT(nu_ped) FOR situacao IN([AB],[FA]))d
        WHERE d.AB<=0

    )


        SELECT * FROM (

            SELECT a.Romaneio,a.Rota,a.[ID Motor],a.Motorista,a.Veículo,a.Complemento,a.Pedido,a.MIX,a.Cliente,a.Qtde,a.[Total Venda],
            COUNT(a.Motorista)OVER(PARTITION BY Motorista) AS Seq
            FROM (

                SELECT r.nu_rom AS [Romaneio],rot.descricao AS [Rota],r.cd_motor AS [ID Motor],m.nome AS [Motorista],v.descricao AS [Veículo],m.Complemento,
                COUNT(i.nu_ped) AS [Pedido],COUNT(DISTINCT it.cd_prod) AS [MIX],COUNT(DISTINCT ped.cd_clien) AS [Cliente],
                SUM(it.qtde) AS Qtde,SUM(it.vl_venda) AS [Total Venda]
                FROM it_rom i
                INNER JOIN romaneio r ON i.nu_rom=r.nu_rom
                INNER JOIN it_pedv it ON i.nu_nf=it.nu_nf AND i.nu_ped=it.nu_ped AND i.cd_emp=it.cd_emp AND it.situacao IN('FA','AB')
                INNER JOIN ped_vda ped ON i.nu_ped=ped.nu_ped AND i.cd_emp=ped.cd_emp
                LEFT JOIN nota nf ON ped.nu_ped=nf.nu_ped AND it.nu_nf=nf.nu_nf
                INNER JOIN motor m ON r.cd_motor=m.cd_motor
                INNER JOIN veic_ent v ON r.cd_veic_ent=v.cd_veic_ent
                INNER JOIN rot_prdf rot ON r.cd_rot_prdf=rot.cd_rot_prdf
                INNER JOIN TabBase x ON i.nu_rom=x.nu_rom
                WHERE m.Complemento<>''
                GROUP BY rot.descricao,r.cd_motor,v.descricao,m.nome,m.Complemento,r.nu_rom

            )a

        )b

    """
}

def main():

    df=sql.CriarTabela(kwargs=querys)

    temp_path=os.path.join(os.getcwd(),'memoria.csv')
    arq=glob(temp_path)

    temp_df=pd.DataFrame()

    if len(arq)>0:

        temp_df=pd.read_csv(arq[-1])
        lista=temp_df['Romaneio'].unique().tolist()
 
        df['motor']=df['motor'].loc[~df['motor']['Romaneio'].isin(lista)]

        pass

    if len(df['motor'])>0:

        whatsapp_df=pd.DataFrame(columns=['Vendedor','DDD','Telefone','Mensagens','Path'])

        for m in df['motor']['Motorista'].unique().tolist():

            nome=str(m).title()

            complemento=str(df['motor'].loc[df['motor']['Motorista']==m,'Complemento'].unique().tolist()[-1])
            
            if complemento.isnumeric()==False or len(complemento[2:])<=2:

                continue
            
            ddd=complemento[:2]
            telefone=complemento[2:]

            lista=df['motor'].loc[df['motor']['Motorista']==m,'Romaneio'].unique().tolist()

            mensagem=f'Olá {nome} tudo bem? me chamo Iris, estou passando para te informar que você já pode carregar rota já separada.\n\nSegue abaixo o número do romaneio:\n'

            for l in lista:

                mensagem+=f'\n.Romaneio: *{l}*'

                pass

            mensagem+='\n\nObs. Assim que chegar informar os romaneios para o setor logístico para agilizar o carregamento. Grata pela colaboração e tenho um excelente trabalho.'

            whatsapp_df.loc[len(whatsapp_df)]=[nome,ddd,telefone,mensagem,'']

            pass

        whatsapp_df.to_excel(f'whatsapp.xlsx',index=False)
        temp_df=pd.concat([temp_df,df['motor']],axis=0,ignore_index=True)
        temp_df.to_csv(temp_path,index=False,encoding='UTF-8')

        pass

    pass


if __name__=='__main__':

    main()

    pass