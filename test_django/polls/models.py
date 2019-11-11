from django.db import models

# Create your models here.


class ServerStatusManager(models.Manager):
    pass


class RunserverTasksManager(models.Manager):
    pass


class RunserverTasks(models.Model):
    pid = models.BigIntegerField()
    name = models.CharField(max_length=100, default='')
    host = models.CharField(max_length=100, default='')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    objects = RunserverTasksManager()


class ServerStatus(models.Model):
    """
    server_name         :: name of server from config
    base_dir            :: absolute path to directory of project
    status :: status of server(DON'T WORK NOW).
        Available values: ['shutdown', 'starting', 'ready']
        - 'shutdown' means no screen of this SERVER_NAME are started
        - 'starting' means the screen of this SERVER_NAME try to started(check_server.py make this)
        - 'ready' means the screen of this SERVER_NAME has finished to load
    on_update           :: signal of server marked to update.
        Available values: [True, False]
        - True means that server marked to update AND background_task of this SERVER_NAME don't get new tasks
        - False means that server runs as usual
    handle_bt_requests  :: signal of nlp_tasks to do tasks.
        Available values: [True, False]
        - True means that background_task of this SERVER_NAME get new tasks
        - False means that background_task of this SERVER_NAME don't get new tasks
    background_ready    :: signal of background_task of this SERVER_NAME has no running tasks and this screen ready to update
        Available values: [True, False]
    restart_if_fails    :: signal of that server will be restarted if it fail
        Available values: [True, False]
    start_time          :: time when current state of server with this SERVER_NAME started
    end_time            :: time when current state of server with this SERVER_NAME finished
    deleted             :: signal of record has deleted(not used now)
        Available values: [True, False]
    """
    server_name = models.CharField(max_length=20, default='')
    base_dir = models.CharField(max_length=100, default='')
    status = models.CharField(max_length=20, default='ready')
    on_update = models.BooleanField(default=False)
    handle_bt_requests = models.BooleanField(default=False)
    background_ready = models.BooleanField(default=False)
    restart_if_fails = models.BooleanField(default=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)
    objects = ServerStatusManager()
