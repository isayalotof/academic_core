from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MenuItem(_message.Message):
    __slots__ = ("id", "name", "description", "category", "price", "available", "date")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    description: str
    category: str
    price: float
    available: bool
    date: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., price: _Optional[float] = ..., available: bool = ..., date: _Optional[str] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("id", "user_id", "user_name", "items", "total_amount", "status", "order_date", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ORDER_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    user_name: str
    items: _containers.RepeatedCompositeFieldContainer[OrderItem]
    total_amount: float
    status: str
    order_date: str
    created_at: str
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., items: _Optional[_Iterable[_Union[OrderItem, _Mapping]]] = ..., total_amount: _Optional[float] = ..., status: _Optional[str] = ..., order_date: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class OrderItem(_message.Message):
    __slots__ = ("menu_item_id", "menu_item_name", "quantity", "price")
    MENU_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    MENU_ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    menu_item_id: int
    menu_item_name: str
    quantity: int
    price: float
    def __init__(self, menu_item_id: _Optional[int] = ..., menu_item_name: _Optional[str] = ..., quantity: _Optional[int] = ..., price: _Optional[float] = ...) -> None: ...

class AddMenuItemRequest(_message.Message):
    __slots__ = ("name", "description", "category", "price", "date")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    category: str
    price: float
    date: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., price: _Optional[float] = ..., date: _Optional[str] = ...) -> None: ...

class GetMenuRequest(_message.Message):
    __slots__ = ("date",)
    DATE_FIELD_NUMBER: _ClassVar[int]
    date: str
    def __init__(self, date: _Optional[str] = ...) -> None: ...

class CreateOrderRequest(_message.Message):
    __slots__ = ("user_id", "items")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    items: _containers.RepeatedCompositeFieldContainer[OrderItemRequest]
    def __init__(self, user_id: _Optional[int] = ..., items: _Optional[_Iterable[_Union[OrderItemRequest, _Mapping]]] = ...) -> None: ...

class OrderItemRequest(_message.Message):
    __slots__ = ("menu_item_id", "quantity")
    MENU_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    menu_item_id: int
    quantity: int
    def __init__(self, menu_item_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListOrdersRequest(_message.Message):
    __slots__ = ("page", "page_size", "user_id", "status", "date")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    user_id: int
    status: str
    date: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., user_id: _Optional[int] = ..., status: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class GetBalanceRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class MenuItemResponse(_message.Message):
    __slots__ = ("item", "message")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    item: MenuItem
    message: str
    def __init__(self, item: _Optional[_Union[MenuItem, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class MenuResponse(_message.Message):
    __slots__ = ("items", "date")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[MenuItem]
    date: str
    def __init__(self, items: _Optional[_Iterable[_Union[MenuItem, _Mapping]]] = ..., date: _Optional[str] = ...) -> None: ...

class OrderResponse(_message.Message):
    __slots__ = ("order", "message")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    order: Order
    message: str
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class OrdersListResponse(_message.Message):
    __slots__ = ("orders", "total_count")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[Order]
    total_count: int
    def __init__(self, orders: _Optional[_Iterable[_Union[Order, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class BalanceResponse(_message.Message):
    __slots__ = ("balance", "message")
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    balance: float
    message: str
    def __init__(self, balance: _Optional[float] = ..., message: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version", "timestamp")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    status: str
    version: str
    timestamp: str
    def __init__(self, status: _Optional[str] = ..., version: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...
