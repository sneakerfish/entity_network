import unittest
from process_story import find_entities, geo_replace_abbreviation

class FindEntitiesTest(unittest.TestCase):
    def test_no_entities(self):
        assert find_entities("This is a test.") == []
    def test_my_name(self):
        assert find_entities("This is a sentence about someone named Richard Morello who is also writing it.") == [("Richard Morello", "PERSON")]
    def test_secondary_mention(self):
        assert find_entities("This is a sentence about President George Washington.  Mr Washington was our first president.") == \
            [("George Washington", "PERSON")]
    def test_place_name(self):
        assert find_entities("This sentence is about the state of California. It is a big state.") == [("California", "GPE")]
    def test_place_abbrev(self):
        assert find_entities("This sentence is about California.  Calif. is a very big state.") == [("California", "GPE")]


class TestGeoReplaceAbbreviations(unittest.TestCase):
    def test_no_replacement(self):
        assert geo_replace_abbreviation(("Test", "PERSON")) == ("Test", "PERSON")
    def test_replacement(self):
        assert geo_replace_abbreviation(("Calif.", "GPE")) == ("California", "GPE")
    def test_different_replacement(self):
        assert geo_replace_abbreviation(("CA", "GPE")) == ("California", "GPE")
    def test_usa1(self):
        assert geo_replace_abbreviation(("USA", "GPE")) == ("United States", "GPE")
    def test_usa2(self):
        assert geo_replace_abbreviation(("US", "GPE")) == ("United States", "GPE")
    def test_usa3(self):
        assert geo_replace_abbreviation(("U.S.", "GPE")) == ("United States", "GPE")
    def test_usa4(self):
        assert geo_replace_abbreviation(("U.S.A.", "GPE")) == ("United States", "GPE")
    def test_usa5(self):
        assert geo_replace_abbreviation(("the United States", "GPE")) == ("United States", "GPE")
    def test_china(self):
        assert geo_replace_abbreviation(("People's Republic of China", "GPE")) == ("China", "GPE")
