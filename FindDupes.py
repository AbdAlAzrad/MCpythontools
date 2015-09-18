from __future__ import print_function  # print() support for python 2.7
from nbt140 import NBTFile
from glob import glob
import os
import utilities

def main(player_folder):
    player_list = glob(os.path.join(player_folder, '*.dat'))
    number_of_workers = utilities.get_worker_count()
    print(number_of_workers)


__author__ = 'azrad'

if __name__ == '__main__':
    main('/home/azrad/mineproject/minecraft1-8/world/playerdata')