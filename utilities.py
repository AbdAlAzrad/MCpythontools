__author__ = 'azrad'


def get_worker_count():
    from multiprocessing import cpu_count
    """Set the number of processes to use, minimum of 1 process"""
    output_number_of_workers = cpu_count() - 1
    if output_number_of_workers < 1:
        output_number_of_workers = 1
    return output_number_of_workers
