from django.urls import path

from frontends.django_web import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/calculate/", views.calculate, name="calculate"),
    path("api/advanced/", views.advanced_math, name="advanced_math"),
    path("api/programmer/", views.programmer, name="programmer"),
    path("api/currency/", views.currency, name="currency"),
    path("api/unit/catalog/", views.unit_catalog, name="unit_catalog"),
    path("api/unit/convert/", views.unit_convert, name="unit_convert"),
    path("api/date/", views.date_calculate, name="date_calculate"),
    path("api/settings/", views.settings_view, name="settings"),
    path("api/history/", views.history, name="history"),
]
