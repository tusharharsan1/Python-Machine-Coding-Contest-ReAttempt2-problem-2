from typing import Dict

from exceptions.customer_session_not_found_exception import CustomerSessionNotFoundException
from models.bill import Bill
from models.customer_session_status import CustomerSessionStatus
from models.menu_item import MenuItem
from repositories.customer_session_repository import CustomerSessionRepository
from repositories.order_repository import OrderRepository

GST_RATE = 0.05             # GST is 5% of the food cost
SERVICE_CHARGE_RATE = 0.10  # the service charge is 10% of the food cost


class OrderService:
    """Holds the business logic of generating a bill.

    The repositories are given in the constructor, do NOT change the constructor.
    """

    def __init__(self, customer_session_repository: CustomerSessionRepository,
                 order_repository: OrderRepository):
        self.customer_session_repository = customer_session_repository
        self.order_repository = order_repository

    def generate_bill(self, user_id: int) -> Bill:
        """Generates the bill of the active customer session of this user and ends the session.

        Raises:
            CustomerSessionNotFoundException: if the user has no active customer session.
        """

        # Step 1: find the active session of this user, it must exist
        customer_session = self.customer_session_repository.find_active_customer_session_by_user_id(user_id)
        if customer_session is None:
            raise CustomerSessionNotFoundException(f"No active customer session for user {user_id}")

        # Step 2: end the session, so the customer cannot be billed twice for the same orders
        customer_session.customer_session_status = CustomerSessionStatus.ENDED
        self.customer_session_repository.save(customer_session)

        # Step 3: get all the orders of this session
        orders = self.order_repository.find_orders_by_customer_session(customer_session.id)

        # Step 4: put the items of all the orders together into ONE new dictionary {menu item: total quantity}
        ordered_items: Dict[MenuItem, int] = {}
        for order in orders:
            for menu_item, quantity in order.ordered_items.items():
                ordered_items[menu_item] = ordered_items.get(menu_item, 0) + quantity

        # Step 5: the food cost is the sum of price x quantity of every item
        food_cost = 0.0
        for menu_item, quantity in ordered_items.items():
            food_cost += menu_item.price * quantity

        # Step 6: the taxes are a percentage of the food cost
        gst = food_cost * GST_RATE
        service_charge = food_cost * SERVICE_CHARGE_RATE
        total_amount = food_cost + gst + service_charge

        # Step 7: create the bill and return it
        return Bill(ordered_items=ordered_items, total_amount=total_amount, gst=gst, service_charge=service_charge)
