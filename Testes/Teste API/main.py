import requests
from ConectionSQL import SQL
import pandas as pd
import time

sql=SQL('Netfeira','sqlserver','MOINHO','192.168.0.252')

conectando=sql.ConexaoSQL()

url='https://api.powerbi.com/beta/89024f02-ca0e-4816-b5b2-1b5bdf790280/datasets/6cba7b0f-0441-4891-9969-c69cf8f6996c/rows?key=JQvJzqw5YOTmXJvSzAeoeuIm2AH7EaJ6Iz6sdaTxkQKnG31NvGH2K19%2BCOXQ%2FL87HpGZq0BQKoDCG9TrCom1MQ%3D%3D'

while True:

    query="""

    SELECT CONVERT(DECIMAL(15,2),SUM(qtde*vl_unit_vda)) AS 'Total',COUNT(cd_prod) AS 'Produto'
    FROM it_pedv
    INNER JOIN ped_vda ON it_pedv.nu_ped=ped_vda.nu_ped
    WHERE YEAR(ped_vda.dt_ped)=YEAR(GETDATE()) AND MONTH(ped_vda.dt_ped)=MONTH(GETDATE()) AND DAY(ped_vda.dt_ped)=DAY(GETDATE()) AND it_pedv.situacao IN('FA','AB')


    """

    df=pd.read_sql(query,conectando)

    dados=df.to_dict('records')

    r=requests.post(url,json=dados)

    print(r)

    pass