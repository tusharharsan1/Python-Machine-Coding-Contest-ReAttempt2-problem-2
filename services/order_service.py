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

        # TODO Step 1: Find the active customer session of this user.
        #   Use: self.customer_session_repository.find_active_customer_session_by_user_id(user_id)
        #   If you get None (no active session), raise CustomerSessionNotFoundException("...some message...").

        # TODO Step 2: End the session, so it cannot be billed again.
        #   customer_session.customer_session_status = CustomerSessionStatus.ENDED
        #   Save it back: self.customer_session_repository.save(customer_session)

        # TODO Step 3: Get all the orders of this customer session.
        #   Use: self.order_repository.find_orders_by_customer_session(customer_session.id)

        # TODO Step 4: Put the items of all the orders together into ONE dictionary.
        #   ordered_items: Dict[MenuItem, int] = {}   (the key is a MenuItem, the value is the total quantity)
        #   Loop over the orders, and inside it loop over order.ordered_items.items() (menu_item, quantity).
        #   Add the quantity to what is already there:
        #       ordered_items[menu_item] = ordered_items.get(menu_item, 0) + quantity

        # TODO Step 5: Calculate the food cost.
        #   food_cost = the sum of (menu_item.price * quantity) over ordered_items

        # TODO Step 6: Calculate the taxes.
        #   gst = food_cost * GST_RATE
        #   service_charge = food_cost * SERVICE_CHARGE_RATE
        #   total_amount = food_cost + gst + service_charge

        # TODO Step 7: Create a Bill and return it (and delete the line `return None` below).
        #   Bill(ordered_items=..., total_amount=..., gst=..., service_charge=...)

        return None
