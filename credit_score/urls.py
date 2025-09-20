from django.urls import path
from . import views

app_name = 'credit_score' # ОЧЕНЬ ВАЖНО для redirect
urlpatterns = [
    path('predict/', views.predict_credit_approval, name='predict'),
]