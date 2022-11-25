import machine
import socket
import network
import time
import ubinascii
from wifi_pw import secrets

ssid = secrets['ssid']
password = secrets['pw']

led=machine.Pin('LED',machine.Pin.OUT)

class Servo:
    def __init__(self, MIN_DUTY=300000, MAX_DUTY=2300000, pin=7, freq=50):
        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY
        
    def rotateDeg(self, deg):
        if deg < 0:
            deg = 0
        elif deg > 180:
            deg = 180
        duty_ns = int(self.MAX_DUTY - deg * (self.MAX_DUTY-self.MIN_DUTY)/180)
        self.pwm.duty_ns(duty_ns)

servo1 = Servo(pin=0)
servo2 = Servo(pin=7)
deg1=0
deg2=0

ssid = secrets['ssid']
password = secrets['pw']
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid,password)


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
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    try:
        
        conn, addr = s.accept()
        
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        request = str(request)
        
        index1 = request.find('servo1=') + len('servo1=')
        
        #Parse int
        try:
            if request[index1].isdigit():
                offset = 1
                if request[index1+1].isdigit():
                    offset = 2
                    if request[index1+2].isdigit():
                        offset = 3
                deg1 = int(request[index1:index1+offset])
                print(deg1)
                led.value(0)
                
            
            index2 = request.find('servo2=') + len('servo2=')
            
            #Parse int
            if request[index2].isdigit():
                offset = 1
                if request[index2+1].isdigit():
                    offset = 2
                    if request[index2+2].isdigit():
                        offset = 3
                deg2 = int(request[index2:index2+offset])
                print(deg2)
                
            servo1.rotateDeg(deg1)
            servo2.rotateDeg(deg2)
                
            
            # Load html and replace with current data 
            response = get_html('index.html')
        except:
            response = get_html('index.html')
            
        try:
            response = response.replace('slider_value1', str(deg1))
        except Exception as e:
            response = response.replace('slider_value1', '0')
            
        try:
            response = response.replace('slider_value2', str(deg2))
        except Exception as e:
            response = response.replace('slider_value2', '0')
        
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()
        led.value(1)
    except OSError as e:
        conn.close()
        s.close()
        led.value(0)
        print('Connection closed')
        break
    except (KeyboardInterrupt):
        conn.close()
        s.close()
        led.value(0)
        print('Connection closed')
        break
