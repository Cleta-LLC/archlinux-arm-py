"""Common operations to be performed on arch devices."""
from Logger.logging_config import get_simple_logger
CLASS_LOG = get_simple_logger("main")

class ArchLinuxArmDevice():
    """This class includes rpi4 64-bits 8GB RAM version."""

    def __init__(self, target, root_password=None):
        self.bridge = target
        self.device = self.bridge.device
        if root_password:
            self.device.add_root_password(root_password)

    # Set up a device to work with pacman
    def _low_level_setup(self):
        self.device._set_pacman()
        self.device._update_pacman()
        self.device._set_sudo()

    # Send command
    def send_command(self, cmd, sudo=False, respond=False):
        """Sends command using Bridge."""
        return self.bridge.execute(cmd, sudo, respond) 

    # Operations
    def op_install_sudo(self):
        self.device._set_sudo()

    def op_set_new_user(self, new_username, new_password):
        self.device._set_new_user(new_username, new_password)

    def op_set_locale(self):
        command_list = [
            "ln -s /usr/share/zoneinfo/America/New_York /etc/localtime", 
            'echo "en_US.UTF-8 UTF-8" > /etc/locale.gen', 
            "locale-gen"]
        self.send_command(command_list, sudo=True)
    
    def op_set_hostname(self, hostname=None):
        if not hostname:
            hostname = self.device.username
        command_list = [ 
            "echo {} > /etc/hostname".format(hostname), 
            "echo 127.0.0.1 localhost {} >> /etc/hosts".format(hostname)
        ]
        self.send_command(command_list, sudo=True)

    def op_set_time(self):
        command_list = [
            'echo "LANG=en_US.UTF-8" >> /etc/locale.conf', 
            'echo "LC_COLLATE=C" >> /etc/locale.conf',
            'echo "LC_TIME=en_US.UTF-8" >> /etc/locale.conf'
        ]
        self.send_command(command_list, sudo=True)
    
    def op_set_datetime(self):
        self.pacman_install("wget")
        return self.send_command(
            "date -s \"$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z\"",
            sudo=True)


    def pacman_install(self, package, needed=True, noconfirm=True):
        cmd = "pacman -S "
        flags = ""
        if needed:
            flags += " --needed"
        if noconfirm:
            flags += " --noconfirm"

        if isinstance(package, list):
            for p in package:
                self.send_command(cmd + p + flags, sudo=True)
        else:
            self.send_command(cmd + package + flags, sudo=True)
    
    def is_package_installed(self, package):
        cmd = "pacman -Qs {}".format(package)
        self.send_command(cmd, sudo=True)
        
    def new_system_setup(self, new_username, new_password, new_hostname):
        CLASS_LOG.info("Setting up new device")
        self._low_level_setup()
        self.op_set_locale()
        self.op_set_hostname(new_hostname)
        self.op_set_time()
        self.op_set_datetime()
        self.op_set_new_user(new_username, new_password)
        CLASS_LOG.info("Device setup complete.")
    
    def docker_setup(self):
        """Install and runs docker service."""
        self.send_command("usermod -aG docker {}".format(self.device.username), sudo=True)
        self.send_command("pacman -Syu --needed --noconfirm", sudo=True)
        self.pacman_install(["docker", "docker-machine"])
        self.send_command("systemctl start docker.service", sudo=True)

    def docker_swarm_join(self, token, leader):
        """Sets the device to join a docker swarm using a token."""
        self.send_command("docker swarm leave -f")
        self.send_command("docker swarm join --token {} {}".format(token, leader), sudo=True)

    def install_yay(self):
        # Install yay needs git
        self.send_command("git -c http.sslVerify=false clone https://aur.archlinux.org/yay.git")
        self.send_command("cd yay && makepkg -si --noconfirm", respond=True)
        self.send_command("yay --version")
