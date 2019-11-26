#!/usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################
#                                                           #
#  Zabbix-DockerMonitor-Coletor.py                          #
#                                                           #
#  Discover containers and send infos from docker stats     #
#  to Zabbix Server or Zabbix Proxy                         #
#                                                           #
#  Version 1.0                                              #
#                                                           #
#  Autor: Aldori Junior                                     #
#  aldorisantosjunior@hotmail.com                           #
#  https://github.com/AldoriJunior/ZabbixDockerMonitor      #
#                                                           #
#############################################################


import subprocess
import ast
import os
from pyzabbix import ZabbixMetric, ZabbixSender
from datetime import datetime, date
import json
import logging
import telnetlib
import socket


class DockerMonitor(object):
    '''Class for DockerMonitor'''

    def __init__(self, hostname='', zabbixserver=''):
        self.hostname = hostname
        self.zabbixserver = zabbixserver
    
    def check(self,hostname,zabbixserver):
        logging.info("Starting to check containers")

        number_cpus = os.cpu_count()
        # Get Number of vCPUs
        logging.info("Number of vCPUs: %s" % number_cpus)

        # Discover containers in Docker Stats
        # Get informations from containers
        getcontainers = subprocess.run(['docker', 'stats', '--no-stream', '--format', \
        '{\'container\':\'{{ .Container }}\',\'containername\':\'{{ .Name}}\',\'memory\':[{\'raw\':\'{{ .MemUsage }}\',\'percent\':\'{{ .MemPerc }}\'}],\'cpu\':\'{{ .CPUPerc }}\',\'NetIO\':\'{{ .NetIO}}\',\'Blockio\':\'{{ .BlockIO}}\',\'pid\':\'{{ .PIDs }}\'}'], stdout=subprocess.PIPE)
        
        # perform data processing to make list
        x = getcontainers.stdout
        x = x.decode('utf-8')
        x = x.replace("'b{", "")
        x = x.replace("\n", "")
        x = x.replace("}{", "},{")
        x = "[" + x + "]"

        logging.debug("Identified the containers: %s" % x)
        try:
            # Conversion AST to make List
            results = ast.literal_eval(x)
            logging.debug("Results of literal_eval conversion: %s" % results)

            for result in results:
                # For result (container) defined some variables
                container_id = result[u'container']
                container_pid = result[u'pid']
                container_name = result[u'containername']
                dockerinstance = container_name
                memory = result[u'memory']
                # Memory has 3 variables, usage, total and percent
                for x in memory:
                    memory = x[u'raw']
                    # memory usage is a first result
                    # memory total is a second result
                    memory_usage = memory.split(' /')[0]
                    memory_total = memory.split('/ ')[-1]
                    # here we make a conversion to bytes, to use in Zabbix 
                    # before this, for result (Kb, MiB, GiB, MB, GB), we need to make a different calc
                    if "kB" in str(memory_usage):
                        # remove string
                        memory_usage = memory_usage.replace("kB", "")
                        # make a float number
                        memory_usage = float(memory_usage)
                        # multiply results according to data type
                        memory_usage = memory_usage * 1024
                        # Make a int number with round
                        memory_usage = int(round(memory_usage))
                    if "MiB" in str(memory_usage):
                        memory_usage = memory_usage.replace("MiB", "")
                        memory_usage = float(memory_usage)
                        memory_usage = memory_usage * 1048576
                        memory_usage = int(round(memory_usage))
                    elif "GiB" in str(memory_usage):
                        memory_usage = memory_usage.replace("GiB", "")
                        memory_usage = float(memory_usage)
                        memory_usage = memory_usage * 1073741824
                        memory_usage = int(round(memory_usage))
                    if "kB" in str(memory_total):
                        memory_total = memory_total.replace("kB", "")
                        memory_total = float(memory_total)
                        memory_total = memory_total * 1024
                        memory_total = int(round(memory_total))
                    if "MiB" in str(memory_total):
                        memory_total = memory_total.replace("MiB", "")
                        memory_total = float(memory_total)
                        memory_total = memory_total * 1048576
                        memory_total = int(round(memory_total))
                    elif "GiB" in str(memory_total):
                        memory_total = memory_total.replace("GiB", "")
                        memory_total = float(memory_total)
                        memory_total = memory_total * 1073741824
                        memory_total = int(round(memory_total))
                    perc_mem = x[u'percent']
                    perc_mem = perc_mem.replace("%", "")
                    perc_mem = float(perc_mem)
                netio = result['NetIO']
                netio_input = netio.split(' /')[0]
                netio_output = netio.split('/ ')[-1]
                if "kB" in str(netio_input):
                    netio_input = netio_input.replace("kB", "")
                    netio_input = float(netio_input)
                    netio_input = netio_input * 1024
                    netio_input = int(round(netio_input))
                if "MB" in str(netio_input):
                    netio_input = netio_input.replace("MB", "")
                    netio_input = float(netio_input)
                    netio_input = netio_input * 1048576
                    netio_input = int(round(netio_input))
                elif "GB" in str(netio_input):
                    netio_input = netio_input.replace("GB", "")
                    netio_input = float(netio_input)
                    netio_input = netio_input * 1073741824
                    netio_input = int(round(netio_input))
                elif "0B" in str(netio_input):
                    netio_input = netio_input.replace("B", "")
                    netio_input = int(netio_input)
                if "kB" in str(netio_output):
                    netio_output = netio_output.replace("kB", "")
                    netio_output = float(netio_output)
                    netio_output = netio_output * 1024
                    netio_output = int(round(netio_output))
                if "MB" in str(netio_output):
                    netio_output = netio_output.replace("MB", "")
                    netio_output = float(netio_output)
                    netio_output = netio_output * 1048576
                    netio_output = int(round(netio_output))
                elif "GB" in str(netio_output):
                    netio_output = netio_output.replace("GB", "")
                    netio_output = float(netio_output)
                    netio_output = netio_output * 1073741824
                    netio_output = int(round(netio_output))
                elif "0B" in str(netio_output):
                    netio_output = netio_output.replace("B", "")
                    netio_output = int(netio_output)

                blockio = result[u'Blockio']
                blockio_input = blockio.split(' /')[0]
                blockio_output = blockio.split('/ ')[-1]
                if "kB" in str(blockio_input):
                    blockio_input = blockio_input.replace("kB", "")
                    blockio_input = float(blockio_input)
                    blockio_input = blockio_input * 1024
                    blockio_input = int(round(blockio_input))
                if "MB" in str(blockio_input):
                    blockio_input = blockio_input.replace("MB", "")
                    blockio_input = float(blockio_input)
                    blockio_input = blockio_input * 1048576
                    blockio_input = int(round(blockio_input))
                elif "GB" in str(blockio_input):
                    blockio_input = blockio_input.replace("GB", "")
                    blockio_input = float(blockio_input)
                    blockio_input = blockio_input * 1073741824
                    blockio_input = int(round(blockio_input))
                elif "0B" in str(blockio_input):
                    blockio_input = blockio_input.replace("B", "")
                    blockio_input = int(blockio_input)
                if "kB" in str(blockio_output):
                    blockio_output = blockio_output.replace("kB", "")
                    blockio_output = float(blockio_output)
                    blockio_output = blockio_output * 1024
                    blockio_output = int(round(blockio_output))
                if "MB" in str(blockio_output):
                    blockio_output = blockio_output.replace("MB", "")
                    blockio_output = float(blockio_output)
                    blockio_output = blockio_output * 1048576
                    blockio_output = int(round(blockio_output))
                elif "GB" in str(blockio_output):
                    blockio_output = blockio_output.replace("GB", "")
                    blockio_output = float(blockio_output)
                    blockio_output = blockio_output * 1073741824
                    blockio_output = int(round(blockio_output))
                elif "0B" in str(blockio_output):
                    blockio_output = blockio_output.replace("B", "")
                    blockio_output = int(blockio_output)
                cpu = result[u'cpu']
                cpu = cpu.replace("%", "")
                cpu = float(cpu)
                cpu_real = cpu / number_cpus
                cpu_real = float("{0:.2f}".format(cpu_real))
                try:
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',container_id]',container_id)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',container_pid]',container_pid)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',container_name]',container_name)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',memory_usage]',memory_usage)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',memory_total]',memory_total)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',perc_mem]',perc_mem)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',cpu]',cpu)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',cpu_real]',cpu_real)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',netio_input]',netio_input)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',netio_output]',netio_output)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',blockio_input]',blockio_input)
                    self._send_data(hostname,'docker.instance['+dockerinstance.upper()+',blockio_output]',blockio_output)
                    logging.info("Data Sent to Zabbix Server Successfully!")
                except:
                    logging.warning("Unable to send data to Zabbix Server!")
        except:
            logging.debug("Conversion fail in Literal_Eval")

        


    def _send_data(self, hostname, key, value):

        '''Send the queue data to Zabbix.'''
        packet = [
        ZabbixMetric(hostname, key, value)
        ]
        logging.debug("Packet to Send: %s" % (packet))
        try:
            ZabbixSender(zabbix_server=zabbixserver, use_config=False).send(packet)
            logging.debug("Finished sending data to key %s" % (key))
        except Exception as e:
            logging.warning("Unable to send data to Zabbix Server!")
            logging.warning("Error founded: %s" % e)


def main():
    global zabbixserver, hostname

    # Zabbix Server or Zabbix Proxy
    zabbixserver =  "10.10.10.10"
    # Server hostname, the same of Zabbix Frontend
    hostname = "SRVAPP-1"
    # LogLevel
    LogLevel = "INFO"
    # Log Directory
    DirLog = "/var/log/DockerMonitor"

    # creat a log direct if doesn't exists
    if not os.path.exists(DirLog):
        os.makedirs(DirLog)
    
    date = datetime.now().strftime("%Y-%m-%d")
    filelog = DirLog + "/DockerMonitor" + date + ".log"
    logging.basicConfig(filename=filelog, level=logging.getLevelName(LogLevel), format='%(asctime)s %(levelname)s: %(message)s')
    logging.info("")
    logging.info("####################################")
    logging.info("##### STARTING A NEW EXECUTION #####")
    logging.info("####################################")
    logging.info("")
    logging.info("ZabbixServer = %s" % zabbixserver)
    logging.info("Server Hostname = %s" % hostname)
    logging.info("Log directory = %s" % DirLog)
    logging.info("LogLevel = %s" % LogLevel)
    logging.info("")
    
    try:
        TEMPOTIMEOUT = 3
        telnetlib.Telnet(zabbixserver, 10051, TEMPOTIMEOUT)
        run = DockerMonitor(hostname=hostname, zabbixserver=zabbixserver)
        run.check(hostname, zabbixserver)
    except socket.timeout:
        logging.info("Initial connection test with Zabbix Proxy / Server returned failed! Aborting!")
        logging.info("Check ZabbixServer Settings in variables")
        exit(0)


if __name__ == '__main__':
    main()

