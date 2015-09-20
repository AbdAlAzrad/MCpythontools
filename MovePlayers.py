from __future__ import print_function
import multiprocessing
import argparse
from nbt140 import NBTFile, MalformedFileError  # for newer version try: https://github.com/twoolie/NBT
import utilities

try:
    from __builtin__ import xrange as range  # python 2.7
except ImportError:
    pass  # not required for python 3


def create_parser():
    """Returns parser object for handling command line arguments"""
    my_parser = argparse.ArgumentParser(
        description='Application to check and/or move all players in minecraft out of the End. Purpose of this' +
                    'script is to prepare a server for migration to 1.9. Written by' +
                    'azrad from CraftyMynes, game-server: mc.craftymynes.com', add_help=False)

    required_group = my_parser.add_argument_group(title='required')
    required_group.add_argument('--path', action="store", type=str, dest="path",
                                help='Path to the MCserver root (where the minecraft_server.jar file is located)',
                                required=True)
    required_group.add_argument('--destination', nargs='+', action="store", type=int, dest="destination",
                                help='Coordinates to move players in the End too', required=True)

    optional_group = my_parser.add_argument_group(title='other, optional')
    optional_group.add_argument('--countonly', action="store_true", dest="countonly", default=False,
                                help='do NOT actually move/modify the players/files')
    optional_group.add_argument('--printnames', action="store_true", dest="printnames", default=False,
                                help='print list of players found/moved, might be long!')
    optional_group.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    optional_group.add_argument('--help', action='help', help='show this help message and exit')
    return my_parser


def move_player(starting_arguments, task_queue, report_queue):
    """The multiprocess worker, grabs a filename string from the queue, looks to see if it is in the end, and moves
    the player out of the end"""
    while True:
        player_filename = task_queue.get()  # grab a job (player file name) from the job queue
        if not player_filename:  # we consumed one of the poison pills at the end of the queue
            report_queue.put(None)  # insert poison pill terminator
            return 0  # let this worker die, no more work to do

        # parse the player file, and see if player is in the end
        try:
            player_object = NBTFile(player_filename, 'rb')
        except MalformedFileError:
            print('WARNING: player file', player_filename, 'does not seem to be a valid player file, skipping')
            continue
        try:
            if player_object['Dimension'].value != 1:  # 1 = the End, 0 = Overworld, -1 = Nether
                continue
        except KeyError:
            print('WARNING: player file', player_filename, 'does not seem to have a location!, skipping')
            continue

        # if --countonly argument was given
        if starting_arguments.countonly:
            report_queue.put(player_filename.split('/')[-1].replace('.dat', ''))
            continue

        # player is in the end, now move them out of the end
        player_object['Dimension'].value = 0  # 1 = the End, 0 = Overworld, -1 = Nether
        player_object['Pos'][0].value = starting_arguments.destination[0]  # x coordinate
        player_object['Pos'][1].value = starting_arguments.destination[1]  # y coordinate
        player_object['Pos'][2].value = starting_arguments.destination[2]  # z coordinate

        # repack and write the modified player file back to the drive
        try:
            player_object.write_file(player_filename)
            report_queue.put(player_filename.split('/')[-1].replace('.dat', ''))
        except Exception as e:
            print('WARNING: Following problem caused player file', player_filename, 'to not be written',
                  'to the drive')
            print(e, 'skipping file')


def sanity_check_coordinates(starting_arguments):
    """Sanity check on coordinates argument"""
    if len(starting_arguments.destination) != 3:
        raise IndexError("--destination requires exactly 3 integers")
    elif starting_arguments.destination[1] < 0 or starting_arguments.destination[1] > 255:
        raise IndexError("--destination y value must be greater than 0 and less than 256")
    elif abs(starting_arguments.destination[0]) > 30000000:
        raise IndexError("--destination x value must be in range +/- 30000000")
    elif abs(starting_arguments.destination[2]) > 30000000:
        raise IndexError("--destination z value must be in range +/- 30000000")


def calculate_number_of_workers():
    """Set the number of processes to use, minimum of 1 process"""
    output_number_of_workers = multiprocessing.cpu_count() - 1
    if output_number_of_workers < 1:
        output_number_of_workers = 1
    return output_number_of_workers


def create_and_start_workers(starting_arguments, input_job_queue, input_output_queue, input_num_of_workers):
    """Creates a list of processes, and starts them"""
    # noinspection PyUnusedLocal
    output_list_of_workers = [multiprocessing.Process(target=move_player,
                                                      args=(starting_arguments, input_job_queue,
                                                            input_output_queue,)) for _i in range(input_num_of_workers)]
    [worker.start() for worker in output_list_of_workers]
    return output_list_of_workers


def load_job_queue(input_job_queue, input_list_of_workers, input_jobs_list):
    """Puts each player file (string) into the job_queue, then puts in 1 poison pill for each process"""
    [input_job_queue.put(job) for job in input_jobs_list]
    # noinspection PyUnusedLocal
    [input_job_queue.put(None) for _dummy in input_list_of_workers]


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
    """The main loop to set up everything"""
    starting_arguments = create_parser().parse_args()  # get the command line arguments used to start script
    sanity_check_coordinates(starting_arguments)  # make sure --destination isn't crazy
    player_file_list = utilities.get_player_files(starting_arguments.path)  # list of player files
    job_queue = multiprocessing.Queue()  # queue to feed player files to workers
    report_queue = multiprocessing.Queue()  # queue for workers to return names of moved players
    number_of_workers = calculate_number_of_workers()  # calculate # of workers from cores
    list_of_workers = create_and_start_workers(starting_arguments, job_queue, report_queue, number_of_workers)
    load_job_queue(job_queue, list_of_workers, player_file_list)  # put player files in the queue
    [worker.join() for worker in list_of_workers]  # wait for all workers to end

    # process output

    list_of_moved_players = [report for report in collect_reports(number_of_workers, report_queue)]
    [worker.join() for worker in list_of_workers]  # wait for all workers to end

    if starting_arguments.printnames:
        [print(player_file) for player_file in list_of_moved_players]

    # print totals
    if starting_arguments.countonly:
        print('Found', len(list_of_moved_players), 'players in the End, did not move them.')
    else:
        print('Moved', len(list_of_moved_players), 'players out of the End.')


__author__ = 'azrad'
__version__ = '0.1'

if __name__ == '__main__':
    main()
