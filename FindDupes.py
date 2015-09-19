from __future__ import print_function  # make python 2.7 print like 3.4
from nbt140 import NBTFile
import utilities
import multiprocessing

try:
    from __builtin__ import xrange as range  # python 2.x, DANGER: the normal 2.7 range function is now not accessible
except ImportError:
    pass  # python 3.4


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
    """Creates a list of processes, and starts them"""
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


def main(server_path):
    list_of_jobs = utilities.get_player_files(server_path)  # list of player files
    number_of_workers = utilities.get_worker_count()  # cal number of workers based on cores

    job_queue = multiprocessing.Queue()  # queue to feed player files to workers
    report_queue = multiprocessing.Queue()  # queue for workers to return bad inventory reports
    list_of_workers = create_and_start_workers(job_queue, report_queue, number_of_workers)  # start worker processes
    load_job_queue(job_queue, list_of_workers, list_of_jobs)

    list_of_bad_players_inventories = []
    poison_pills = 0
    while poison_pills < number_of_workers:
        report = report_queue.get()
        if not report:
            poison_pills += 1
        else:
            list_of_bad_players_inventories.append(report)

    [print(report) for report in list_of_bad_players_inventories]
    [worker.join() for worker in list_of_workers]  # wait for all workers to end
__author__ = 'azrad'

if __name__ == '__main__':
    main("/home/azrad/mineproject/minecraft1-8")


"""
if int(platform.python_version().split('.')[0]) < 3:
    print('using python 2.x')
else:
    print('using python 3.x')
"""