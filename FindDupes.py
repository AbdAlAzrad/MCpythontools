from __future__ import print_function
from nbt140 import NBTFile
import utilities
# import platform


def check_playerfile(playerfile):
    player_inventory = NBTFile(playerfile)['Inventory']
    player_echest = NBTFile(playerfile)['EnderItems']
    bad_inv_items = [[item['id'].value, item['Count'].value] for item in player_inventory if item['Count'].value < 2]
    bad_end_items = [[item['id'].value, item['Count'].value] for item in player_echest if item['Count'].value < 2]
    if bad_inv_items or bad_end_items:
        uuid = playerfile.split('/')[-1].replace('.dat', '')  # extract uuid from filename
        return [uuid, bad_inv_items, bad_end_items]







def main(server_path):
    player_list = utilities.get_player_files(server_path)
    number_of_workers = utilities.get_worker_count()
    #print(number_of_workers)
    for player in player_list:
        print(check_playerfile(player))


__author__ = 'azrad'

if __name__ == '__main__':
    main("/home/azrad/mineproject/minecraft1-8")

"""
if int(platform.python_version().split('.')[0]) < 3:
    print('using python 2.x')
else:
    print('using python 3.x')
"""