from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from .models import DynamicTable
from .serializers import DynamicTableSerializer, DynamicTableRowSerializer
from .signals import create_dynamic_model


@extend_schema(
    tags=['DynamicTable'],
    description='Create a record to store details about the newly created dynamic model.'
)
class DynamicTableViewSet(viewsets.ModelViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer


@extend_schema(
    tags=['DynamicTableRow'],
    description='Utilize the data structure established from the "tables" previously created.'
)
class DynamicTableRowViewSet(viewsets.ModelViewSet):
    model = None

    def get_queryset(self):
        self.get_dynamic_model()
        return self.model.objects.all()

    def get_serializer_class(self):
        serializer = DynamicTableRowSerializer
        self.get_dynamic_model()
        serializer.Meta.model = self.model
        return serializer

    def get_dynamic_model(self):
        if self.model:
            return

        dynamic_table = get_object_or_404(DynamicTable, pk=self.kwargs['table_id'])
        self.model = create_dynamic_model(dynamic_table)

    def create(self, request, *args, **kwargs):
        return super().create( request, *args, **kwargs)
