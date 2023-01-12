import telebot
from telebot import types
from TOKEN import TOKENAPI
from Acesso import Login
from Query import Query
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from glob import glob

#configuração do ambiente

s=Login()

sql=Query(s.usuario,s.senha,s.database,s.server)

TOKENS=TOKENAPI()

bot=telebot.TeleBot(token=TOKENS.token,parse_mode='HTML')

querys={

    'Vendedor':

    """
    
    SELECT LTRIM(RTRIM([ID Vendedor])) AS [ID Vendedor],Vendedor
    FROM netfeira.vw_vendedor
    WHERE [Status do Vendedor]='ATIVO'
    
    """,
    'Produto':

    """
    
    SELECT * FROM netfeira.vw_produto
    
    """
}

#funções principais

@bot.message_handler(commands=['start'])
def Main(message):

    bot.send_chat_action(chat_id=message.from_user.id,action='typing')
    bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)

    mensagem='Informe o código do vendedor para que possamos habilitar o menu:'
    
    bot.send_message(chat_id=message.from_user.id,text=mensagem)
    bot.register_next_step_handler(message=message,callback=Validar)
        
    pass


def Validar(message):

    global id

    df=sql.CriarTabela(kwargs=querys)

    id=str(message.text).strip().upper()

    cont=len(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==id,'ID Vendedor'].unique().tolist())

    if cont>0:

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        nome=str(df['Vendedor'].loc[df['Vendedor']['ID Vendedor']==id,'Vendedor'].values[-1]).title()

        mensagem=f'{msg} <b>{nome}</b> tudo bem, em que posso ajudar?'

        bot.send_chat_action(chat_id=message.from_user.id,action='typing')

        #menu
        opc={'Foto':'callfoto'}

        markups=types.InlineKeyboardMarkup()

        for op,func in opc.items:

            markups.add(

                types.InlineKeyboardButton(text=op,callback_data=func),row_width=1
            )

            pass

        bot.send_message(chat_id=message.from_user.id,text=mensagem,reply_markup=markups)
        
        pass

    else:

        mensagem=f'Código informado invalido!'

        bot.send_chat_action(chat_id=message.from_user.id,action='typing')
        bot.send_message(chat_id=message.from_user.id,text=mensagem)

        
        pass

    pass

def Main()


if __name__=='__main__':

    bot.polling()

    pass