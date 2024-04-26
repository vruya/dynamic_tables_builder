from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DynamicTableViewSet, DynamicTableRowViewSet

router = DefaultRouter()
router.register(r'tables', DynamicTableViewSet, basename='dynamic-table')
router.register(r"tables/(?P<table_id>\d+)/rows", DynamicTableRowViewSet, basename='dynamic-table-row')

urlpatterns = [
    path('', include(router.urls)),
]
