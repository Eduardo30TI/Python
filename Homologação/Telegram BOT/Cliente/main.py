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

#TOKEN_PROD
#TOKEN
TOKEN=config('TOKEN_PROD')

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
    
    SELECT * FROM netfeira.vw_etapa_ped
    
    """,

    'MIX':

    """
    
    SELECT * FROM netfeira.vw_mixcliente
    
    """

}


commands_dict={ 
    '/titulos': 'Títulos em aberto',
    '/pedidos': 'Acompanhamento de pedidos',
    '/mix':'MIX do cliente'

    
}

start={
    '/titulos': 'Opcao',
    '/pedidos': 'Historico',
    '/mix':'MIX'


}

funcoes={
    '/titulos': 'Opcao',
    '/pedidos': 'Historico',
    '/mix':'MIX'


}

#função usando para opções
col_dict={
    '/titulos': ['Receber'],
    '/pedidos': ['Historico','Cliente'],
    '/mix':['MIX','Cliente']

}

tab_dict={
    '/titulos': 'Receber'

}

col_name={
    '/titulos': 'Status do Título'


}

callback_dict={ 
    '/titulos': 1
   

}


@bot.message_handler(commands=['start','titulos','pedidos','mix'])
def Main(message):

    CommandsMenu()

    global comando

    comando=message.text
        
    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    chat_id=message.from_user.id

    bot.delete_message(chat_id=chat_id,message_id=message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    temp_path=Path(__file__)
    temp_path=temp_path.parent.joinpath('Memória')

    Path(temp_path).mkdir(exist_ok=True)
        
    path_arq=os.path.join(temp_path.joinpath('Consolidado.xlsx'))

    arquivo=glob(path_arq)

    if len(arquivo)<=0:

        temp_df=pd.DataFrame(columns=['ChatID','Código'])

        temp_df.to_excel(path_arq,index=False,sheet_name='Chat')

        pass

    temp_df=pd.read_excel(path_arq,sheet_name='Chat')

    count=len(temp_df.loc[temp_df['ChatID']==chat_id])

    if count<=0:
        
        bot.send_message(chat_id=chat_id,text=f'{msg} por questões de segurança me informe seu CPF ou CNPJ (sem pontos e sem barra) interno para que possamos continuar.')

        bot.register_next_step_handler(message=message,callback=ValidacaoID)        

        pass

    else:

        if message.text=='/start':

            pass

        else:

            func=start[str(message.text)]
                            
            globals().get(func)(message)

            pass

        pass


    pass

@bot.callback_query_handler(func=lambda call:True)
def call_handler(message):

    chat_id=message.from_user.id
    
    conteudo=str(message.data)

    msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

    id=int(conteudo[:conteudo.find('/')])

    val=str(conteudo[conteudo.find('/')+1:])

    bot.delete_message(chat_id=chat_id,message_id=message.message.message_id)
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    match id:
        case 1:

            temp_df=Memoria(chat_id=chat_id)

            codigo=temp_df['Código'].tolist()[-1]
            
            df=sql.GetDados(querys=querys,colunas=['Cliente','Receber'])

            df['Receber']=df['Receber'].loc[(df['Receber']['ID Cliente']==codigo)&(df['Receber']['Status do Título']==val)]

            if len(df['Receber'])>0:

                qtd_titulos=Moeda.Numero(len(df['Receber']['Título'].unique().tolist()))

                soma=Moeda.FormatarMoeda(df['Receber']['Valor Líquido'].sum())

                nome=str(df['Cliente'].loc[df['Cliente']['ID Cliente']==codigo,'Nome Fantasia'].tolist()[-1]).title()

                mensagem = f'{msg}, {nome} identifiquei <strong>{qtd_titulos}</strong> títulos no nosso sistema, totalizando <strong>R$ {soma}</strong>. Lembrando que caso tenha feito o pagamento as informações serão atualizada em 7 dias úteis em nosso sistema.'

                bot.send_message(chat_id=chat_id,text=mensagem)
            else:

                bot.send_message(chat_id=chat_id,text='Não encontrei nenhuma informação no sistema.')

            pass

    pass

def ValidacaoID(message):

    chat_id=message.from_user.id

    codigo=str(message.text).upper().strip()

    temp_path=Path(__file__)

    temp_path=os.path.join(temp_path.parent.joinpath('Memória','Consolidado.xlsx'))

    temp_df=pd.read_excel(temp_path)

    df=sql.GetDados(querys=querys,colunas=['Cliente'])

    df['Cliente']['CNPJ']=df['Cliente']['CNPJ'].astype(str)

    codigo=df['Cliente'].loc[df['Cliente']['CNPJ']==codigo,'ID Cliente'].unique().tolist()[-1]

    count=len(df['Cliente'].loc[df['Cliente']['ID Cliente']==codigo])
    
    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)
    #bot.delete_message(chat_id=chat_id,message_id=message.message_id)

    if count>0:

        id_temp=temp_df.loc[temp_df['Código']==codigo,'ChatID'].tolist()
        
        if len(id_temp)>0:

            bot.send_message(chat_id=chat_id,text='Identificamos que o código desse usuário já está sendo usando em outro aparelho. Caso você desconheça essa informação entrar em contato com o administrador da plataforma.')

            bot.register_next_step_handler(message=message,callback=ValidacaoID)

            pass

        else:

            bot.send_chat_action(chat_id=message.from_user.id,action='typing')
            #bot.delete_message(chat_id=message.from_user.id,message_id=message.message_id)

            nome=str(df['Cliente'].loc[df['Cliente']['ID Cliente']==codigo,'Nome Fantasia'].tolist()[-1]).title()

            temp_df.loc[len(temp_df)]=[chat_id,codigo]

            temp_df.to_excel(temp_path,index=False,sheet_name='Chat')

            bot.send_message(chat_id=chat_id,text=f'Seja bem vindo {nome}.')

            CommandsMenu()

            pass

        pass

    else:

        bot.send_message(chat_id=chat_id,text='Usuário informado não existe no sistema!')

        bot.register_next_step_handler(message=message,callback=ValidacaoID)

        pass

    pass

def Historico(message):

    chat_id=message.from_user.id

    bot.send_message(chat_id=chat_id,text='Aguarde ...')

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    df['Historico']=df['Historico'].loc[df['Historico']['ID Cliente']==codigo]
    
    if len(df['Historico'])>0:

        nome=str(df['Historico'].loc[df['Historico']['ID Cliente']==codigo,'Nome Fantasia'].tolist()[-1]).title()

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        total=Moeda.FormatarMoeda(df['Historico']['Total Venda'].sum())

        dt_max=DataConverte(df['Historico']['Data de Faturamento'].max())

        dt_etapa=DataConverte(df['Historico']['Data da Etapa'].max(),hora=True)

        etapa=str(df['Historico']['Etapa'].unique().tolist()[-1]).capitalize()

        df['Consolidado']=df['Historico'].groupby(['Produto'],as_index=False).agg({'Qtde':'sum'})

        df['Consolidado']['Info']=df['Consolidado'].apply(lambda info: f'{str(info["Produto"]).capitalize()} - Qtde: {Moeda.Numero(info["Qtde"])} unidade(s)',axis=1)

        mensagem=f'{msg} <strong>{nome}</strong> identifiquei que sua última compra foi {dt_max} no valor de R$ {total}.\n\nStatus do pedido: {etapa} - Data e hora: {dt_etapa}\n.'

        mensagem+='\n.'.join([l for l in df['Consolidado']['Info'].unique().tolist()])

        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:

        bot.send_message(chat_id=chat_id,text='Não encontrei nunhum pedido realizado em nosso sistema.')

        pass

    pass

def MIX(message):

    chat_id=message.from_user.id

    bot.send_message(chat_id=chat_id,text='Aguarde ...')

    temp_df=Memoria(chat_id=chat_id)

    codigo=temp_df['Código'].tolist()[-1]

    df=sql.GetDados(querys=querys,colunas=col_dict[comando])

    bot.send_chat_action(chat_id=chat_id,action='typing',timeout=espera)

    df['MIX']=df['MIX'].loc[df['MIX']['ID Cliente']==codigo]
    
    if len(df['MIX'])>0:

        nome=str(df['Cliente'].loc[df['Cliente']['ID Cliente']==codigo,'Nome Fantasia'].tolist()[-1]).title()

        msg='Bom dia' if datetime.now().hour<12 else 'Boa tarde'

        mix=Moeda.Numero(df['MIX']['SKU'].count())

        mensagem=f'{msg} <strong>{nome}</strong> identifiquei que você já comprou em nosso sistema {mix} produto(s).\n'

        for l in df['MIX']['Positivado'].unique().tolist():

            mensagem+=f'\n{str(l).capitalize()}:\n.'

            mensagem+='\n.'.join([str(l).capitalize() for l in df['MIX'].loc[df['MIX']['Positivado']==l,'Produto'].unique().tolist()])

            pass

        bot.send_message(chat_id=chat_id,text=mensagem)

        pass


    else:

        bot.send_message(chat_id=chat_id,text='Não encontrei nunhum pedido realizado em nosso sistema.')

        pass

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

def DataConverte(data,hora=False):

    data=datetime.strftime(data,'%d/%m/%Y') if hora==False else datetime.strftime(data,'%d/%m/%Y %H:%M:%S')

    return data

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

    Start()

    pass