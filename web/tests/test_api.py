import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_exclusion_list(api_client):
    response = api_client.get("/api/v1/exclusions/")
    assert response.status_code == 200
    assert "results" in response.data


@pytest.mark.django_db
def test_sources(api_client):
    response = api_client.get("/api/v1/sources/")
    assert response.status_code == 200
    assert isinstance(response.data, list)


@pytest.mark.django_db
def test_stats(api_client):
    response = api_client.get("/api/v1/stats/")
    assert response.status_code == 200
    assert "total_records" in response.data
    assert "by_source_state" in response.data


@pytest.mark.django_db
def test_exclusion_detail_not_found(api_client):
    response = api_client.get("/api/v1/exclusions/999999999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Medicaid Exclusion List" in response.content


@pytest.mark.django_db
def test_search_page(client):
    response = client.get("/search/")
    assert response.status_code == 200
    content = response.content.decode()
    assert 'name="q"' in content
    assert 'name="npi"' in content
    assert 'name="source_state"' not in content
    assert 'name="list_source"' not in content
    assert 'name="include_reinstated"' not in content


@pytest.mark.django_db
def test_usage_page(client):
    response = client.get("/usage/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_page(client):
    response = client.get("/contact/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_openapi_schema(api_client):
    response = api_client.get("/api/schema/")
    assert response.status_code == 200
