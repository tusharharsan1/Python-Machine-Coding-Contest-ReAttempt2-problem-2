import unittest

from controllers.order_controller import OrderController
from dtos.generate_bill_request_dto import GenerateBillRequestDto
from dtos.response_status import ResponseStatus
from exceptions.customer_session_not_found_exception import CustomerSessionNotFoundException
from models.bill import Bill
from models.customer_session import CustomerSession
from models.customer_session_status import CustomerSessionStatus
from models.menu_item import MenuItem
from models.order import Order
from models.user import User
from repositories.in_memory_customer_session_repository import InMemoryCustomerSessionRepository
from repositories.in_memory_order_repository import InMemoryOrderRepository
from services.order_service import OrderService


class SpySessionRepository(InMemoryCustomerSessionRepository):
    """Same as the normal repository, but it remembers the status of every session which was saved."""

    def __init__(self):
        super().__init__()
        self.saved_statuses = []

    def save(self, customer_session):
        self.saved_statuses.append(customer_session.customer_session_status)
        return super().save(customer_session)


class BillTestBase(unittest.TestCase):
    """Common setup used by the test classes below.

    Before EVERY test we build brand new, empty repositories, and these menu items and users:

        dosa 100.0    coffee 50.0    idli 30.5    biryani 250.0
        users: Asha (id 1), Bala (id 2), Chitra (id 3)
    """

    def setUp(self):
        self.session_repository = InMemoryCustomerSessionRepository()
        self.order_repository = InMemoryOrderRepository()
        self.service = OrderService(self.session_repository, self.order_repository)
        self.controller = OrderController(self.service)

        self.dosa = MenuItem(id=1, name="Dosa", price=100.0)
        self.coffee = MenuItem(id=2, name="Coffee", price=50.0)
        self.idli = MenuItem(id=3, name="Idli", price=30.5)
        self.biryani = MenuItem(id=4, name="Biryani", price=250.0)

        self.asha = User(id=1, name="Asha")
        self.bala = User(id=2, name="Bala")
        self.chitra = User(id=3, name="Chitra")

    # ---------- helpers ----------
    def _session(self, user, status=CustomerSessionStatus.ACTIVE):
        return self.session_repository.save(CustomerSession(user=user, customer_session_status=status))

    def _order(self, session, items):
        """items = {menu item: quantity}"""
        return self.order_repository.save(Order(customer_session=session, ordered_items=dict(items)))

    def _bill(self, user):
        return self.service.generate_bill(user.id)

    def assert_amounts(self, bill, food_cost):
        """The bill must have GST 5%, service charge 10% and a total of the three together."""
        self.assertAlmostEqual(food_cost * 0.05, bill.gst, places=6)
        self.assertAlmostEqual(food_cost * 0.10, bill.service_charge, places=6)
        self.assertAlmostEqual(food_cost * 1.15, bill.total_amount, places=6)


# ======================================================================================
# 1. The two repositories (each can earn marks on its own)
# ======================================================================================
class RepositoryTest(BillTestBase):

    # ---------- sessions ----------
    def test_finds_the_active_session_of_the_user(self):
        session = self._session(self.asha)
        found = self.session_repository.find_active_customer_session_by_user_id(self.asha.id)
        self.assertIsNotNone(found)
        self.assertIs(session, found)

    def test_no_session_gives_none(self):
        self._session(self.asha)
        self.assertIsNotNone(self.session_repository.find_active_customer_session_by_user_id(1))
        self.assertIsNone(self.session_repository.find_active_customer_session_by_user_id(99))

    def test_an_ended_session_is_not_found(self):
        self._session(self.asha)
        self._session(self.bala, CustomerSessionStatus.ENDED)
        self.assertIsNotNone(self.session_repository.find_active_customer_session_by_user_id(self.asha.id))
        self.assertIsNone(self.session_repository.find_active_customer_session_by_user_id(self.bala.id))

    def test_the_session_of_another_user_is_not_returned(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.bala)
        self.assertIs(bala_session, self.session_repository.find_active_customer_session_by_user_id(self.bala.id))
        self.assertIs(asha_session, self.session_repository.find_active_customer_session_by_user_id(self.asha.id))

    def test_the_active_session_is_found_among_ended_ones(self):
        self._session(self.asha, CustomerSessionStatus.ENDED)
        active = self._session(self.asha)
        self._session(self.asha, CustomerSessionStatus.ENDED)
        self.assertIs(active, self.session_repository.find_active_customer_session_by_user_id(self.asha.id))

    def test_user_ids_are_compared_exactly(self):
        ten = User(id=10, name="Ten")
        self._session(ten)
        self.assertIsNotNone(self.session_repository.find_active_customer_session_by_user_id(10))
        self.assertIsNone(self.session_repository.find_active_customer_session_by_user_id(1))

    def test_a_session_which_ends_is_not_found_any_more(self):
        session = self._session(self.asha)
        self.assertIsNotNone(self.session_repository.find_active_customer_session_by_user_id(self.asha.id))
        session.customer_session_status = CustomerSessionStatus.ENDED
        self.session_repository.save(session)
        self.assertIsNone(self.session_repository.find_active_customer_session_by_user_id(self.asha.id))

    # ---------- orders ----------
    def test_finds_the_orders_of_a_session(self):
        session = self._session(self.asha)
        first = self._order(session, {self.dosa: 1})
        second = self._order(session, {self.coffee: 2})
        found = self.order_repository.find_orders_by_customer_session(session.id)
        self.assertEqual(2, len(found))
        self.assertEqual({first.id, second.id}, {order.id for order in found})

    def test_the_orders_of_another_session_are_not_returned(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.bala)
        mine = self._order(asha_session, {self.dosa: 1})
        self._order(bala_session, {self.coffee: 1})
        self._order(bala_session, {self.idli: 1})
        found = self.order_repository.find_orders_by_customer_session(asha_session.id)
        self.assertEqual([mine.id], [order.id for order in found])

    def test_a_session_without_orders_gives_an_empty_list(self):
        session = self._session(self.asha)
        other = self._session(self.bala)
        self._order(other, {self.dosa: 1})
        self.assertEqual(1, len(self.order_repository.find_orders_by_customer_session(other.id)))
        self.assertEqual([], self.order_repository.find_orders_by_customer_session(session.id))

    def test_an_unknown_session_id_gives_an_empty_list(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertEqual(1, len(self.order_repository.find_orders_by_customer_session(session.id)))
        self.assertEqual([], self.order_repository.find_orders_by_customer_session(9999))

    def test_the_found_orders_are_the_saved_order_objects(self):
        session = self._session(self.asha)
        order = self._order(session, {self.dosa: 3})
        found = self.order_repository.find_orders_by_customer_session(session.id)
        self.assertIs(order, found[0])
        self.assertIsInstance(found, list)


# ======================================================================================
# 2. The controller alone: a fake service lets us check ONLY what the controller does
# ======================================================================================
class FakeOrderService:
    """Pretends to be OrderService. Remembers how it was called."""

    def __init__(self, bill_to_return=None, error_to_raise=None):
        self.bill_to_return = bill_to_return
        self.error_to_raise = error_to_raise
        self.calls = []

    def generate_bill(self, user_id):
        self.calls.append(user_id)
        if self.error_to_raise is not None:
            raise self.error_to_raise
        return self.bill_to_return


class ControllerOnlyTest(unittest.TestCase):

    def test_success_returns_the_bill_from_the_service_and_success_status(self):
        bill = Bill()
        response = OrderController(FakeOrderService(bill_to_return=bill)).generate_bill(GenerateBillRequestDto(5))
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertIs(bill, response.bill)

    def test_controller_passes_the_user_id_of_the_request(self):
        service = FakeOrderService(bill_to_return=Bill())
        OrderController(service).generate_bill(GenerateBillRequestDto(user_id=42))
        self.assertEqual([42], service.calls)

    def test_controller_passes_another_user_id_too(self):
        service = FakeOrderService(bill_to_return=Bill())
        OrderController(service).generate_bill(GenerateBillRequestDto(user_id=7))
        self.assertEqual([7], service.calls)

    def test_any_exception_gives_failure_and_no_bill(self):
        for error in (CustomerSessionNotFoundException("x"), RuntimeError("other"), ValueError("v")):
            with self.subTest(error=type(error).__name__):
                response = OrderController(FakeOrderService(error_to_raise=error)).generate_bill(
                    GenerateBillRequestDto(1))
                self.assertEqual(ResponseStatus.FAILURE, response.response_status)
                self.assertIsNone(response.bill)

    def test_the_controller_does_not_raise_when_the_service_fails(self):
        controller = OrderController(FakeOrderService(error_to_raise=KeyError("boom")))
        try:
            response = controller.generate_bill(GenerateBillRequestDto(1))
        except Exception as error:
            self.fail(f"The controller must catch the exception, but it raised {error!r}")
        self.assertEqual(ResponseStatus.FAILURE, response.response_status)


# ======================================================================================
# 3. The service: the bill
# ======================================================================================
class BillAmountsTest(BillTestBase):

    def test_bill_of_one_order_with_one_item(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        bill = self._bill(self.asha)
        self.assertIsInstance(bill, Bill)
        self.assert_amounts(bill, 100.0)

    def test_food_cost_is_price_times_quantity(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 3})
        self.assert_amounts(self._bill(self.asha), 300.0)

    def test_food_cost_of_several_items(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2, self.coffee: 1})   # 200 + 50
        bill = self._bill(self.asha)
        self.assertAlmostEqual(12.5, bill.gst, places=6)
        self.assertAlmostEqual(25.0, bill.service_charge, places=6)
        self.assertAlmostEqual(287.5, bill.total_amount, places=6)

    def test_prices_with_decimals(self):
        session = self._session(self.asha)
        self._order(session, {self.idli: 3})   # 91.5
        bill = self._bill(self.asha)
        self.assertAlmostEqual(4.575, bill.gst, places=6)
        self.assertAlmostEqual(9.15, bill.service_charge, places=6)
        self.assertAlmostEqual(105.225, bill.total_amount, places=6)

    def test_gst_is_five_percent_and_service_charge_is_ten_percent(self):
        session = self._session(self.asha)
        self._order(session, {self.biryani: 4})   # 1000
        bill = self._bill(self.asha)
        self.assertAlmostEqual(50.0, bill.gst, places=6)
        self.assertAlmostEqual(100.0, bill.service_charge, places=6)

    def test_total_amount_includes_the_food_cost_gst_and_service_charge(self):
        session = self._session(self.asha)
        self._order(session, {self.biryani: 4})   # 1000 + 50 + 100
        self.assertAlmostEqual(1150.0, self._bill(self.asha).total_amount, places=6)

    def test_taxes_are_calculated_on_the_food_cost_only(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 10})   # 1000
        bill = self._bill(self.asha)
        # the service charge is not taxed and the GST is not part of the service charge
        self.assertAlmostEqual(bill.total_amount, 1000.0 + bill.gst + bill.service_charge, places=6)
        self.assertAlmostEqual(100.0, bill.service_charge, places=6)

    def test_amounts_are_numbers_with_decimals_allowed(self):
        session = self._session(self.asha)
        self._order(session, {self.idli: 1})
        bill = self._bill(self.asha)
        self.assertIsInstance(bill.total_amount, float)
        self.assertIsInstance(bill.gst, float)
        self.assertIsInstance(bill.service_charge, float)

    def test_big_quantities(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1000, self.coffee: 2000})
        self.assert_amounts(self._bill(self.asha), 200000.0)


class BillItemsTest(BillTestBase):

    def test_bill_lists_the_ordered_items_with_their_quantities(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2, self.coffee: 1})
        bill = self._bill(self.asha)
        self.assertEqual({self.dosa: 2, self.coffee: 1}, bill.ordered_items)

    def test_the_orders_of_the_session_are_added_together(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self._order(session, {self.coffee: 2})
        self._order(session, {self.idli: 3})
        bill = self._bill(self.asha)
        self.assertEqual({self.dosa: 1, self.coffee: 2, self.idli: 3}, bill.ordered_items)
        self.assert_amounts(bill, 100.0 + 100.0 + 91.5)

    def test_the_same_item_in_many_orders_appears_once_with_the_total_quantity(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2, self.coffee: 1})
        self._order(session, {self.dosa: 3})
        self._order(session, {self.coffee: 4, self.dosa: 1})
        bill = self._bill(self.asha)
        self.assertEqual(2, len(bill.ordered_items))
        self.assertEqual(6, bill.ordered_items[self.dosa])
        self.assertEqual(5, bill.ordered_items[self.coffee])
        self.assert_amounts(bill, 6 * 100.0 + 5 * 50.0)

    def test_quantities_are_added_not_replaced(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2})
        self._order(session, {self.dosa: 5})
        self.assertEqual(7, self._bill(self.asha).ordered_items[self.dosa])

    def test_every_order_counts_including_the_last_one_and_the_first_one(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self._order(session, {self.coffee: 1})
        self._order(session, {self.idli: 1})
        self._order(session, {self.biryani: 1})
        bill = self._bill(self.asha)
        self.assertEqual({self.dosa, self.coffee, self.idli, self.biryani}, set(bill.ordered_items.keys()))

    def test_the_keys_of_the_bill_are_the_menu_items_themselves(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        bill = self._bill(self.asha)
        self.assertIs(self.dosa, list(bill.ordered_items.keys())[0])

    def test_a_session_without_orders_gives_an_empty_bill_and_still_ends(self):
        session = self._session(self.asha)
        bill = self._bill(self.asha)
        self.assertIsInstance(bill, Bill)
        self.assertEqual({}, bill.ordered_items)
        self.assertEqual(0, bill.total_amount)
        self.assertEqual(0, bill.gst)
        self.assertEqual(0, bill.service_charge)
        self.assertEqual(CustomerSessionStatus.ENDED, session.customer_session_status)

    def test_an_order_without_items_adds_nothing(self):
        session = self._session(self.asha)
        self._order(session, {})
        self._order(session, {self.dosa: 1})
        bill = self._bill(self.asha)
        self.assertEqual({self.dosa: 1}, bill.ordered_items)

    # ---------- only the orders of the right session ----------
    def test_the_orders_of_other_customers_are_not_in_the_bill(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.bala)
        self._order(asha_session, {self.dosa: 1})
        self._order(bala_session, {self.biryani: 5})
        bill = self._bill(self.asha)
        self.assertEqual({self.dosa: 1}, bill.ordered_items)
        self.assert_amounts(bill, 100.0)

    def test_each_customer_gets_their_own_bill(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.bala)
        self._order(asha_session, {self.dosa: 1})
        self._order(bala_session, {self.biryani: 2})
        self.assert_amounts(self._bill(self.bala), 500.0)
        self.assert_amounts(self._bill(self.asha), 100.0)

    def test_the_orders_of_an_earlier_ended_session_are_not_in_the_bill(self):
        old_session = self._session(self.asha, CustomerSessionStatus.ENDED)
        self._order(old_session, {self.biryani: 3})
        new_session = self._session(self.asha)
        self._order(new_session, {self.coffee: 1})
        bill = self._bill(self.asha)
        self.assertEqual({self.coffee: 1}, bill.ordered_items)
        self.assert_amounts(bill, 50.0)

    def test_the_bill_can_be_generated_again_for_a_new_session_of_the_same_customer(self):
        first = self._session(self.asha)
        self._order(first, {self.dosa: 1})
        self.assert_amounts(self._bill(self.asha), 100.0)
        second = self._session(self.asha)
        self._order(second, {self.coffee: 2})
        bill = self._bill(self.asha)
        self.assertEqual({self.coffee: 2}, bill.ordered_items)
        self.assert_amounts(bill, 100.0)

    # ---------- things which must not change ----------
    def test_the_orders_are_not_changed(self):
        session = self._session(self.asha)
        first = self._order(session, {self.dosa: 1})
        second = self._order(session, {self.dosa: 2, self.coffee: 1})
        self.assertEqual({self.dosa: 3, self.coffee: 1}, self._bill(self.asha).ordered_items)
        self.assertEqual({self.dosa: 1}, first.ordered_items)
        self.assertEqual({self.dosa: 2, self.coffee: 1}, second.ordered_items)

    def test_the_bill_does_not_share_its_dictionary_with_an_order(self):
        session = self._session(self.asha)
        order = self._order(session, {self.dosa: 1})
        bill = self._bill(self.asha)
        self.assertIsNot(order.ordered_items, bill.ordered_items)

    def test_the_menu_items_are_not_changed(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2, self.coffee: 1})
        self.assertIsNotNone(self._bill(self.asha))
        self.assertEqual((100.0, 50.0), (self.dosa.price, self.coffee.price))
        self.assertEqual(("Dosa", "Coffee"), (self.dosa.name, self.coffee.name))


class SessionRulesTest(BillTestBase):

    def test_the_session_is_ended_after_the_bill(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertIsNotNone(self._bill(self.asha))
        self.assertEqual(CustomerSessionStatus.ENDED, session.customer_session_status)
        self.assertFalse(session.is_active())

    def test_the_ended_session_is_saved_in_the_repository(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertIsNotNone(self._bill(self.asha))
        self.assertIsNone(self.session_repository.find_active_customer_session_by_user_id(self.asha.id))

    def test_the_session_is_saved_back_with_the_status_ended(self):
        spy = SpySessionRepository()
        service = OrderService(spy, self.order_repository)
        session = spy.save(CustomerSession(user=self.asha))
        self._order(session, {self.dosa: 1})
        self.assertIsNotNone(service.generate_bill(self.asha.id))
        self.assertEqual(CustomerSessionStatus.ENDED, spy.saved_statuses[-1])

    def test_a_bill_cannot_be_generated_twice_for_the_same_session(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertIsNotNone(self._bill(self.asha))
        with self.assertRaises(CustomerSessionNotFoundException):
            self._bill(self.asha)

    def test_only_the_session_of_the_customer_is_ended(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.bala)
        self.assertIsNotNone(self._bill(self.asha))
        self.assertEqual(CustomerSessionStatus.ENDED, asha_session.customer_session_status)
        self.assertEqual(CustomerSessionStatus.ACTIVE, bala_session.customer_session_status)

    # ---------- no active session ----------
    def test_a_customer_without_a_session_raises_customer_session_not_found(self):
        self._session(self.asha)
        self.assertIsNotNone(self._bill(self.asha))   # the service works for a customer with a session
        with self.assertRaises(CustomerSessionNotFoundException):
            self._bill(self.bala)

    def test_an_unknown_user_id_raises_customer_session_not_found(self):
        with self.assertRaises(CustomerSessionNotFoundException):
            self.service.generate_bill(999)

    def test_a_customer_with_only_an_ended_session_raises(self):
        session = self._session(self.asha, CustomerSessionStatus.ENDED)
        self._order(session, {self.dosa: 1})
        self._session(self.bala)
        self.assertIsNotNone(self._bill(self.bala))
        with self.assertRaises(CustomerSessionNotFoundException):
            self._bill(self.asha)

    def test_the_not_found_message_is_not_empty(self):
        with self.assertRaises(CustomerSessionNotFoundException) as context:
            self.service.generate_bill(999)
        self.assertTrue(str(context.exception).strip())

    def test_a_failed_bill_changes_nothing(self):
        bala_session = self._session(self.bala)
        order = self._order(bala_session, {self.dosa: 1})
        with self.assertRaises(CustomerSessionNotFoundException):
            self._bill(self.asha)
        self.assertEqual(CustomerSessionStatus.ACTIVE, bala_session.customer_session_status)
        self.assertEqual({self.dosa: 1}, order.ordered_items)
        self.assert_amounts(self._bill(self.bala), 100.0)


# ======================================================================================
# 4. The whole flow through the controller
# ======================================================================================
class ControllerFlowTest(BillTestBase):

    def _generate(self, user):
        return self.controller.generate_bill(GenerateBillRequestDto(user_id=user.id))

    def test_the_controller_returns_the_bill(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 2, self.coffee: 1})
        self._order(session, {self.coffee: 3})
        response = self._generate(self.asha)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual({self.dosa: 2, self.coffee: 4}, response.bill.ordered_items)
        self.assertAlmostEqual(20.0, response.bill.gst, places=6)
        self.assertAlmostEqual(40.0, response.bill.service_charge, places=6)
        self.assertAlmostEqual(460.0, response.bill.total_amount, places=6)

    def test_the_controller_uses_the_user_id_of_the_request(self):
        asha_session = self._session(self.asha)
        bala_session = self._session(self.chitra)
        self._order(asha_session, {self.dosa: 1})
        self._order(bala_session, {self.biryani: 1})
        self.assertAlmostEqual(115.0, self._generate(self.asha).bill.total_amount, places=6)
        self.assertAlmostEqual(287.5, self._generate(self.chitra).bill.total_amount, places=6)

    def test_a_customer_without_a_session_gets_failure_and_no_bill(self):
        response = self._generate(self.asha)
        self.assertEqual(ResponseStatus.FAILURE, response.response_status)
        self.assertIsNone(response.bill)

    def test_the_second_request_for_the_same_session_fails(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        first = self._generate(self.asha)
        second = self._generate(self.asha)
        self.assertEqual(ResponseStatus.SUCCESS, first.response_status)
        self.assertEqual(ResponseStatus.FAILURE, second.response_status)
        self.assertIsNone(second.bill)

    def test_a_failure_does_not_stop_the_next_request(self):
        self.assertEqual(ResponseStatus.FAILURE, self._generate(self.asha).response_status)
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertEqual(ResponseStatus.SUCCESS, self._generate(self.asha).response_status)

    def test_the_bill_of_a_session_without_orders_is_a_success(self):
        self._session(self.asha)
        response = self._generate(self.asha)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual(0, response.bill.total_amount)

    def test_the_session_is_ended_after_a_successful_request(self):
        session = self._session(self.asha)
        self._order(session, {self.dosa: 1})
        self.assertEqual(ResponseStatus.SUCCESS, self._generate(self.asha).response_status)
        self.assertEqual(CustomerSessionStatus.ENDED, session.customer_session_status)


if __name__ == "__main__":
    unittest.main()
