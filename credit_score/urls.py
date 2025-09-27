from django.urls import path
from . import views

app_name = 'credit_score'
urlpatterns = [

    path('predict/', views.predict_credit_approval, name='credit_application'),
    path('', views.index_view, name='index')
]
