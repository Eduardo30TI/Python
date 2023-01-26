import telebot
from TOKEN import TOKENAPI
import requests

TOKENS=TOKENAPI()

bot=telebot.TeleBot(token=TOKENS.token,parse_mode='HTML')


@bot.message_handler(commands=['start'])
def Main(message):

    bot.send_message(chat_id=message.from_user.id,text=f'Bom dia {message.from_user.first_name} digite seu cep abaixo:')

    bot.register_next_step_handler(message=message,callback=CEP)

    pass

def CEP(message):

    if(len(message.text)==8 and str(message.text).isnumeric()):

        link=f'https://viacep.com.br/ws/{message.text}/json/'

        request=requests.get(url=link)

        if(request.status_code==200):

            content=request.json()

            mensagem=f'Logradouro: {content["logradouro"]}, {content["bairro"]}, CEP: {content["cep"]} - {content["localidade"]}/{content["uf"]}'

            bot.send_message(chat_id=message.from_user.id,text=mensagem)

            pass

        else:

            bot.send_message(chat_id=message.from_user.id,text='Erro de conexão com a API')

            pass
            
        pass

    else:

        bot.send_message(chat_id=message.from_user.id,text='CEP informado invalido!')

        pass

    pass


if __name__=='__main__':

    bot.polling()

    pass