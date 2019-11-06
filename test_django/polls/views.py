from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from lib.json_encoder import JSONEncoderHttp
from background_task import background
from test_django.settings import BASE_DIR, SERVER_NAME
from polls.models import ServerStatus
from django.utils import timezone
# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@background(schedule=5)
def hello():
    print("Hello World frm BT!")


def background_view(request):
    hello()
    return HttpResponse("Hello world! Our BT scripts works in async")


@background(schedule=5)
def raise_exception():
    raise Exception("MyException")


@background(schedule=5)
def long_task(delay):
    import time
    time.sleep(delay)


def raise_exception_process_task(request):
    raise_exception()
    return JsonResponse({}, encoder=JSONEncoderHttp)


def raise_exception_pyserver(request):
    raise Exception("MyException")


def long_task_process_task(request):
    data = request.data
    delay = 10 if 'delay' not in data else data['delay']
    long_task(delay)
    return JsonResponse({}, encoder=JSONEncoderHttp)


def long_task_pyserver(request):
    data = request.data
    delay = 10 if 'delay' not in data else data['delay']
    import time
    time.sleep(delay)
    return JsonResponse({}, encoder=JSONEncoderHttp)


def change_server_status(request):
    data = request.data
    if 'server_name' not in data:
        raise Exception('Required server_name field has skipped')
    server_name = data['server_name']

    if 'base_dir' not in data:
        base_dir = BASE_DIR
    else:
        base_dir = data['base_dir']

    if 'on_update' not in data:
        raise Exception('Required on_update field has skipped')
    on_update = data['on_update']

    if 'restart_if_fails' not in data:
        raise Exception('Required restart_if_fails field has skipped')
    restart_if_fails = data['restart_if_fails']

    if 'background_ready' not in data:
        raise Exception('Required background_ready field has skipped')
    background_ready = data['background_ready']

    if 'handle_bt_requests' not in data:
        raise Exception('Required handle_bt_requests field has skipped')
    handle_bt_requests = data['handle_bt_requests']

    server = ServerStatus.objects.filter(deleted=False, server_name=server_name, base_dir=base_dir).latest('start_time')
    server.end_time = timezone.now()
    server.save()
    server.on_update = on_update
    server.restart_if_fails = restart_if_fails
    server.background_ready = background_ready
    server.handle_bt_requests = handle_bt_requests
    server.end_time = None
    server.id = None
    server.pk = None
    server.save()

    return JsonResponse({}, encoder=JSONEncoderHttp)


def show_server_status(request):
    servers = ServerStatus.objects.filter(end_time__isnull=True, deleted=False)
    servers_dict = {}
    for server in servers:
        ss = dict()
        ss['status'] = server.status
        ss['on_update'] = server.on_update
        ss['handle_bt_requests'] = server.handle_bt_requests
        ss['background_ready'] = server.background_ready
        ss['restart_if_fails'] = server.restart_if_fails

        servers_dict[server.server_name + ' on ' + server.base_dir] = ss

    return JsonResponse(servers_dict, encoder=JSONEncoderHttp)


def show_current_server(request):
    return JsonResponse({'server': SERVER_NAME}, encoder=JSONEncoderHttp)
