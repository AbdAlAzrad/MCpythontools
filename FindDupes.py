from __future__ import print_function  # make python 2.7 print like 3.4
from nbt140 import NBTFile
import utilities
import multiprocessing
import argparse

try:
    from __builtin__ import xrange as range  # python 2.x, DANGER: the normal 2.7 range function is now not accessible
except ImportError:
    pass  # python 3.4


def create_parser():
    """Returns parser object for handling command line arguments"""
    my_parser = argparse.ArgumentParser(
        description='Application to duplicated items in minecraft. Purpose of this script is to find items with a' +
                    'quantity of less than 1. These are a precursor to most duplication methods. Written by' +
                    'azrad from CraftyMynes, game-server: mc.craftymynes.com', add_help=False)

    required_group = my_parser.add_argument_group(title='required')
    required_group.add_argument('--path', action="store", type=str, dest="path",
                                help='Path to the MCserver root (where the minecraft_server.jar file is located)',
                                required=True)

    optional_group = my_parser.add_argument_group(title='other, optional')
    optional_group.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    optional_group.add_argument('--help', action='help', help='show this help message and exit')
    return my_parser


def check_playerfile(task_queue, report_queue):

    while True:
        player_filename = task_queue.get()  # grab a job (player file name) from the job queue
        if not player_filename:  # we consumed one of the poison pills at the end of the queue
            report_queue.put(None)  # insert poison pill terminator
            return 0  # let this worker die, no more work to do

        player_object = NBTFile(player_filename)
        bad_inv_items = [[item['id'].value, item['Count'].value] for item in player_object['Inventory']
                         if item['Count'].value < 1]
        bad_end_items = [[item['id'].value, item['Count'].value] for item in player_object['EnderItems']
                         if item['Count'].value < 1]

        if bad_inv_items or bad_end_items:
            uuid = player_filename.split('/')[-1].replace('.dat', '')  # extract uuid from filename
            report_queue.put([uuid, bad_inv_items, bad_end_items])


def create_and_start_workers(job_queue, report_queue, number_of_workers):
    """Creates a list of processes, and starts them, returns list of worker processes"""
    # noinspection PyUnusedLocal
    list_of_workers = [multiprocessing.Process(target=check_playerfile, args=(job_queue, report_queue,))
                       for _i in range(number_of_workers)]
    [worker.start() for worker in list_of_workers]
    return list_of_workers


def load_job_queue(job_queue, list_of_workers, list_of_jobs):
    """Puts each player file (string) into the job_queue, then puts in 1 poison pill for each process"""
    [job_queue.put(job) for job in list_of_jobs]
    # noinspection PyUnusedLocal
    [job_queue.put(None) for _dummy in list_of_workers]


def collect_reports(number_of_workers, report_queue):
    """pulls reports off the report queue until it has grabbed 1 poison pill for each worker process
    returns the reports"""
    list_of_bad_players_inventories = []
    poison_pills_found = 0
    while poison_pills_found < number_of_workers:
        report = report_queue.get()
        if not report:
            poison_pills_found += 1
        else:
            list_of_bad_players_inventories.append(report)
    return list_of_bad_players_inventories


def main():
    starting_arguments = create_parser().parse_args()  # get the command line arguments used to start script
    list_of_jobs = utilities.get_player_files(starting_arguments.path)  # list of player files
    number_of_workers = utilities.get_worker_count()  # cal number of workers based on cores

    job_queue = multiprocessing.Queue()  # queue to feed player files to workers
    report_queue = multiprocessing.Queue()  # queue for workers to return bad inventory reports
    list_of_workers = create_and_start_workers(job_queue, report_queue, number_of_workers)  # start worker processes
    load_job_queue(job_queue, list_of_workers, list_of_jobs)

    [print(report) for report in collect_reports(number_of_workers, report_queue)]  # print report of suspicious stuff
    [worker.join() for worker in list_of_workers]  # wait for all workers to end


__author__ = 'azrad'
__version__ = '0.1'
if __name__ == '__main__':
    main()
