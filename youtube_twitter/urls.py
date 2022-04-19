
from django.urls import path
from .views import index, logout, twitter
app_name = 'youtube_twitter'
urlpatterns = [

    path('', twitter, name='home' ),
    path('youtube/',index , name='index' ),
    path('logout/', logout, name='logout')
]
