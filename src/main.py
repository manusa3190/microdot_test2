from microdot import Microdot, Response
from microdot.websocket import with_websocket
from network import WLAN, STA_IF, AP_IF

from machine import Pin, Timer
import ujson

ESSID = 'ESP32'
PASSWORD = '12345678'

ap_connected_led = Pin(21, Pin.OUT)

ap_if = WLAN(AP_IF)
ap_if.active(True)
ap_if.config(essid=ESSID, password=PASSWORD)
host = ap_if.ifconfig()[0]
print('Access Point started with IP:', host)

def check_ap_connection():
    has_device = True if len(ap_if.status('stations'))>0 else False
    ap_connected_led.value(has_device) 


sta_led = Pin(22, Pin.OUT)
sta_btn = Pin(33, Pin.IN, Pin.PULL_UP)
sta_if = WLAN(STA_IF)
sta_if.active(True)
sta_if.config(reconnects=5)


if_blink_timer = Timer(0)

def if_led_blink(_):
    check_ap_connection()

    sta_led.value(sta_if.isconnected())

if_blink_timer.init(period=1000, mode=Timer.PERIODIC, callback=if_led_blink)

app = Microdot()
# Response.default_content_type = 'text/html'

@app.route('/')
def index(request):
    with open('index.html', 'r') as file:
        html = file.read()

    for key, value in [('miconName', 'ESP32'), ('host', host)]:
        html = html.replace('{{' + key + '}}', value)

    return Response(body=html, headers={'Content-Type': 'text/html'})

@app.route('/get_status')
@with_websocket
async def get_status(request, ws):
    while True:
        message = await ws.receive()
        status = sta_if.status('stations')
        res = {'code':status,'message':'接続先が見つかりません'}
        await ws.send(ujson.dumps(res))

@app.route('/scan_wifi')
@with_websocket
async def scan_wifi(request, ws):
    print('receive')
    while True:
        points = sta_if.scan()
        point_ssids = [ point[0].decode('utf-8') for point in points ]
        print(point_ssids)
        await ws.send(ujson.dumps(point_ssids))

@app.route('/try_connect', methods=['POST'])
def try_connect(request):
    # print('Request received:', request.method, request.url, request.headers, request.body)
    data = request.body.decode()
    (ssid, password) = ujson.loads(data).values()
    print('SSID:', ssid, 'Password:',password)

    try:
        sta_if.connect(ssid, password)
        sta_if.config(reconnects=5)

        if sta_if.isconnected():
            return Response(body='{"result": "Success"}', headers={'Content-Type': 'application/json'})
        else:
            return Response(body='{"result": "Failure"}', headers={'Content-Type': 'application/json'})
    except Exception as e:
        return Response(body='{"result": "Except"}', headers={'Content-Type': 'application/json'})


app.run(host, port=80, debug=True)