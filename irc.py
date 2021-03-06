import socket
import sys
import time as Time
import os
import random
from datetime import datetime, time, timedelta
import logging

from bluetooth import BluetoothSerialPortController

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Utility:

    @staticmethod
    def print_and_log(message, type):
        if type == 'irc':
            print (bcolors.HEADER + message +  bcolors.ENDC)
        elif type == 'calm':
            print (bcolors.OKBLUE + message +  bcolors.ENDC)
        elif type == 'pog':
            print (bcolors.OKGREEN + message +  bcolors.ENDC)
        elif type == 'meter':
            print (bcolors.WARNING + message +  bcolors.ENDC)
        elif type == 'error':
            print (bcolors.FAIL + message +  bcolors.ENDC)
        logging.info(message)

class IRC:
 
    irc = socket.socket()
  
    def __init__(self):
        # Define the socket
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    def send(self, channel, msg):
        # Transfer data
        self.irc.send(bytes("PRIVMSG " + channel + " " + msg + "\n", "UTF-8"))

    def close_socket(self):
        self.irc.close()

    def open_socket(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    def connect(self, server, port, channel, botnick, botpass):
        # Connect to the server
        Utility.print_and_log("[IRC] Connecting to: " + server, type='irc')
        self.irc.connect((server, port))

        # Perform user authentication
        self.irc.send(bytes("PASS " + botpass + "\n", "UTF-8"))
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        Time.sleep(5)

        # join the channel
        self.irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))

        Utility.print_and_log('[IRC] Connected!', type='irc')

    def disconnect(self):
        self.irc.send(bytes("PRIVMSG " + "/disconnect" + "\n", "UTF-8"))
 
    def get_response(self):
        Time.sleep(1)
        # Get the response
        try:
            resp = self.irc.recv(1024).decode("UTF-8")
        except Exception as err:
            return f"[ERROR] {err}"
 
        if resp.find('PING') != -1:
            #Utility.print_and_log('[INFO] <REPLYING TO PONG>')                    
            self.irc.send(bytes('PONG :tmi.twitch.tv', "UTF-8")) 
 
        return resp

class PogMonitor:

    def __init__(self, max, channel, stream_stamp_at_script_start):
        self.q = []
        self.current_length = 0
        self.max = max
        self.irc = IRC()
        self.server = "irc.chat.twitch.tv" # Provide a valid server IP/Hostname
        self.port = 6667
        self.channel = f"#{channel}"
        self.botnick = "etxblizzard"
        self.botpass = "oauth:jw0r9l3ze7sgtz1fk4i7v0bvtn5vxk"
        self.threshold_multiplier = 2.5
        self.startTime = datetime.now()
        self.streamStartTime = datetime(year=2020, month=5, day=30, hour=info['hour'], minute=info['minute'], second=info['second'])

    def initialise_irc(self):
        self.irc.connect(self.server, self.port, self.channel, self.botnick, self.botpass)

    def reinitialise_irc(self):
        self.irc.close_socket()
        self.irc.open_socket()
        self.irc.connect(self.server, self.port, self.channel, self.botnick, self.botpass)

    def pop(self):
        self.q.pop(0)
        self.current_length -= 1

    def append(self, e):
        self.q.append(e)
        self.current_length += 1
            
    def push(self, e):
        if self.full():
            self.pop()
        self.append(e)

    def full(self):
        return self.current_length == self.max

    def moving_average(self):
        return sum(self.q) / self.current_length

    def main_loop(self):
        BluetoothSerialPortController.slow()
        Utility.print_and_log(f"[INFO] Initialising IRC", type='irc')
        self.initialise_irc()
        blanks = 0
        decrease_count = 0
        local_maxima = 0

        while True:
            text = self.irc.get_response()
            message_count = text.count('PRIVMSG')
            if message_count == 0:
                if blanks < 3:
                    blanks += 1
                    continue
                Utility.print_and_log(f"[ERROR] IRC sent a blank.", type='error')
                Utility.print_and_log(f"[INFO] Reinitialising IRC...", type='irc')
                self.reinitialise_irc()
                blanks = 0
                Time.sleep(2)
                continue

            self.push(message_count)

            if self.full():
                #Utility.print_and_log(f"[INFO] MVING AVG: {self.moving_average()}; MSGCNT: {message_count}; QL: {self.current_length}")
                if message_count < local_maxima:
                    decrease_count += 1
                    if decrease_count == 3:
                        BluetoothSerialPortController.slow()
                        Utility.print_and_log(f"[METER] hype-o-meter chillin' ", type='meter')
                        local_maxima = 0
                        decrease_count = 0

                elif message_count > self.moving_average() * self.threshold_multiplier:
                    BluetoothSerialPortController.fast()

                    local_maxima = message_count

                    timeStamp = self.streamStartTime + timedelta(seconds=(datetime.now() - self.startTime).seconds)
                    #Utility.print_and_log(f"[POG] BIGPLAYTIMEBOI CLIP CLIP CLIP @: {timeStamp.time().__str__()}")
                    Utility.print_and_log(f"[POG] TWITCH CHAT JUST WENT BONKERS ", type='pog')
                    Utility.print_and_log(f"[METER] HYPE-O-METER GOIN' CRAZY ", type='meter')

                if local_maxima == 0:
                    Utility.print_and_log(f"[INFO] twitch chat is calm", type='calm')


if __name__ == '__main__':
    channel = "hiko"
    
    # Add support to scrape dynamically
    info = {"hour" : 9, "minute" : 40, "second" : 15}
    
    logging.basicConfig(filename=f'{channel}.log',level=logging.DEBUG)
    pog_monitor = PogMonitor(10, channel=channel, stream_stamp_at_script_start=info)
    pog_monitor.main_loop()

