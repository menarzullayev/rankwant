"""`translate()` has no fallback locale; a gap is the property name."""

from core.i18n import translate

CATALOG = {
    "user.name": {"en": "Name", "uz": "Ism", "ru": "Имя"},
    "user.bio": {"en": "Bio", "uz": "Tarjimai hol"},
}


def test_one_property() -> None:
    assert translate("en", "user.name", catalog=CATALOG) == "Name"
    assert translate("uz", "user.name", catalog=CATALOG) == "Ism"


def test_many_properties() -> None:
    texts = translate("en", "user.name", "user.bio", catalog=CATALOG)
    assert texts == ("Name", "Bio")


def test_missing_locale_is_the_property() -> None:
    assert translate("zh", "user.name", catalog=CATALOG) == "user.name"


def test_missing_property_is_the_property() -> None:
    assert translate("en", "user.unknown", catalog=CATALOG) == "user.unknown"


def test_empty_string_is_the_property() -> None:
    catalog = {"user.name": {"en": "   "}}
    assert translate("en", "user.name", catalog=catalog) == "user.name"


def test_does_not_copy_uzbek_when_ru_is_missing() -> None:
    assert translate("ru", "user.bio", catalog=CATALOG) == "user.bio"
