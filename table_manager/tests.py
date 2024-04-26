import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import DynamicTable


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_dynamic_table(db):
    return DynamicTable.objects.create(
        name='Test Table',
        schema={
            'email': {
                'type': 'number'
            },
            'text': {
                'type': 'string',
                'options': {
                    'max_length': 5,
                    'null': True
                }
            }
        }
    )


@pytest.mark.django_db
class TestDynamicTableViewSet:
    def test_get_tables(self, api_client):
        url = reverse('dynamic-table-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_post_table(self, api_client):
        url = reverse('dynamic-table-list')
        data = {
            'name': 'Test Table',
            'schema': {
                'email': {
                    'type': 'number'
                }
            }
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert DynamicTable.objects.count() == 1

    def test_detail_get_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Table'

    def test_detail_patch_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        data = {
            'name': 'New Table',
            'schema': {
                'email': {
                    'type': 'string',
                    'options': {
                        'max_length': 123
                    }
                },
                'pin': {
                    'type': 'number'
                }
            }
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        create_dynamic_table.refresh_from_db()
        assert create_dynamic_table.name == 'New Table'
        assert create_dynamic_table.schema['email']['type'] == 'string'
        assert create_dynamic_table.schema['email']['options']['max_length'] == 123
        assert create_dynamic_table.schema['pin']['type'] == 'number'

    def test_detail_error_patch_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        data = {
            'name': 'New Table',
            'schema': {
                'email': {
                    'type': 'test',
                }
            }
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not a valid choice' in str(response.data['schema']['email']['type'])

    def test_detail_invalid_option_patch_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        data = {
            'schema': {
                'email': {
                    'type': 'string',
                    'options': {
                        'maxlength': 123
                    }
                }
            }
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid option' in str(response.data['schema']['email']['options'])

    def test_detail_invalid_type_option_patch_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        data = {
            'schema': {
                'email': {
                    'type': 'string',
                    'options': {
                        'max_length': '123'
                    }
                }
            }
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid type' in str(response.data['schema']['email']['options'])

    def test_detail_delete_table(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-detail', kwargs={'pk': create_dynamic_table.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert DynamicTable.objects.count() == 0


@pytest.fixture(scope="function")
def create_row(create_dynamic_table):
    client = APIClient()
    url = reverse('dynamic-table-row-list', kwargs={'table_id': create_dynamic_table.pk})
    response = client.post(url, {'email': 1})
    assert response.status_code == 201
    return response.data, create_dynamic_table.pk


@pytest.mark.django_db
class TestDynamicTableRowViewSet:
    def test_get_rows(self, api_client, create_dynamic_table):
        url = reverse('dynamic-table-row-list', kwargs={'table_id': create_dynamic_table.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_post_row(self, api_client, create_row):
        row, table_id = create_row
        assert row['email'] == 1.0

    def test_post_error_row(self, api_client, create_dynamic_table):
        # Email is required
        data = {
            'text': '123'
        }
        url = reverse('dynamic-table-row-list', kwargs={'table_id': create_dynamic_table.pk})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'required' in str(response.data['email'])
        # Email must be number
        data = {
            'email': 'test'
        }
        url = reverse('dynamic-table-row-list', kwargs={'table_id': create_dynamic_table.pk})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'required' in str(response.data['email'])
        # Text has max 5 chars
        data = {
            'email': 123,
            'text': '431249875381812'
        }
        url = reverse('dynamic-table-row-list', kwargs={'table_id': create_dynamic_table.pk})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'no more than 5 characters' in str(response.data['text'])

    def test_detail_get_row(self, api_client, create_row):
        row, table_id = create_row
        url = reverse('dynamic-table-row-detail', kwargs={'table_id': table_id, 'pk': row['id']})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 1.0

    def test_detail_patch_row(self, api_client, create_row):
        row, table_id = create_row
        url = reverse('dynamic-table-row-detail', kwargs={'table_id': table_id, 'pk': row['id']})
        data = {'email': 123}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 123.0

    def test_detail_delete_row(self, api_client, create_row):
        row, table_id = create_row
        url = reverse('dynamic-table-row-detail', kwargs={'table_id': table_id, 'pk': row['id']})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
