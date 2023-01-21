from django.urls import path
from . import views

urlpatterns = [
    path('organizations', views.organizations),
    path('organizations/<slug:slug>', views.organizations),
    
    path('users', views.users),
    path('users/<slug:slug>', views.users),
    
    path('login', views.login),
    path('register', views.register),
    
    path('campaigns', views.campaigns),
    path('campaigns/<slug:slug>', views.campaigns),
    path('campaigns/<slug:campaign_id>/journeys', views.journeys),
    
    path('contacts', views.contacts),
    path('contacts/<slug:slug>', views.contacts),
    
    path('journeys', views.journeys),
    path('journeys/<slug:slug>', views.journeys),
    
    path('batches', views.batches),
]