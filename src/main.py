from microdot import Microdot, Response
from network import WLAN, AP_IF

ap_if = WLAN(AP_IF)
ap_if.active(True)
ap_if.config(essid='ESP32', password='12345678')
host = None

if ap_if.active():
    host = ap_if.ifconfig()[0]
    print('Access Point started with IP:', host)
else:
    print('Failed to start Access Point')


app = Microdot()
# Response.default_content_type = 'text/html'

@app.route('/')
def index(request):
    with open('index.html', 'r') as file:
        html = file.read()

    for key, value in [('miconName', 'ESP32'), ('host', host)]:
        html = html.replace('{{' + key + '}}', value)

    print(html)
    return Response(body=html, headers={'Content-Type': 'text/html'})

@app.route('/get_status')
def get_status(request):
    print('Request received:', request.method, request.url, request.headers)
    return Response(body='{"status": "OK"}', headers={'Content-Type': 'application/json'})


app.run(host, port=80, debug=True)