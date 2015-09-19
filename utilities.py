import os.path
from multiprocessing import cpu_count
from glob import glob


def get_worker_count():
    """Set the number of processes to use, minimum of 1 process"""
    output_number_of_workers = cpu_count() - 1
    if output_number_of_workers < 1:
        output_number_of_workers = 1
    return output_number_of_workers


def get_player_files(path_to_server_root):

    return glob(os.path.join(path_to_server_root, 'world', 'playerdata', '*.dat'))

__author__ = 'azrad'
