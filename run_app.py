"""Runs modules inside the App directory."""
from App.fleet import Fleet, Ship

# Override variables from .env file
host_list = ["192.168.1.167"]

ship = Ship("192.168.1.167")
ship.interactive("raspi0")

# fleet = Fleet(host_list=host_list)

# # Create connections
# fleet.create_bridges_to_devices()

# # Open Interactive session
# fleet.exec_interactive_session_target(position=0)

# # Commands
# # fleet.all_aboard()
# #exec_in_target.exec_target(2)
