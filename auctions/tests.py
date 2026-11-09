"AI-written tests"

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connections
from django.test import SimpleTestCase, TestCase, TransactionTestCase
from django.utils import timezone

from .models import Auction, Bid
from .services import place_bid


class ProjectSetupTests(SimpleTestCase):

    # This is our first very basic test to verify that CI setup is correct
    # It checks wheter the auctions app is registered in the project settings
    # We will be adding more complex tests here as we develop the app
    def test_auctions_app_is_installed(self):
        self.assertIn("auctions", settings.INSTALLED_APPS)


def create_test_user(name):
    User = get_user_model()
    login = f"{name}@example.com" if User.USERNAME_FIELD == "email" else name
    return User.objects.create_user(
        **{User.USERNAME_FIELD: login},
        password="test-password-123",
    )


class PlaceBidTests(TestCase):

    def setUp(self):
        self.alice = create_test_user("alice")
        self.bob = create_test_user("bob")

        self.auction = Auction.objects.create(
            title="Test Painting",
            starting_price=Decimal("100.00"),
            minimum_increment=Decimal("10.00"),
            ends_at=timezone.now() + timedelta(days=1),
            closed=False,
        )

    def test_first_bid_at_starting_price(self):
        bid = place_bid(
            self.auction.pk,
            self.alice,
            Decimal("100.00"),
        )

        self.assertEqual(bid.amount, Decimal("100.00"))
        self.assertEqual(Bid.objects.count(), 1)

    def test_first_bid_below_starting_price(self):
        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, self.alice, Decimal("99.00"))

        self.assertEqual(Bid.objects.count(), 0)

    def test_valid_minimum_increment(self):
        place_bid(self.auction.pk, self.alice, Decimal("100.00"))

        bid = place_bid(
            self.auction.pk,
            self.bob,
            Decimal("110.00"),
        )

        self.assertEqual(bid.amount, Decimal("110.00"))
        self.assertEqual(Bid.objects.count(), 2)

    def test_bid_below_minimum_increment(self):
        place_bid(self.auction.pk, self.alice, Decimal("100.00"))

        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, self.bob, Decimal("105.00"))

        self.assertEqual(Bid.objects.count(), 1)

    def test_user_can_outbid_themselves(self):
        place_bid(self.auction.pk, self.alice, Decimal("100.00"))
        place_bid(self.auction.pk, self.alice, Decimal("110.00"))

        self.assertEqual(Bid.objects.count(), 2)

    def test_invalid_amount(self):
        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, self.alice, "abc")

        self.assertEqual(Bid.objects.count(), 0)

    def test_unauthenticated_user(self):
        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, AnonymousUser(), Decimal("100.00"))

        self.assertEqual(Bid.objects.count(), 0)

    def test_missing_user(self):
        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, None, Decimal("100.00"))

    def test_closed_auction(self):
        self.auction.closed = True
        self.auction.save()

        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, self.alice, Decimal("100.00"))

        self.assertEqual(Bid.objects.count(), 0)

    def test_expired_auction(self):
        self.auction.ends_at = timezone.now() - timedelta(seconds=1)
        self.auction.save()

        with self.assertRaises(ValidationError):
            place_bid(self.auction.pk, self.alice, Decimal("100.00"))

        self.assertEqual(Bid.objects.count(), 0)

    def test_nonexistent_auction(self):
        with self.assertRaises(Auction.DoesNotExist):
            place_bid(999999, self.alice, Decimal("100.00"))


class ConcurrentBiddingTests(TransactionTestCase):

    def setUp(self):
        self.alice = create_test_user("concurrent_alice")
        self.bob = create_test_user("concurrent_bob")

        self.auction = Auction.objects.create(
            title="Concurrent Auction",
            starting_price=Decimal("100.00"),
            minimum_increment=Decimal("10.00"),
            ends_at=timezone.now() + timedelta(days=1),
            closed=False,
        )

    def test_concurrent_bids_same_amount(self):
        # Create an initial bid
        place_bid(self.auction.pk, self.alice, Decimal("100.00"))

        # Synchronize the start of both threads
        barrier = Barrier(2)

        def attempt_bid(user_id):
            close_old_connections()

            try:
                user = get_user_model().objects.get(pk=user_id)

                # Both threads start bidding together
                barrier.wait(timeout=10)

                try:
                    place_bid(
                        self.auction.pk,
                        user,
                        Decimal("110.00"),
                    )
                    return "accepted"

                except ValidationError:
                    return "rejected"

            finally:
                connections.close_all()

        # Two threads, two independent database connections
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(attempt_bid, self.alice.pk)
            second = executor.submit(attempt_bid, self.bob.pk)

            results = [
                first.result(timeout=20),
                second.result(timeout=20),
            ]

        # Exactly one competing bid should succeed
        self.assertCountEqual(
            results,
            ["accepted", "rejected"],
        )

        # Initial bid + exactly one successful new bid
        self.assertEqual(Bid.objects.count(), 2)

        # Verify the final highest bid
        highest_bid = Bid.objects.order_by("-amount").first()

        self.assertEqual(
            highest_bid.amount,
            Decimal("110.00"),
        )
