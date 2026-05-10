from django.urls import path

from frontends.django_web import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/calculate/", views.calculate, name="calculate"),
    path("api/advanced/", views.advanced_math, name="advanced_math"),
    path("api/programmer/", views.programmer, name="programmer"),
    path("api/currency/", views.currency, name="currency"),
]
