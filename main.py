import json
import requests
from time import sleep
import random

hue_user_id = "YGdRHVAyssUU0YNjVusxiqnnjAVg3Ug1GDY7--jD"
hue_bridge_ip = "192.168.1.17"
hue_url = "http://"+hue_bridge_ip+"/api/"+hue_user_id+"/lights"
party = False

hue_request = {"turn_off":{"on":False},
               "turn_on":{"on":True},
               "colorloop":{"effect":"colorlooop"}
               }


class HueLight:

    def get_state(self, url):
        response = http_get(url)
        state = response["state"]
        return state

    def put_state(self, state, value=0):
        payload = hue_request[state]
        http_put(self.state_url, payload)

    def put_payload(self, payload, value=0):
        http_put(self.state_url, payload)

    def __init__(self, name, url, address):
        self.name = name
        self.address = address
        self.url = url+"/"+address
        self.state_url = url+"/"+address+"/state"
        self.state = self.get_state(self.url)


def get_hue_lights(url):
    response = requests.get(url)
    content = json.loads(response.content)
    hue_lights = [HueLight(content[light]["name"],url,light) for light in content]
    return hue_lights


def http_get(url):
    response = requests.get(url)
    data = json.loads(response.content)
    return data

def http_put(url, payload):
    payload_json = json.dumps(payload)
    response = requests.put(url, data=payload_json)

def find_changes(a, b):
    changes = {}
    for light in a["lights"]:
        for entry in a["lights"][light]["state"]:
            if a["lights"][light]["state"][entry] != b["lights"][light]["state"][entry]:
                changes[str("light_"+light+"_"+entry)] = a["lights"][light]["state"][entry]
    for sensor in a["sensors"]:
        for entry in a["sensors"][sensor]["state"]:
            if a["sensors"][sensor]["state"][entry] != b["sensors"][sensor]["state"][entry] and entry != "lastupdated":
                changes[str("sensor_"+sensor+"_"+entry)] = a["sensors"][sensor]["state"][entry]
    return changes

hue_lights = get_hue_lights(hue_url)

# tts = gTTS(text='Good morning', lang='en')
# tts.save("good.mp3")
# os.system("good.mp3")

data = http_get("http://192.168.1.17/api/YGdRHVAyssUU0YNjVusxiqnnjAVg3Ug1GDY7--jD")
last_data = data
while True:
    data = http_get("http://192.168.1.17/api/YGdRHVAyssUU0YNjVusxiqnnjAVg3Ug1GDY7--jD")
    changes = find_changes(data, last_data)
    if changes:
        for change in changes:
            print(change + " = " + str(changes[change]))

        if "sensor_9_buttonevent" in changes and changes["sensor_9_buttonevent"] == 1001:
            del changes["sensor_9_buttonevent"]
            party = not party

        if "sensor_11_presence" in changes and changes["sensor_11_presence"]:
            if not hue_lights[0].state["on"]:
                payload = {"ct":400,
                           "bri":90,
                           "transitiontime":22,
                           "on":True}
                http_put(hue_lights[0].state_url, payload)

    if party:
        for light in hue_lights:
            payload = {"bri": random.randint(150, 254),
                       "sat": random.randint(150, 254),
                       "hue": random.randint(1, 65534),
                       "transitiontime": 0
                       }
            payload_json = json.dumps(payload)
            light.put_payload(payload)

    last_data = data
    sleep(0.1)
