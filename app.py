import os
import re
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv

import wit_client
import polito_client

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

# load environment from file if exists
load_dotenv(find_dotenv())

app = Flask(__name__)
TOKEN = os.environ['TELEGRAM_TOKEN']  # put your token in heroku app as environment variable
SECRET = '/bot' + TOKEN
URL = os.environ['HEROKU_URL'] #  paste the url of your application

UPDATE_QUEUE = Queue()
BOT = telepot.Bot(TOKEN)

examples = '_Quali aule libere ci sono ora?_\n_Domani alle 10 dove posso andare a studiare?_\n' + \
    '\nPuoi specificare un riferimento temporale e un riferimento spaziale:\n-temporale: abbastanza generico, dovrei capirti comunque\n-spaziale: puoi dirmi di mostrarti solo alcuni risultati in una certa area del poli (ad esempio "cittadella politecnica" o altri valori che puoi vedere in un risultato non filtrato)\n' + \
    '\n_Fra due ore quali aule sono libere al lingotto?_\n' + \
    'Scrivi la domanda in modo naturale'


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if msg['text'].startswith('/'):
            # this is a command
            if msg['text'] == '/start':
                bot.sendMessage(
                    chat_id, 'Benvenuto! chiedimi informazioni sulle aule libere')
            elif msg['text'] == '/help':
                bot.sendMessage(
                    chat_id, 'Eccoti alcuni esempi di utilizzo:\n' + examples, parse_mode="Markdown")
        else:
            intent, entities = ent_extractor.parse(msg['text'])

            # pprint(intent)
            # pprint(entities)
            if intent:
                if intent['value'] == 'greetings':
                    bot.sendMessage(chat_id, 'ciao!')

                elif intent['value'] == 'info':
                    bot.sendMessage(
                        chat_id, 'chiedimi informazioni sulle aule libere. Esempi:\n' + examples, parse_mode="Markdown")

                elif intent['value'] == 'search_rooms':
                    datetime = entities.get('datetime')
                    area = entities.get('area')
                    loading_string = 'Sto cercando aule '
                    if datetime:
                        if not datetime.get('value'):
                            # if this is an interval
                            datetime = datetime['from']
                        date_param = datetime['value'].split('T')[0]
                        time_param = datetime['value'].split('T')[
                            1].split('+')[0]
                        loading_string += ' il giorno ' + date_param + ' ora ' + time_param

                    else:
                        date_param = None
                        time_param = None

                    if area:
                        loading_string += ' in ' + area['value']

                    bot.sendMessage(chat_id, loading_string)

                    result = data_provider.getRooms(
                        {'date': date_param, 'time': time_param})
                    # pprint(result)
                    all_rooms = result['aule_libere']
                    for curr_area, rooms in all_rooms.items():
                        # key is an area, value a list of rooms
                        if area:
                            delimiters = [' ', '_', ',', ', ', '-', '\n']
                            regex_pattern = '|'.join(
                                map(re.escape, delimiters))
                            search_filters = re.split(
                                regex_pattern, area['value'])
                            if not all(filter in curr_area.lower() for filter in search_filters):
                                continue

                        res = ''
                        for room in rooms:
                            res += '    ' + room['nome_aula']

                        bot.sendMessage(chat_id, curr_area + ': ' + res)

                else:
                    bot.sendMessage(chat_id, 'intento ' + intent['value'])

            else:
                bot.sendMessage(chat_id, 'non ti capisco')
    else:
        bot.sendMessage(chat_id, 'non supporto ancora questo tipo di messaggi')


bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
ent_extractor = wit_client.Extractor(os.environ['WIT_TOKEN'])
data_provider = polito_client.Client(os.environ['POLITO_TOKEN'])

BOT.message_loop({'chat': handle}, source=UPDATE_QUEUE)  # take updates from queue

@app.route(SECRET, methods=['GET', 'POST'])
def pass_update():
    UPDATE_QUEUE.put(request.data)  # pass update to bot
    return 'OK'

# set the telegram webhook

webhook_url = URL + SECRET

# https://github.com/nickoala/telepot/issues/165#issuecomment-256056446
if webhook_url != BOT.getWebhookInfo()['url']:
    BOT.setWebhook(webhook_url)

