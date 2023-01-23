from . import views 
from django.urls import path


urlpatterns = [
    path('',views.index, name='index'),
    path('past-12-hours/',views.past,),
    path('next-12-hours/',views.next,),
  
]
