from lib.models import UsernameWithSite

class TestModels:
    def test_username_with_site_creation(self):
        user = UsernameWithSite("TestUser", "en.wikipedia.org")
        assert user.username == "TestUser"
        assert user.site == "en.wikipedia.org"

    def test_username_without_site(self):
        user = UsernameWithSite("TestUser")
        assert user.username == "TestUser"
        assert user.site is None
