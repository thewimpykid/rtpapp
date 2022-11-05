from . import views 
from django.urls import path


urlpatterns = [
    path('',views.index, name='index'),
    path('past-24-hours/',views.past,),
  
]
