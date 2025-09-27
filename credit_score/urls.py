from django.urls import path
from . import views

app_name = 'credit_score'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('predict/', views.predict_credit_approval, name='predict_credit_approval'),

]