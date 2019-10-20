#!/usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################
#                                                           #
#  Zabbix-DockerMonitor-Discover.py                         #
#                                                           #
#  Simple script to discover docker container               #
#  in docker stats                                          #
#                                                           #
#  Version 1.0                                              #
#                                                           #
#  Autor: Aldori Junior                                     #
#  aldorisantosjunior@hotmail.com                           #
#  https://github.com/AldoriJunior/ZabbixDockerMonitor      #
#                                                           #
#############################################################

import json
import subprocess
import ast

data = []

getcontainers = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{\'containername\':\'{{ .Name}}\'}'], stdout=subprocess.PIPE)
x = getcontainers.stdout
x = x.decode('utf-8')
x = x.replace("'b{", "")
x = x.replace("\n", "")
x = x.replace("}{", "},{")
x = "[" + x + "]"
results = ast.literal_eval(x)
for result in results:
    container_name = result[u'containername']
    container_name = container_name.upper()
    data.append({'{#DOCKERINSTANCE}':container_name})

print(json.dumps({"data":data}))
