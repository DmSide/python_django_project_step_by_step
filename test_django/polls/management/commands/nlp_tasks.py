# -*- coding: utf-8 -*-
import logging
import random
import sys
import time

from django import VERSION
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from web_service.settings import BASE_DIR, SERVER_NAME

from background_task.tasks import tasks, autodiscover
from background_task.utils import SignalManager
from compat import close_connection

from nlp.models import ServerStatus
from background_task.models import Task
import os

logger = logging.getLogger(__name__)


def check_server_status_record():
    try:
        ServerStatus.objects.filter(deleted=False, server_name=SERVER_NAME, base_dir=BASE_DIR).latest('start_time')
    # except MultipleObjectsReturned:
    #     for server in list(ServerStatus.objects.filter(
    #             end_time__isnull=True,
    #             deleted=False,
    #             server_name=SERVER_NAME,
    #             base_dir=BASE_DIR
    #     )):
    #         server.end_time = timezone.now()
    #         server.save()
    #     ServerStatus.objects.create(server_name=SERVER_NAME, base_dir=BASE_DIR)
    except ObjectDoesNotExist:
        ServerStatus.objects.create(server_name=SERVER_NAME, base_dir=BASE_DIR)


def _configure_log_std():
    class StdOutWrapper(object):
        def write(self, s):
            logger.info(s)

    class StdErrWrapper(object):
        def write(self, s):
            logger.error(s)
    sys.stdout = StdOutWrapper()
    sys.stderr = StdErrWrapper()


class Command(BaseCommand):
    help = 'Run tasks that are scheduled to run on the queue'

    # Command options are specified in an abstract way to enable Django < 1.8 compatibility
    OPTIONS = (
        (('--duration', ), {
            'action': 'store',
            'dest': 'duration',
            'type': int,
            'default': 0,
            'help': 'Run task for this many seconds (0 or less to run forever) - default is 0',
        }),
        (('--sleep', ), {
            'action': 'store',
            'dest': 'sleep',
            'type': float,
            'default': 5.0,
            'help': 'Sleep for this many seconds before checking for new tasks (if none were found) - default is 5',
        }),
        (('--queue', ), {
            'action': 'store',
            'dest': 'queue',
            'help': 'Only process tasks on this named queue',
        }),
        (('--log-std', ), {
            'action': 'store_true',
            'dest': 'log_std',
            'help': 'Redirect stdout and stderr to the logging system',
        }),

    )

    if VERSION < (1, 8):
        from optparse import make_option
        option_list = BaseCommand.option_list + tuple([make_option(*args, **kwargs) for args, kwargs in OPTIONS])

    # Used in Django >= 1.8
    def add_arguments(self, parser):
        for (args, kwargs) in self.OPTIONS:
            parser.add_argument(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._tasks = tasks

    def handle(self, *args, **options):
        duration = options.pop('duration', 0)
        sleep = options.pop('sleep', 5.0)
        queue = options.pop('queue', None)
        log_std = options.pop('log_std', False)
        sig_manager = SignalManager()

        if log_std:
            _configure_log_std()

        autodiscover()

        start_time = time.time()

        worker_name = str(os.getpid())

        while (duration <= 0) or (time.time() - start_time) <= duration:
            if sig_manager.kill_now:
                # shutting down gracefully
                break

            server = ServerStatus.objects.filter(
                # end_time__isnull=True,
                deleted=False,
                server_name=SERVER_NAME,
                base_dir=BASE_DIR
            ).latest('start_time')
            server_status_on_update = server.on_update
            server_handle_bt_requests = server.handle_bt_requests
            if server_status_on_update:
                logger.debug('server on update. wait.')
                count_of_locked = Task.objects.filter(locked_by=worker_name).count()
                if count_of_locked == 0:
                    if not server.background_ready:
                        server.end_time = timezone.now()
                        server.save()
                        server.background_ready = True
                        server.end_time = None
                        server.id = None
                        server.pk = None
                        server.save()
                    time.sleep(sleep)
            else:
                if server_handle_bt_requests:
                    if not self._tasks.run_next_task(queue):
                        # there were no tasks in the queue, let's recover.
                        close_connection()
                        logger.debug('waiting for tasks')
                        time.sleep(sleep)
                    else:
                        # there were some tasks to process, let's check if there is more work to do after a little break.
                        time.sleep(random.uniform(sig_manager.time_to_wait[0], sig_manager.time_to_wait[1]))
                else:
                    logger.debug('server_handle_bt_requests set FALSE')
