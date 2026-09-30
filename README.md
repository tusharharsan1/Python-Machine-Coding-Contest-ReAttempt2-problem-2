# Generate Bill for Restaurant Management System

## Problem Statement

You are building a Restaurant Management System. As a part of this system, you need to build a functionality using which customers can generate a bill for their orders.

## Assignment

Your task is to implement the following functionality.

#### Requirements

1. Generally a customer places multiple orders before requesting for the bill. Hence, our system must be able to track orders placed by a customer.
    * We have an entity called as `CustomerSession` in our system which helps us track the orders placed by a customer.
    * Once the customer places their 1st order, a `CustomerSession` is created for them with status as `ACTIVE`.
    * All the subsequent orders placed by the customer are associated with the `CustomerSession` created for them.
    * Once the customer requests for the bill, we should mark the `CustomerSession` as `ENDED`.
    * (Creating sessions and placing orders is not part of this assignment. You only generate the bill.)
2. The request for generating the bill will contain just the customer id (`user_id`).
3. This functionality should aggregate the items ordered by the customer and calculate the total amount to be paid by the customer.
    * Only the orders of the customer's `ACTIVE` session are part of the bill.
    * If the customer has no `ACTIVE` session, the bill cannot be generated: raise `CustomerSessionNotFoundException`. Nothing should be changed then.
    * If the session has no orders, the bill is empty and all its amounts are 0. The session still ends.
    * The same item ordered several times (in one order or in many orders) appears once in the bill, with the total quantity. Two items are the same item if they are the same `MenuItem` object.
4. This functionality should also calculate GST and service charge on the total amount.
5. GST will be 5% of the total food cost and service charge will be 10% of the total food cost. The `total_amount` of the bill is the food cost + GST + service charge.
6. Return the bill details in the response. Amounts are compared with a small tolerance, so tiny decimal differences do not matter.

#### Instructions (Expected Time: 30 - 35 minutes)

1. Implement the `generate_bill` method inside the `OrderController` class. The controller should call the service and wrap any exception into a FAILURE response status.
2. Complete the class `OrderService` in `services/order_service.py`. This is where your business logic lives. Its constructor takes `(customer_session_repository, order_repository)`, do not change it.
3. Complete the class `InMemoryCustomerSessionRepository`. This stores sessions in memory using a dictionary.
4. Complete the class `InMemoryOrderRepository`. This stores orders in memory using a dictionary.
5. Refer to `GenerateBillRequestDto` and `GenerateBillResponseDto` for understanding the expected input and output.
6. Refer to the models package to understand the data structures (`CustomerSession`, `Order`, `Bill`, `MenuItem`, etc.).
7. Do not change the names of the existing methods and classes. You may add more methods if required.
