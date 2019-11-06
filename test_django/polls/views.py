from django.shortcuts import render
from django.http import HttpResponse
from background_task import background
# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@background(schedule=5)
def hello():
    print("Hello World frm BT!")


def background_view(request):
    hello()
    return HttpResponse("Hello world! Our BT scripts works in async")