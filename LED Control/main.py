import machine
import socket
import network
import time
import ubinascii
from wifi_pw import secrets

ssid = secrets['ssid']
password = secrets['pw']
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid,password)

 
# rgb led
led=machine.Pin('LED',machine.Pin.OUT)

# Wait for connect or fail
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    led.value(1)
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print('mac = ' + mac)
 

# Function to load in html page    
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()
        
    return html

# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


print('Listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        # print(r)
        
        r = str(r)
        led_on = r.find('?led=on')
        led_off = r.find('?led=off')
        print('led_on = ', led_on)
        print('led_off = ', led_off)
        if led_on ==7:
            print('LED ON')
            led.value(1)
            
        if led_off == 7:
            print('LED OFF')
            led.value(0)
            
        response = get_html('index.html')
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
    except OSError as e:
        cl.close()
        s.close()
        machine.reset()
        print('Connection closed')
    except (KeyboardInterrupt):
        machine.reset()
        print('Connection closed')
