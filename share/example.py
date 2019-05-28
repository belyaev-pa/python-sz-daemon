# -*- coding: utf-8 -*-
from lib.base_daemon import BaseDaemon
from lib.daemon_configurator import DaemonConfigurator


class ExampleDaemon(BaseDaemon):

    def run(self):
        while True:
            print('Hello world!')



def create_daemon(command):
    """
    Функция создания и управлению демоном
    :param command: строка содержащая команду start, stop, restart
    :param conf_dict: словарь с настройками
    :return: void
    """
    PID_FILE_PATH = '/path/to/pid_file.pid'
    LOG_NAME = 'example_log_name'
    daemon = ExampleDaemon(PID_FILE_PATH, LOG_NAME)
    config = DaemonConfigurator(daemon)
    react_dict = config.get_reacts_for_daemon()
    try:
        react_dict[command]()
    except KeyError:
        raise KeyError("Can`t find {0} in provided command".format(command))


if __name__ == '__main__':
    create_daemon('stop')
