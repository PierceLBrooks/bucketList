
import os
import sys
import copy
import json
import time
import logging
import threading
import traceback
import pscreen as ps

class Context(object):
    def __init__(self):
        self.thread = None
        self.lock = threading.Lock()
        self.flag = True
        self.query = ""
        self.output = []
        self.advance = 0
        self.state = 0
        self.cities = {}
        self.congratulations = 0
        self.attractions = {}
        self.city = "Circleville"
        self.location = "your apartment"
        self.money = 100
        self.hours = 8
        self.minutes = 0
        with open(os.path.join(os.getcwd(), "cities.json"), "r") as descriptor:
            content = descriptor.read()
            cities = json.loads(content)
            for city in cities:
                self.cities[city["name"]] = city

context = None

def process(query):
    global context
    stage = 0
    #print(str(context.output))
    context.previous = context.state
    if not (context.previous == context.state):
        return stage
    output = []
    if (context.state == 0):
        output.append("You are being pursued by an assassin.")
        output.append("You must visit the following attractions on your bucket list before the assassin kills you:")
        for city in context.cities:
            for location in context.cities[city]["locations"]:
                if (location["attraction"]):
                    context.attractions[location["name"]] = False
                    output.append(" * "+location["name"])
        output.append("")
        context.state = 1
    elif (context.state == 1):
        if ((context.location in context.attractions) and not (context.attractions[context.location])):
            context.attractions[context.location] = True
            output.append("Congratulations! You have visited a new attraction!")
            context.congratulations += 1
        output.append("You are at "+context.location+".")
        output.append("You have "+str(context.money)+" bucks in your wallet.")
        output.append("It is "+str((context.hours%13)+int(context.hours/13))+":"+("0" if (context.minutes < 10) else "0")+str(context.minutes)+" "+("P" if (context.hours >= 12) else "A")+"M.")
        context.state = 2
        stage = 1
    elif (context.state == 2):
        #print("\""+query+"\"")
        if not (len(query) == 0):
            if ("a" in query):
                if (context.congratulations > 0):
                    output.append("You have already visited the following attractions:")
                    for attraction in context.attractions:
                        context.output.append(" * "+attraction)
                else:
                    output.append("You have not visited any attractions yet.")
                query = ""
            if (len(query) == 0):
                context.state = 1
                stage = 1
    if (len(output) > 0):
        context.lock.acquire()
        output.append("")
        context.output += output
        context.advance = int(len(output)/2)
        context.lock.release()
    return stage

def handle(argument):
    global context
    print(str(argument))
    query = ""
    while (True):
        stage = process(query.lower())
        query = ""
        context.lock.acquire()
        if not (context.flag):
            context.lock.release()
            break
        query += context.query
        context.query = ""
        context.lock.release()
        if (len(query) == 0):
            continue
        print(query)

def run(size):
    global context
    width = size[0]
    height = size[1]
    limit = 100
    column = 32
    rows = min(int(int(height)/int(column)), 16)
    context = Context()
    context.thread = threading.Thread(target=handle, args=tuple([None]))
    context.thread.start()
    output = []
    query = ""
    queries = ["w", "s", "b", "t", "a"]
    presses = {}
    lines = [""]
    line = 0
    buttonsNext = [False, False, False]
    buttonsPrevious = [False, False, False]
    backgroundColor = tuple([128, 128, 128])
    textColor = tuple([0, 0, 0, 255])
    scrollColor = tuple([255, 255, 255, 255])
    first = 10
    quit = False
    previous = None
    mouse = None
    ps.FontSelect()
    while (True):
        mouse = ps.MouseGetPosition()
        mouse = tuple([float(mouse[0]), float(mouse[1])])
        buttonsPrevious[0] = buttonsNext[0]
        buttonsPrevious[1] = buttonsNext[1]
        buttonsPrevious[2] = buttonsNext[2]
        buttonsNext[0] = ps.MouseGetButtonL()
        buttonsNext[1] = ps.MouseGetButtonM()
        buttonsNext[2] = ps.MouseGetButtonR()
        if (ps.KeyIsPressed("escape")):
            print("quit")
            quit = True
        for i in range(len(queries)):
            if (ps.KeyIsPressed(queries[i])):
                query += queries[i]
        for press in presses:
            if not (press == query):
                presses[press] = False
        if not (len(query) == 0):
            if not (query in presses):
                presses[query] = False
            if (presses[query]):
                query = ""
            else:
                presses[query] = True
        #print(str(presses))
        if not (len(query) == 0):
            if ("t" in query):
                line = len(lines)-1
                query = ""
            if ("b" in query):
                line = len(lines)-1
                query = ""
            if ("w" in query):
                line -= 1
                if (line < 0):
                    line = 0
                query = ""
            if ("s" in query):
                if (line < min(rows, len(lines))-1):
                    line = min(rows, len(lines))-1
                line += 1
                if (line >= len(lines)):
                    line = len(lines)-1
                query = ""
            if not (len(query) == 0):
                context.lock.acquire()
                context.query += query
                query = ""
                context.lock.release()
        context.lock.acquire()
        if (context.advance > 0):
            if (abs(line-len(lines)) < context.advance*2):
                line += context.advance
                if (line >= len(lines)):
                    line = len(lines)-1
                context.advance = 0
        output += context.output
        context.output = []
        context.lock.release()
        if not (len(output) == 0):
            lines.append(output[0])
            if (len(lines) > limit):
                lines = lines[1:]
            output = output[1:]
        ps.ClearScreen(backgroundColor)
        if (quit):
            break
        #print(str(lines))
        if (first > 0):
            first -= 1
            line = len(lines)-1
        ps.Rectangle(int(column/4), column, int(column/2), column*(rows+1), textColor, 0)
        ps.Rectangle(int(column/4), int((float(line)/float(len(lines)))*float(column*rows))+column, int(column/2), int((float(line)/float(len(lines)))*float(column*rows))+(column*2), scrollColor, 0)
        for i in range(max(line-rows, 0), max(line+1, min(rows, len(lines)))):
            if (len(lines[i]) == 0):
                continue
            x = column
            y = column+((i-max(line-rows, 0))*column)
            #print(str(x)+" "+str(y))
            ps.FontWrite(int(x), int(y), lines[i], textColor)
        ps.UpdateScreen()
    context.lock.acquire()
    context.flag = False
    context.lock.release()
    context.thread.join()
    return 0

def launch(arguments):
    global context
    result = None
    size = tuple([1280, 720])
    ps.LoadScreen(size)
    try:
        result = run(size)
    except:
        logging.error(traceback.format_exc())
        result = None
    print(str(result))
    ps.UnloadScreen()
    if not (context == None):
        context.lock.acquire()
        if (context.flag):
            context.flag = False
            context.lock.release()
            context.thread.join()
        else:
            context.lock.release()
    if not (result == 0):
        return False
    return True

if (__name__ == "__main__"):
    print(str(launch(sys.argv)))
