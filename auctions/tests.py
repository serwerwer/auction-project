from django.conf import settings
from django.test import SimpleTestCase

class ProjectSetupTests(SimpleTestCase):

    # This is our first very basic test to verify that CI setup is correct
    # It checks wheter the auctions app is registered in the project settings
    # We will be adding more complex tests here as we develop the app
    def test_auctions_app_is_installed(self):
        self.assertIn("auctions", settings.INSTALLED_APPS)