import telebot
from telebot import types
import pyttsx3
from Acesso import Login
from Query import Query
from Moeda import Moeda
from RemoverArquivo import Remover
from decouple import config
from datetime import datetime
from glob import glob
import os
from pathlib import Path
import pandas as pd

TOKEN=config('TOKEN')

bot=telebot.TeleBot(token=TOKEN,parse_mode='HTML')

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

comando=None

espera=3600

querys={

    'Receber':

    """
    
    SELECT * FROM netfeira.vw_contareceber
    WHERE Situação='EM ABERTO'
    
    """,

    'Cliente':

    """
    
    SELECT * FROM netfeira.vw_cliente
    
    """,

    'Historico':


    """
    
    WITH TabEntrega AS (

        SELECT DISTINCT tp_entrega,
        CASE WHEN tp_entrega='TR' THEN 'TRANSPORTADORA'
        WHEN tp_entrega='RE' THEN 'RETIRA' WHEN tp_entrega='EN' THEN 'ENTREGA' END AS st_entrega
        FROM ped_vda

    ),

    TabEvento AS (

        SELECT * FROM (

            SELECT a.seq_evento,a.cd_emp,a.cd_clien,a.dt_criacao,a.nu_ped,a.des_fila,a.seq,
            MAX(a.seq)OVER(PARTITION BY a.cd_emp,a.cd_clien,a.nu_ped ORDER BY a.seq DESC) AS seq_max
            FROM (

                SELECT e.seq_evento,e.cd_emp,e.cd_clien,e.dt_criacao,e.nu_ped,f.des_fila,
                ROW_NUMBER()OVER(PARTITION BY e.cd_emp,e.cd_clien,e.nu_ped ORDER BY e.seq_evento) AS seq
                FROM evento e
                INNER JOIN fila f ON e.cd_fila=f.cd_fila

            )a

        )b
        WHERE b.seq=b.seq_max

    )

    SELECT CONVERT(DATETIME,CAST(ped.dt_cad AS DATE),101) AS [Data do Pedido],ped.dt_cad AS [Data e Hora],emp.nome_fant AS [Empresa],
    i.nu_ped AS [Pedido],tp.[Estatística Comercial],tp.[Tipo de Pedido],ped.cd_clien AS [ID Cliente],cli.[Nome Fantasia],cli.Matriz,
    it.cd_prod AS SKU,prod.Produto,prod.Fabricante,it.seq AS [Seq],
    it.unid_vda AS [Unid. VDA],it.qtde_unid_vda AS [Qtde VDA],
    it.vl_venda AS [Total Venda],
    CASE WHEN it.situacao='FA' THEN 'FATURADO' ELSE 'EM ABERTO' END AS [Situação]
    ,ev.des_fila AS [Fila],en.st_entrega AS [Situação de Entrega]
    FROM it_rom i
    INNER JOIN romaneio r ON i.nu_rom=r.nu_rom AND r.situacao<>'EN'
    INNER JOIN ped_vda ped ON i.nu_ped=ped.nu_ped AND i.cd_emp=ped.cd_emp
    INNER JOIN it_pedv it ON ped.cd_emp=it.cd_emp AND ped.nu_ped=it.nu_ped
    INNER JOIN TabEvento ev ON ped.cd_emp=ev.cd_emp AND ped.cd_clien=ev.cd_clien AND ped.nu_ped=ev.nu_ped
    INNER JOIN TabEntrega en ON ped.tp_entrega=en.tp_entrega
    INNER JOIN empresa emp ON ped.cd_emp=emp.cd_emp AND emp.ativo=1
    INNER JOIN netfeira.vw_cliente cli ON ped.cd_clien=cli.[ID Cliente]
    INNER JOIN netfeira.vw_produto prod ON it.cd_prod=prod.SKU
    INNER JOIN netfeira.vw_tpped tp ON ped.tp_ped=tp.[ID Tipo]
    AND NOT it.situacao IN('CA','DV')
    
    """

}


commands_dict={
      

}

start={
      

}

funcoes={


}

#função usando para opções
col_dict={

}

tab_dict={

}

col_name={


}

callback_dict={
   

}


@bot.message_handler(commands=[])
def Main(message):




    pass

def Opcao(message):

    chat_id=message.from_user.id
    
    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    lista=df[tab_dict[comando]][col_name[comando]].unique().tolist()

    markup=InlineKeyboardMarkup(lista,call_back=callback_dict[comando])

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    bot.send_message(chat_id=chat_id,text=f'{msg} escolha uma das opções abaixo:',reply_markup=markup)

    pass

def CommandsMenu():

    bot.delete_my_commands()
    
    bot.set_my_commands([

        types.BotCommand(command=str(comando),description=str(descricao)) for comando,descricao in commands_dict.items()
    ])

    bot.set_my_commands(bot.get_my_commands())

    pass

def Memoria(chat_id):
    
    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    temp_df=temp_df.loc[temp_df['ChatID']==chat_id]

    return temp_df

    pass

def ReplyKeyboardMarkup(lista: list):

    markup=types.ReplyKeyboardMarkup(row_width=1)

    for l in lista:

        markup.add(

            types.KeyboardButton(text=l)

        )

        pass

    return markup

    pass

def InlineKeyboardMarkup(lista: list,call_back: int):

    markup=types.InlineKeyboardMarkup(row_width=1)

    for l in lista:

        markup.add(

            types.InlineKeyboardButton(text=l,callback_data=f'{str(call_back)}/{l}')
        )

        pass

    return markup    

    pass

def DataConverte(data):

    return datetime.strftime(data,'%d/%m/%Y')

    pass

def Voice(mensagem):

    engine=pyttsx3.init()

    caracteres=len([l for l in mensagem])
   
    rate=engine.getProperty('rate')
    velocidade=caracteres-rate if (caracteres-rate)>0 else rate+caracteres
    engine.setProperty('rate',velocidade)
    engine.save_to_file(mensagem,'audio.mp3')
    #engine.say(mensagem)
    engine.runAndWait()

    temp_path=os.path.join(os.getcwd(),'audio.mp3')

    return temp_path

    pass

def RemoverEspaco(val):

    return str(val).strip()

    pass

def Start():

    while True:

        try:
           
            print('BOT Telegram conectado!')

            bot.polling()

            pass

        except Exception as erro:

            print('BOT Telegram desconectado!')

            Start()          

            pass

        pass

    pass

if __name__=='__main__':

    

    pass