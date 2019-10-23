from django.urls import path

from dictionary import views

urlpatterns = [
    path('<str:word>', views.lookup, name='lookup'),
]
