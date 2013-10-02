#!/usr/bin/env python
# -*- coding: latin-1 -*-

#############################################
#             printerstatus.py              #
#                                           #
#   Written by Øystein Røysland Sørlie      #
#           o.r.sorlie@hf.uio.no            #
#                                           #
#               July 2011                   #
#                                           #
#############################################

import sys, os, time, getopt, netsnmp

usage = "usage: " + str(sys.argv[0]) + " [-h] [-d] printers"

helpMessage = "Help for " + str(sys.argv[0]) + ";\n\
        -a show all"

class bcolors:
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    endC = '\033[0m'

    def disable(self):
        self.header = ''
        self.blue = ''
        self.green = ''
        self.yellow = ''
        self.red = ''
        self.endC = ''

"""
Some constants
"""
var_model = netsnmp.Varbind('.1.3.6.1.2.1.25.3.2.1.3')
var_display = netsnmp.Varbind('.1.3.6.1.2.1.43.16.5.1.2')
var_accessories = netsnmp.Varbind('.1.3.6.1.2.1.43.11.1.1.6')
var_acc_max = netsnmp.Varbind('.1.3.6.1.2.1.43.11.1.1.8')
var_acc_current = netsnmp.Varbind('.1.3.6.1.2.1.43.11.1.1.9')
var_tray_name = netsnmp.Varbind('.1.3.6.1.2.1.43.8.2.1.13')
var_tray_status = netsnmp.Varbind('.1.3.6.1.2.1.43.8.2.1.11')

community = 'public'
ver = 1


def getInfo(printer):

    model = netsnmp.snmpwalk(var_model, Version=ver, DestHost=printer, Community=community)[0]
    statuses = netsnmp.snmpwalk(var_display, Version=ver, DestHost=printer, Community=community)
    if statuses[1]:
        status = statuses[0] + " " + statuses[1]
    else:
        status = statuses[0]
    tonermax = int(netsnmp.snmpwalk(var_acc_max, Version=ver, DestHost=printer, Community=community)[0])
    tonercurrent = int(netsnmp.snmpwalk(var_acc_current, Version=ver, DestHost=printer, Community=community)[0])
    toner = 100.0 * tonercurrent / tonermax
    kitmax = int(netsnmp.snmpwalk(var_acc_max, Version=ver, DestHost=printer, Community=community)[1])
    kitcurrent = int(netsnmp.snmpwalk(var_acc_current, Version=ver, DestHost=printer, Community=community)[1])
    kit = 100.0 * kitcurrent / kitmax
    traynames = netsnmp.snmpwalk(var_tray_name, Version=ver, DestHost=printer, Community=community)
    traystatuses = netsnmp.snmpwalk(var_tray_status, Version=ver, DestHost=printer, Community=community)
    
    return model, status, toner, kit, traynames, traystatuses

def printStatus(show, printer, model, status, toner, kit, trayname, traystatus):

    if show == 'all':
        os.system('clear')
        for i in range(0, len(printer)):
            print bcolors.header + "Printer:  " + printer[i] + bcolors.endC + " - " + model[i]
            print "Status:   " + status[i]
            if toner[i] <= 1:
                print "Toner:    " + bcolors.red + "%d%%" % toner[i] + bcolors.endC
            elif 1 < toner[i] <= 10:
                print "Toner:    " + bcolors.yellow + "%d%%" % toner[i] + bcolors.endC
            else:
                print "Toner:    " + bcolors.green + "%d%%" % toner[i] + bcolors.endC
            if kit[i] < 1:
                print "Fuser:    " + bcolors.red + "%d%%" % kit[i] + bcolors.endC
            elif 1 <= kit[i] <= 5:
                print "Fuser:    " + bcolors.yellow + "%d%%" % kit[i] + bcolors.endC
            else:
                print "Fuser:   " + bcolors.green + " %d%%" % kit[i] + bcolors.endC
            for j in range(1, len(trayname[i])):
                if traystatus[i][j] in '0':
                    print bcolors.blue + trayname[i][j] + bcolors.endC + ":   " + bcolors.green + "OK" + bcolors.endC
                else:
                    print bcolors.blue + trayname[i][j] + bcolors.endC + ":   " + bcolors.red + "Empty" + bcolors.endC
                #print bcolors.blue + trayname[i][j] + bcolors.endC + ":     " + traystatus[i][j]
            print ""


def runStuff(printers, delay, show):

    while True:

        arrModel = []
        arrStatus = []
        arrToner = []
        arrKit = []
        arrTrays = []
        arrTrayStatus = []

        for printer in printers:
            model, status, toner, kit, traynames, traystatuses = getInfo(printer)
            arrModel.append(model)
            arrStatus.append(status)
            arrToner.append(toner)
            arrKit.append(kit)
            arrTrays.append(traynames)
            arrTrayStatus.append(traystatuses)

        printStatus(show, printers, arrModel, arrStatus, arrToner, arrKit, arrTrays, arrTrayStatus)
        time.sleep(delay)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'hc:aed:', ['help', 'config=', 'all', 'error', 'delay='])
    else:
        print usage; sys.exit(1)

    delay = 30
    show = 'all'
    printers = args

    for option, value in options:
        if option in ('-h', '--help'):
            print helpMessage; sys.exit(0)
        elif option in ('-a', '--all'):
            show = 'all'
        elif option in ('-e', '--error'):
            show = 'error'
        elif option in ('-d', '--delay'):
            delay = int(value)

    runStuff(printers, delay, show)
        
