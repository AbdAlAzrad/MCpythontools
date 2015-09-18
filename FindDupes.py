from __future__ import print_function  # print() support for python 2.7
from nbt140 import NBTFile
import utilities

def main(server_path):
    player_list = utilities.get_player_files(server_path)
    number_of_workers = utilities.get_worker_count()
    print(number_of_workers)
    print(player_list)


__author__ = 'azrad'

if __name__ == '__main__':
    main("/home/azrad/mineproject/minecraft1-8")
