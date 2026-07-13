import pytest

from exclusions.queries import SearchParams, parse_search_params, search_exclusions


def test_parse_search_params_strips():
    params = parse_search_params(
        {
            "firstname": "  John  ",
            "lastname": "  Smith  ",
            "npi": "1234567890",
        }
    )
    assert params.firstname == "John"
    assert params.lastname == "Smith"
    assert params.npi == "1234567890"


def test_parse_search_params_defaults():
    params = parse_search_params({})
    assert params == SearchParams()


def test_parse_search_params_ignores_legacy_filters():
    params = parse_search_params(
        {
            "q": "Smith",
            "name": "Jones",
            "lastname": "Smith",
            "source_state": "MD",
            "list_source": "state",
            "include_reinstated": "1",
            "excldate_from": "20200101",
        }
    )
    assert params == SearchParams(lastname="Smith")


@pytest.mark.django_db
def test_search_exclusions_npi_filter():
    from exclusions.models import ExclusionRecord

    if not ExclusionRecord.objects.exists():
        pytest.skip("exclusion_main table empty or unavailable")

    sample = ExclusionRecord.objects.exclude(npi="").first()
    if sample is None:
        pytest.skip("no records with NPI in exclusion_main")

    results = search_exclusions(SearchParams(npi=sample.npi))
    assert results.filter(id=sample.id).exists()


@pytest.mark.django_db
def test_search_exclusions_name_matches_lastname():
    from exclusions.models import ExclusionRecord

    sample = ExclusionRecord.objects.exclude(lastname="").first()
    if sample is None:
        pytest.skip("no records with lastname in exclusion_main")

    token = sample.lastname[: min(4, len(sample.lastname))]
    results = search_exclusions(SearchParams(lastname=token))
    assert results.filter(id=sample.id).exists()


@pytest.mark.django_db
def test_search_exclusions_name_matches_midname():
    from exclusions.models import ExclusionRecord

    sample = ExclusionRecord.objects.exclude(midname="").first()
    if sample is None:
        pytest.skip("no records with midname in exclusion_main")

    token = sample.midname[: min(4, len(sample.midname))]
    results = search_exclusions(SearchParams(midname=token))
    assert results.filter(id=sample.id).exists()


@pytest.mark.django_db
def test_search_exclusions_name_matches_busname():
    from exclusions.models import ExclusionRecord

    sample = ExclusionRecord.objects.exclude(busname="").first()
    if sample is None:
        pytest.skip("no records with busname in exclusion_main")

    token = sample.busname[: min(6, len(sample.busname))]
    results = search_exclusions(SearchParams(busname=token))
    assert results.filter(id=sample.id).exists()


@pytest.mark.django_db
def test_search_exclusions_and_narrows_results():
    from exclusions.models import ExclusionRecord

    sample = (
        ExclusionRecord.objects.exclude(lastname="")
        .exclude(firstname="")
        .first()
    )
    if sample is None:
        pytest.skip("no records with both first and last name in exclusion_main")

    last_token = sample.lastname[: min(4, len(sample.lastname))]
    first_token = sample.firstname[: min(4, len(sample.firstname))]
    by_last = search_exclusions(SearchParams(lastname=last_token))
    by_both = search_exclusions(
        SearchParams(lastname=last_token, firstname=first_token)
    )
    assert by_both.filter(id=sample.id).exists()
    assert by_both.count() <= by_last.count()


@pytest.mark.django_db
def test_search_includes_reinstated_by_default():
    from exclusions.models import ExclusionRecord

    reinstated = ExclusionRecord.objects.filter(excltype__iexact="reinstated").first()
    if reinstated is None:
        pytest.skip("no Reinstated rows in exclusion_main")

    if reinstated.busname.strip():
        results = search_exclusions(SearchParams(busname=reinstated.busname[:6]))
    elif reinstated.lastname.strip():
        results = search_exclusions(SearchParams(lastname=reinstated.lastname[:4]))
    else:
        pytest.skip("reinstated row has no searchable name fields")

    assert results.filter(id=reinstated.id).exists()
