from django.urls import path
from . import views

urlpatterns = [
	path('start_stream/', views.start_stream, name='start_stream'),
	path('', views.main, name='main'),
	path('get-json-data/', views.get_json_data, name='get_json_data'),
]