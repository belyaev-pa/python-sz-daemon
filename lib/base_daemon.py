# -*- coding: utf-8 -*-
import sys
import os
import time
import atexit
import signal
import syslog
import datetime
import abc
import traceback


class BaseDaemon(object):

    def __init__(self, pidfile, log_name,
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        """
        конструктор демона
        :param pidfile: путь к pid файлу, обязательный агрумент
        :param stdin: путь к файлу для хранения stdin, по умолчанию никуда не сохраняет
        :param stdout: путь к файлу для хранения stdout, по умолчанию никуда не сохраняет
        :param stderr: путь к файлу для хранения stderr, по умолчанию никуда не сохраняет
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.log_name = log_name
        syslog.openlog(self.log_name)
        syslog.syslog(syslog.LOG_ERR, '*' * 100)
        syslog.syslog(syslog.LOG_INFO, 'Инициализация демонизации процесса {}'.format(log_name))

    def daemonize(self):
        """
        производит UNIX double-form магию,
        Stevens "Advanced Programming in the UNIX Environment"
        for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            msg = "(UNIX)fork #1 был неудачным: %d (%s)\n" % (e.errno, e.strerror)
            syslog.syslog(syslog.LOG_ERR, msg)
            sys.exit(msg)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            msg = "(UNIX)fork #2 был неудачным: %d (%s)\n" % (e.errno, e.strerror)
            syslog.syslog(syslog.LOG_ERR, msg)
            sys.exit(msg)

            # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        syslog.syslog(syslog.LOG_INFO, 'Pid файл {} записан'.format(self.pidfile))
        atexit.register(self.delpid)
        pid = str(os.getpid())
        syslog.syslog(syslog.LOG_INFO, 'Pid процесса: {}'.format(pid))
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        syslog.syslog(syslog.LOG_INFO, 'Демон остановлен. Pid файл удален...'.format(datetime.datetime.now()))
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'pid файл {} уже существует. Возможно процесс демона уже запущен?'.format(self.pidfile)
            syslog.syslog(syslog.LOG_INFO, message)
            sys.stderr.write(message)
            sys.exit(1)

        # Start the daemon
        syslog.syslog(syslog.LOG_INFO, 'Запускаем процесс демонизации.')
        self.daemonize()
        try:
            self.run()
        except BaseException as err:
            syslog.syslog(syslog.LOG_ERR, 'Произошла ошибка при вызове функции run демона. Traceback:')
            syslog.syslog(syslog.LOG_ERR, '-' * 100)
            ex_type, ex, tb = sys.exc_info()
            for obj in traceback.extract_tb(tb):
                syslog.syslog(syslog.LOG_ERR, 'Файл: {}, строка: {}, вызов: {}'.format(obj[0], obj[1], obj[2]))
                syslog.syslog(syslog.LOG_ERR, '----->>>  {}'.format(obj[3]))
            syslog.syslog(syslog.LOG_ERR, 'Ошибка: {}.'.format(err))
            syslog.syslog(syslog.LOG_ERR, '-' * 100)

    sigDict = {}

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "Pid файл {} не найден. Возможно демон не запущен ?".format(self.pidfile)
            syslog.syslog(syslog.LOG_ERR, message)
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        syslog.syslog(syslog.LOG_INFO, 'Перезапускаем процесс демонизации')
        self.stop()
        self.start()

    @abc.abstractmethod
    def run(self):
        """
        You have to implement this method in inheritor to daemon do some work
        :return:
        """
