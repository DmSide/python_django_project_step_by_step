import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_django.settings")
django.setup()

import logging
# from background_task.models import Task
from polls.models import ServerStatus
from django.utils import timezone
from test_django.settings import SERVER_NAME, BASE_DIR

# import subprocess
logger = logging.getLogger(__name__)


def turn_on_tasks_to_server(server_name, server_dir):
    # we have already killed process
    # we must to change status on restart_if_fails of server1 to True

    # Get server from DB
    this_server = ServerStatus.objects.filter(
        deleted=False,
        server_name=server_name,
        base_dir=server_dir,
    ).latest('start_time')
    this_server.end_time = timezone.now()
    this_server.save()
    this_server.restart_if_fails = True
    this_server.handle_bt_requests = True
    this_server.on_update = False
    this_server.background_ready = False
    this_server.end_time = None
    this_server.id = None
    this_server.pk = None
    this_server.save()
    print("Change {} status restart_if_fails = True".format(server_name))
    logger.info("Change {} status restart_if_fails = True".format(server_name))
    print("Change {} status handle_bt_requests = True".format(server_name))
    logger.info("Change {} status handle_bt_requests = True".format(server_name))
    print("Change {} status background_ready = False".format(server_name))
    logger.info("Change {} status background_ready = False".format(server_name))
    print("Change {} status on_update = False".format(server_name))
    logger.info("Change {} status on_update = False".format(server_name))


if __name__ == '__main__':
    turn_on_tasks_to_server(SERVER_NAME, BASE_DIR)
    # Change nginx settings
