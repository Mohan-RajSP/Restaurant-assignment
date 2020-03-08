from . import restaurant_api
from flask_restx import fields

tabletype_create_request = restaurant_api.model('restaurant_create_request',{
   "TableType":fields.Integer(),
})

restaurant_create_request = restaurant_api.model('restaurant_create_request',{
    'Contact': fields.String(),
    'Location': fields.String(),
    'Name': fields.String(),
})

allRestaurant_list = restaurant_api.model('allRestaurant_list',{
    'Contact': fields.String(),
    'Location': fields.String(),
    'Name': fields.String(),
    'Id': fields.Integer(),
})

allRestaurant_response = restaurant_api.inherit('allRestaurant_response', {
    'Message': fields.String(),
    "Restaurants":fields.List(fields.Nested(allRestaurant_list)),
})


restaurant_table_list = restaurant_api.clone("restaurant_table_list",allRestaurant_list,{
    "BookingCharges":fields.String(),
    "TableType": fields.String(),
    "TableCount": fields.Integer(),
})

rest_table_map_request = restaurant_api.clone("rest_table_map_request",{
"BookingCharges":fields.String(),
    "TableType": fields.String(),
    "TableCount": fields.Integer(),
    "RestaurantId":fields.Integer(),
})

book_table_request = restaurant_api.model("book_table_request",{
    "Name":fields.String(),
    "TableType":fields.String(),
})

booking_details = restaurant_api.model('bill_list',{
    "BookingCharges": fields.String(),
    "Location": fields.String(),
    "Name": fields.String(),
    "TableType": fields.String(),
})

book_table_response = restaurant_api.model("book_table_response",{
    "Table":fields.Nested(booking_details),
    "message":fields.String()
})

bill_list = restaurant_api.model('bill_list',{
    "BookingStatus": fields.String(),
    "BookingCharges": fields.String(),
    "PaymentStatus": fields.String(enum=["PAID","NOTPAID"]),
    "Location": fields.String(),
    "Name": fields.String(),
    "TableType": fields.String(),
    "Id": fields.Integer()
})

bill_response = restaurant_api.inherit('allRestaurant_response', {
    'Message': fields.String(),
    "Total":fields.String(),
    "Orders":fields.List(fields.Nested(bill_list))
})


order_history_response = restaurant_api.inherit('order_history_response', {
    'Message': fields.String(),
    "Orders":fields.List(fields.Nested(allRestaurant_list))
})
