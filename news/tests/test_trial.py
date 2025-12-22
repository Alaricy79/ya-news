from django.test import TestCase


class Test(TestCase):

    def test_example_success(self):
        self.assertTrue(True)


class YetAnotherTest(TestCase):

    def test_example_success(self):
        self.assertTrue(False)
