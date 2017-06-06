import requests
import json
from pprint import pprint
from datetime import datetime


class Client:
    def __init__(self, token):
        self.token = token

    def getRooms(self, criteria):

        # pprint(criteria)
        url = 'https://app.didattica.polito.it/aule_libere.php'
        payload = {
            "regID": self.token
        }
        date_param = criteria.get('date')
        time_param = criteria.get('time')
        if date_param:
            payload['giorno'] = date_param
        else:
            # provide current day
            payload['giorno'] = datetime.now().strftime('%d/%m/%Y')

        if time_param:
            payload['ora'] = time_param
        else:
            # provide current time
            payload['ora'] = datetime.now().strftime('%H:%M:%S')

        response = requests.post(
            url, data={'data': json.dumps(payload)}).json()

        res_data = response.get('data')
        if not res_data:
            # not ok
            return None

        return res_data
