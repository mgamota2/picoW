import network
import socket
import time

import machine
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
  
ssid = "NETGEAR17"
password = 'wateryrosebud647'
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <p>Matthew Gamota</p>
            
        </body>
    </html>
"""
 
# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    led.on()
 
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
 
s = socket.socket()
s.bind(addr)
s.listen(1)
 
print('listening on', addr)
 
# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)

        request = cl.recv(1024)
        print(request)

        request = str(request)
        response = html
        
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
 
    except OSError as e:
        
        cl.close()
        led.off()
        print('connection closed')
        
led.off()