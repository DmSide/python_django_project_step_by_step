from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    # path('background_view', views.background_view, name='background_view'),
    url(r'^background_view/?$', views.background_view),
    url(r'^raise_exception_process_task/?$', views.raise_exception_process_task),
    url(r'^raise_exception_pyserver/?$', views.raise_exception_pyserver),
    url(r'^long_task_process_task/?$', views.long_task_process_task),
    url(r'^long_task_pyserver/?$', views.long_task_pyserver),

    url(r'^change_server_status/?$', views.change_server_status),
    url(r'^show_server_status/?$', views.show_server_status),
    url(r'^show_current_server/?$', views.show_current_server),
]