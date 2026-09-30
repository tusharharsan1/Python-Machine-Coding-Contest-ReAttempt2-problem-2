"""A small demo of the bill generation. Run it with:  python main.py
Nothing to change in this file.
"""
from controllers.order_controller import OrderController
from dtos.generate_bill_request_dto import GenerateBillRequestDto
from models.customer_session import CustomerSession
from models.menu_item import MenuItem
from models.order import Order
from models.user import User
from repositories.in_memory_customer_session_repository import InMemoryCustomerSessionRepository
from repositories.in_memory_order_repository import InMemoryOrderRepository
from services.order_service import OrderService


def main():
    session_repository = InMemoryCustomerSessionRepository()
    order_repository = InMemoryOrderRepository()
    controller = OrderController(OrderService(session_repository, order_repository))

    # a customer with an active session and two orders
    asha = User(id=1, name="Asha")
    session = session_repository.save(CustomerSession(user=asha))
    dosa = MenuItem(id=1, name="Dosa", price=100.0)
    coffee = MenuItem(id=2, name="Coffee", price=50.0)
    order_repository.save(Order(customer_session=session, ordered_items={dosa: 2, coffee: 1}))
    order_repository.save(Order(customer_session=session, ordered_items={coffee: 3}))

    response = controller.generate_bill(GenerateBillRequestDto(user_id=asha.id))
    print("Status:", response.response_status)
    if response.bill is not None:
        bill = response.bill
        print("Items:", {item.name: quantity for item, quantity in bill.ordered_items.items()})
        print("GST:", bill.gst, "| service charge:", bill.service_charge, "| total:", bill.total_amount)

    # the session has ended, so a second bill cannot be generated
    print("Second bill:", controller.generate_bill(GenerateBillRequestDto(user_id=asha.id)).response_status)


if __name__ == "__main__":
    main()
