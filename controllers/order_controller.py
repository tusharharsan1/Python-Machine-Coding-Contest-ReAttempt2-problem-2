from dtos.generate_bill_request_dto import GenerateBillRequestDto
from dtos.generate_bill_response_dto import GenerateBillResponseDto
from dtos.response_status import ResponseStatus
from services.order_service import OrderService


class OrderController:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    def generate_bill(self, request_dto: GenerateBillRequestDto) -> GenerateBillResponseDto:
        response_dto = GenerateBillResponseDto()
        try:
            # TODO: 1. Call self.order_service.generate_bill(request_dto.user_id)
            #       2. Put the Bill that comes back in response_dto.bill
            #       3. Set response_dto.response_status = ResponseStatus.SUCCESS
            pass
        except Exception:
            # If ANY exception happens (for example the customer session is not found), the status is FAILURE
            # and the bill must stay None.
            response_dto.response_status = ResponseStatus.FAILURE
        return response_dto
