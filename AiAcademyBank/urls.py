from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('credit_score/', include('credit_score.urls')),
    path('employees_rag/', include('employees_rag.urls')),
path('', lambda request: redirect('credit_score:predict'))
]

