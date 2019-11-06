_all_ = ['Command']
import logging
from polls.management.commands.nlp_tasks import check_server_status_record
from django.core.management.commands.runserver import Command as RunserverCommand

logger = logging.getLogger(__name__)


class Command(RunserverCommand):
    def __init__(self, *args, **kwargs):
        logger.info('Start run_tasks.__init__')
        check_server_status_record()
        logger.info('End run_tasks.__init__')
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        logger.info('Start run_tasks.handle')
        super(Command, self).handle(*args, **options)
        logger.info('End run_tasks.handle')

    def run(self, *args, **options):
        """Runs the server and the compass watch process"""
        logger.info('Start run_tasks.run')
        super(Command, self).run(*args, **options)
        logger.info('End run_tasks.run')
