import json
import os
import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint

import wit_client
import polito_client


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        intent, entities = ent_extractor.parse(msg['text'])

        pprint(intent)
        pprint(entities)
        if intent:
            if intent['value'] == 'greetings':
                bot.sendMessage(chat_id, 'ciao!')

            elif intent['value'] == 'info':
                bot.sendMessage(
                    chat_id, 'chiedimi informazioni sulle aule libere')

            elif intent['value'] == 'search_rooms':
                datetime = entities.get('datetime')
                location = entities.get('location')
                loading_string = 'Sto cercando aule '
                if datetime:
                    if not datetime.get('value'):
                        # if this is an interval
                        datetime = datetime['from']
                    date_param = datetime['value'].split('T')[0]
                    time_param = datetime['value'].split('T')[1].split('+')[0]
                    loading_string += ' il giorno ' + date_param + ' ora ' + time_param

                else:
                    date_param = None
                    time_param = None

                if location:
                    loading_string += ' in ' + location['value']

                bot.sendMessage(chat_id, loading_string)

                result = data_provider.getRooms(
                    {'date': date_param, 'time': time_param})
                # pprint(result)
                all_rooms = result['aule_libere']
                for area, rooms in all_rooms.items():
                    # key is an area, value a list of rooms
                    if location:
                        if not location['value'].lower() in area.lower():
                            continue

                    res = ''
                    for room in rooms:
                        res += '    ' + room['nome_aula']

                    bot.sendMessage(chat_id, area + ': ' + res)

            else:
                bot.sendMessage(chat_id, 'intento ' + intent['value'])

        else:
            bot.sendMessage(chat_id, 'non ti capisco')


bot = telepot.Bot(os.environ['TELEGRAM_TOKEN'])
ent_extractor = wit_client.Extractor(os.environ['WIT_TOKEN'])
data_provider = polito_client.Client(os.environ['POLITO_TOKEN'])

bot.message_loop(handle)
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
