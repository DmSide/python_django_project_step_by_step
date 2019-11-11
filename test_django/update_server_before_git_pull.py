import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_django.settings")
django.setup()

import logging
# from background_task.models import Task
from polls.models import RunserverTasks, ServerStatus
from django.utils import timezone
from test_django.settings import SERVER_NAME, BASE_DIR

logger = logging.getLogger(__name__)


def turn_off_tasks_to_server(server_name, server_dir):
    logger.info('turn_off_tasks_to_server start')
    this_server = ServerStatus.objects.filter(
        deleted=False,
        server_name=server_name,
        base_dir=server_dir,
        # end_time__isnull=True
    ).latest('start_time')
    this_server.end_time = timezone.now()
    this_server.save()
    this_server.on_update = True
    this_server.handle_bt_requests = False
    this_server.restart_if_fails = False
    this_server.end_time = None
    this_server.id = None
    this_server.pk = None
    this_server.save()
    print("Change {} status restart_if_fails = False".format(server_name))
    logger.info("Change {} status restart_if_fails = False".format(server_name))
    print("Change {} status on_update = True".format(server_name))
    logger.info("Change {} status on_update = True".format(server_name))
    print("Change {} status handle_bt_requests = False".format(server_name))
    logger.info("Change {} status handle_bt_requests = False".format(server_name))

    logger.info('turn_off_tasks_to_server end')


def wait_when_tasks_is_over(server_name, server_dir):
    print("Waiting for tasks is over...")
    logger.info("Waiting for tasks is over...")
    ready_to_restart = False
    while not ready_to_restart:
        rt_len = RunserverTasks.objects.filter(host=server_name, end_time__isnull=True).count()
        cur_server = ServerStatus.objects.filter(
            deleted=False,
            server_name=server_name,
            base_dir=server_dir,
            # end_time__isnull=True
        ).latest('start_time')

        background_ready = cur_server.background_ready if cur_server else False
        ready_to_restart = rt_len == 0 and background_ready
    print("Server {} is ready to update".format(server_name))
    logger.info("Server {} is ready to update".format(server_name))


if __name__ == '__main__':
    # Change nginx settings
    turn_off_tasks_to_server(SERVER_NAME, BASE_DIR)
    wait_when_tasks_is_over(SERVER_NAME, BASE_DIR)
