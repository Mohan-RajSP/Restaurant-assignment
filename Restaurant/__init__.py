from utils import custom_log
from flask import Blueprint
from flask_restx import Api

logger = custom_log(__name__)

restaurant_bp = Blueprint("restaurant_bp",__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}

restaurant_api = Api(restaurant_bp,
                            default='Restaurant',
                            default_label='This is the Restaurant Api service',
                            version='0.0.1',
                            title='Restaurant API with Python',
                            description="Restaurant Table Booking and Payment",
                            ordered=False,
                            authorizations=authorizations,
                            security='apikey',
                         )

restaurant_namespace = restaurant_api.namespace('restaurants')

from .restaurant_views import Show_Restaurants,Book_Table,OrderHistory,Bill,Show_Tables,CancelBooking,CheckIn,\
    CreateRestaurant,CreateTableTypes,Table_Rest_Mapping

restaurant_namespace.add_resource(Show_Restaurants,"/allRestaurants")
restaurant_namespace.add_resource(Show_Tables,"/showTables/<string:restaurant_name>")
restaurant_namespace.add_resource(Book_Table,"/bookTable")
restaurant_namespace.add_resource(OrderHistory,"/orderHistory")
restaurant_namespace.add_resource(Bill,"/bill")
restaurant_namespace.add_resource(CancelBooking,"/cancelBooking/<string:bookingId>")
restaurant_namespace.add_resource(CheckIn,"/checkIn/<string:bookingId>")
restaurant_namespace.add_resource(CreateRestaurant,"/createRestaurant")
restaurant_namespace.add_resource(CreateTableTypes,"/createTableType")
restaurant_namespace.add_resource(Table_Rest_Mapping,"/appendTableType")
