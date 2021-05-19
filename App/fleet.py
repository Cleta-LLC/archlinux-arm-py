import sys
import os
from dotenv import load_dotenv
from App.fab_bridge import Bridge
from App.devices import ArchLinuxArmDevice

from Logger.logging_config import get_simple_logger
CLASS_LOG = get_simple_logger("main")

load_dotenv()
host_list = os.getenv("HOST_LIST")
host_list = host_list.split(",")
port = os.getenv("PORT")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
root_password = os.getenv("ROOT_PASSWORD")
new_username = os.getenv("NEW_USERNAME")
new_password = os.getenv("NEW_PASSWORD")
swarm_token = os.getenv("SWARM_TOKEN")
swarm_leader = os.getenv("SWARM_LEADER")

class Ship():
    def __init__(
        self,
        host,
        port=port,
        username=username,
        password=password,
        root_password=root_password,
        new_username=new_username,
        new_password=new_password,
        swarm_token=swarm_token,
        swarm_leader=swarm_leader
        ):

        self.host = host
        self.username=username
        self.password=password
        self.port=port
        self.root_password=root_password
        self.new_username=new_username
        self.new_password=new_password
        self.swarm_token=swarm_token
        self.swarm_leader=swarm_leader
    
    def interactive(self, new_hostname):
        bridge = Bridge(self.host, self.port, self.username, self.password)
        current_device = ArchLinuxArmDevice(bridge, self.root_password)

        message = "Creating bridge with user {} at {}".format(self.username, new_hostname)
        print(message)
        CLASS_LOG.info(message)

        current_device.device.get_shell()
        return


class Fleet():

    def __init__(
        self,
        host_list=host_list,
        port=port,
        username=username,
        password=password,
        root_password=root_password,
        new_username=new_username,
        new_password=new_password,
        swarm_token=swarm_token,
        swarm_leader=swarm_leader
        ):

        self.devices = []
        self.size = 0
        self.host_list=host_list
        self.username=username
        self.password=password
        self.port=port
        self.root_password=root_password
        self.new_username=new_username
        self.new_password=new_password
        self.swarm_token=swarm_token
        self.swarm_leader=swarm_leader
    
    def _check_host_list(self):
        if not isinstance(host_list, list):
            message = "Only list of hosts"
            print(message)
            CLASS_LOG.critical(message)
            sys.exit()

    def create_bridges_to_devices(self):
        self._check_host_list()
        current_device_number = 0

        for i in range(self.size):
            current_device_number += 1  # Start in 1 so hosts are like hostname-1, hostname-2
            current_hostname = "rpi64-{}".format(current_device_number)

            bridge = Bridge(self.host_list[i], self.port, self.username, self.password)
            current_device = ArchLinuxArmDevice(bridge, self.root_password)
            self.devices.add((current_hostname, current_device))
            self.size =+ 1

            message = "Creating bridge with user {} at {}".format(self.username, self.host_list[i])
            print(message)
            CLASS_LOG.info(message)
        return self.devices
    
    def exec_interactive_session_target(self, position):
        if self.size > position >= 0:
            self.devices.get(position).device.get_shell()
            return
        CLASS_LOG.error("Invalid position")

    def exec_in_target(self, position, command):
        size = len(self.devices)
        if size > position >= 0:
            self.devices.get(position).send_command(command)
            message = ("Executed command in target position: {}".format(position))
            print(message)
            CLASS_LOG.info(message)

    def all_aboard(self):
        size = len(self.devices)
        message = "Executing in the following hosts: {}".format(self.host_list)
        print(message)
        CLASS_LOG.info(message)
        for host, device in self.devices.items():
            device.new_system_setup(self.new_username, self.new_password, host)
            message = "Finish setting up new device"
            print(message)
            CLASS_LOG.info(message)


            device.docker_setup()
            message = "Finish Docker set up"
            print(message)
            CLASS_LOG.info(message)

            message = "Joining docker swarm user {} at {}".format(self.new_username, self.swarm_leader)
            print(message)
            CLASS_LOG.info(message)
            device.docker_swarm_join(self.swarm_token, self.swarm_leader)


def all_aboard():
    print(host_list)

    message = "Executing in the following hosts: {}".format(host_list)
    print(message)
    CLASS_LOG.info(message)
    
    if not isinstance(host_list, list):
        message = "Only list of hosts"
        print(message)
        CLASS_LOG.critical(message)
        sys.exit()

    for i in range(len(host_list)):
        bridge = Bridge(host_list[i], port, username, password)
        dev = ArchLinuxArmDevice(bridge, root_password)
        message = "Creating bridge with user {} at {}".format(username, host_list[i])
        print(message)
        CLASS_LOG.info(message)

        hostname = "rpi64-{}".format(i)
        message = "Setting up new device "
        print(message)
        CLASS_LOG.info(message)
        dev.new_system_setup(new_username, new_password, hostname)

    for i in range(len(host_list)):
        bridge = Bridge(host_list[i], port, new_username, new_password)
        dev = ArchLinuxArmDevice(bridge, root_password)
        message = "Creating bridge with user {} at {}".format(new_username, host_list[i])
        print(message)
        CLASS_LOG.info(message)

        dev.docker_setup()
        message = "Docker set up."
        print(message)
        CLASS_LOG.info(message)

        message = "Joining docker swarm user {} at {}".format(new_username, swarm_leader)
        print(message)
        CLASS_LOG.info(message)
        dev.docker_swarm_join(swarm_token, swarm_leader)