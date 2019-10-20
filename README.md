# ZabbixDockerMonitor

Due to the need to track resource consumption statistics by containers within hots, a script for monitoring the information contained in the DockerStats of each container via LLD (Low Level Discovery) was developed.

There're two scripts:

* Zabbix-DockerMonitor-Discover.py (Discover containers in Docker Stats)
* Zabbix-DockerMonitor-Coletor.py (Collect data for containers in Docker Stats)

Templates:

* Template DockerMonitor (Active)

# Requirements
Python3
Py-Zabbix lib

# Configuring

To configure docker container monitoring, follow the steps below:

* Copy scripts to /etc/zabbix/scripts/DockerMonitor
* Change the information contained in the Zabbix-DockerMonitor-Coletor.py script according to the server to be monitored:
    * zabbixserver = "10.10.10.10"
    * hostname = "SERVERAPAP"
    * LogLevel = "INFO"
    * DirLog = "/var/log/DockerMonitor"
* Give Zabbix user permissions on this directory
* Give execute permission (chmod + x) in scripts
* Add user zabbix to the docker group "usermod -a -G docker zabbix"
* Create log directory "mkdir /var/log/DockerMonitor"
* Give recursive permission for zabbix user to write to log folder
* Check if python3 and pip3 are installed
* Install python py-zabbix lib (pip3 install py-zabbix)
* Add UserParameter lines in zabbix_agentd.conf
    * EnableRemoteCommands = 1
    * LogRemoteCommands = 1
* UserParameter = docker.discovery_container, "/etc/zabbix/scripts/DockerMonitor/Zabbix-DockerMonitor-Discover.py"
* UserParameter = docker.get, "/etc/zabbix/scripts/DockerMonitor/Zabbix-DockerMonitor-Coletor.py"
* Validate zabbix_agentd.conf settings (TimeOut, Hostname, ServerActive, etc.)
* Restart zabbix agent
* Add template "Template DockerMonitor (Active)" on Zabbix host
* Track ZabbixAgent log execution

# What is monitored

Everything in docker stats:

* BLOCKIO INPUT of container {#DOCKERINSTANCE}
* BLOCKIO OUTPUT of container {#DOCKERINSTANCE}
* ContainerID of container {#DOCKERINSTANCE}
* ContainerName of container {#DOCKERINSTANCE}
* Total memory of container {#DOCKERINSTANCE}
* Memory used of container {#DOCKERINSTANCE}
* NETIO INPUT of container {#DOCKERINSTANCE}
* NETIO OUTPUT of container {#DOCKERINSTANCE}
* Percentage of memory used by container {#DOCKERINSTANCE}
* PID of container {#DOCKERINSTANCE}
* Total CPU (divided by number of vcpus) used by container {#DOCKERINSTANCE}
* Total CPU (sum all vcpus) used by container {#DOCKERINSTANCE}

# TODO

Separate data submission and byte calculation functions in:

* Zabbix-DockerMonitor-SendData.py
* Zabbix-DockerMonitor-PrepareData.py
