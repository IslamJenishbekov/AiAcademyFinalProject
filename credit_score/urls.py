# credit_score/urls.py
from django.urls import path
from . import views

app_name = 'credit_score'
urlpatterns = [
    # Измените views.credit_application_view на views.predict_credit_approval
    path('predict/', views.predict_credit_approval, name='credit_application'),
    path('', views.index_view, name='index')
]
