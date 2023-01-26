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


@bot.message_handler(content_types=['text'])
def Main(message):

    reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)

    reply_markup.add(

        types.InlineKeyboardButton(text='Start',callback_data='/start'),
        types.InlineKeyboardButton(text='Help',callback_data='/help'),row_width=1
    )

    bot.send_message(chat_id=message.from_user.id,text='Seja bem vindo',reply_markup=reply_markup)

    pass


if __name__=='__main__':

    bot.polling()

    pass