A collection of tools for Minecraft server management written in/for python.

Notes: These tools depends heavily on https://github.com/twoolie/NBT. The necessary parts are included here in a file called nbt140.py.

**FindDupes.py** - Searches every player file on the server for inventory and enderchest items with a count of less than 1 (this is a bug commonly used to duplicate items). Estimated run time on modest machine: (1 minute per 10,000 players)/(number of cores). Since this tool is 'readonly' it can be safely run while minecraft server is running. 

**MovePlayers.py** - Searches every player file for players who are logged out in the End. It then moves them to a specified Overworld location. Runs in about the same time as FindDupes.py. Should not be run while the MC server is running. Purpose: migration to Minecraft 1.9.

