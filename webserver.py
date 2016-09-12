import tornado
import tornado.websocket
from datetime import timedelta
import datetime, sys, time
from pprint import pprint
import json
#import bleach
#import time

# DB
#from bson.objectid import ObjectId
#from bson.json_util import dumps, loads
#from pymongo import MongoClient
#import json
#client = MongoClient("localhost", 27017)
#db = client.sinmensaje

clients = []

import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
print(ports)
arduino_port = ""
for p in ports:
    print (p)
    if "SNR=95333353037351D071B0" in p[2]:
        print ("This is an Arduino!")
        arduino_port = p[0]

if arduino_port == "":
    print ("Arduino not found")
    sys.exit("where is it?")

import serial
ser = serial.Serial(arduino_port, 9600) # Establish the connection on a specific por

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    tt = datetime.datetime.now()
    def check_origin(self, origin):
        #print "origin: " + origin
        return True
    # the client connected
    def open(self):
        print ("New client connected")
        self.write_message("You are connected")
        clients.append(self)
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.test)

    def test(self):
        try:
            info = {}
            try:
                text = ser.readline() # Read the newest output from the Arduino
                #print(text)
                values = str(text).split(" ")
                info = {
                    "potencia"  : float(values[2]),
                    "tension"   : float(values[4]),
                    "corriente" : float(values[6]),
                    "estado"    : int(values[8]),
                    "timestamp" : time.time()
                }
            except Exception as e:
                #print(info)
                info = {
                    "potencia"  : float("0.0"),
                    "tension"   : float("0.0"),
                    "corriente" : float("0.0"),
                    "estado"    : -1,
                    "timestamp" : time.time()
                }
                #raise(e)
            #print(info)
            self.write_message(info)
        except Exception as e:
            print ("restartplease")
            self.write_message("restartplease")
            #raise(e)
        else:
            tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=0.1),
                                                         self.test)

    # the client sent the message
    def on_message(self, message):
        print ("message: " + message)
        try:
            message = json.loads(message)
            #pprint(message)

            if "relay1" in message:
                if (message['relay1'] == 1):
                    ser.write("1\r".encode())
                elif (message['relay1'] == 0):
                    ser.write("0\r".encode())

            #if "min1" in message:
                #if (message['min1'] >= 0 and message['min1'] <= 30):
                    #ser.write(chr(message['min1']))

            if "max1" in message:
                if (message['max1'] >= 0 and message['max1'] <= 30):
                    ser.write((chr(message['max1']+100)+"\r").encode())

        except Exception as e:
            print ("cant send value to arduino")
            #raise(e)
        #self.write_message(message)

    # client disconnected
    def on_close(self):
        print ("Client disconnected")
        clients.remove(self)

#def send_message_to_clients():
#    try:
#        "algo?"
#
#        datos = db.received.find()
#
#        #read_my_data()
#        for client in clients:
#            print "huevada"
#            #self.write_message("You are connected")
#    finally:
#        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1),
#                                                     send_message_to_clients)

socket = tornado.web.Application([(r"/websocket", WebSocketHandler),])
if __name__ == "__main__":
    socket.listen(8888)
    #tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=3),
    #                                             send_message_to_clients)
    tornado.ioloop.IOLoop.instance().start()
