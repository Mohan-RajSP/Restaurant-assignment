from .restaurant_model import RestaurantModel, RestTableMapModel,Bookings, Booking_schema
from .restaurant_model import Restaurant_schema, TabelSchema, RestTableMapSchema
from flask import request
from flask_restx import Resource
from . import restaurant_namespace
from login.utils import field_check
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    fresh_jwt_required,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
jwt_optional
)

"""restaurant_bp = Blueprint("restaurant_bp",__name__)
restaurant_api = Api(restaurant_bp)"""

rest_schema = Restaurant_schema()
table_schema = TabelSchema()
rest_table_schema = RestTableMapSchema()
book_schema = Booking_schema()

from . import restaurant_dto


class Show_Restaurants(Resource):

    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    @restaurant_namespace.response(200, 'OK', restaurant_dto.allRestaurant_response)
    def get(self):
        """
        Step1: Shows all the restaurants in the table "restaurants"
        :return: json list of restaurants
        """
        records = RestaurantModel.show_all_restaurants()
        if len(records)==0:
            return {"message":"No Restaurants found"}, 404
        dumped_data = rest_schema.dump(records,many=True)
        out = {"message":"RETRIEVED", "restaurants":dumped_data}
        return out, 200


class Show_Tables(Resource):
    def get(self,restaurant_name):
        """
        Step2: Shows the type and count of table available with respect to the input restaurant name
        :param restaurant_name:
        :return: Table details
        """
        records = RestTableMapModel.show_table(restaurant_name)
        if len(records)>0:
            return {"message": "RETRIEVED", "restaurants": records},200
        else:
            return {"message": "Restaurant not available for booking"}, 404


class Book_Table(Resource):

    @restaurant_namespace.expect(restaurant_dto.book_table_request)
    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    def post(self):
        """
        Step3: Book the table needed and the count of availabe restaurant reduces by 1, if the count of table is 0,
        then "Tables are not available" is populated.

        """
        req_data = request.get_json()
        fields = ("Name","TableType")
        field_check(fields,req_data)
        userId = get_jwt_identity()
        booked_table = RestTableMapModel.book_table(req_data,userId)
        if not booked_table:
            return {"message": "Tables are not available"}
        return {"Table":booked_table,"message":"BOOKED"}


class OrderHistory(Resource):

    @restaurant_namespace.expect(restaurant_dto.order_history_response)
    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    def get(self):
        """
        Step4: Gives overall order history of a particular user"""
        userId = get_jwt_identity()
        booking_obj = Bookings.get_booking_by_userId(userId=userId)
        dumped_data = book_schema.dump(booking_obj, many=True)
        return {"message":"Retrieved","Orders":dumped_data},200


class Bill(Resource):
    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    @restaurant_namespace.response(200,'OK',restaurant_dto.bill_response)
    def get(self):
        """
        Step5: Gives the bill amount of unpaid bookings together
        :return:
        """
        userId = get_jwt_identity()
        booking_obj = Bookings.unpaid_booking(userId=userId)
        dumped_data = book_schema.dump(booking_obj, many=True)
        total = 0
        for datum in dumped_data:
            total += int(datum["BookingCharges"])
        out = {"Total":total, "Orders":dumped_data}
        return out,200


class CheckIn(Resource):
    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    def get(self,bookingId):
        """
        Step6: Checking in of the booked order with respect to the input booking Id provided.
        :param bookingId:
        """
        Bookings.change_status(bookingId,"CHECKEDIN")
        booking_obj = Bookings.get_booking_by_id(bookingId)
        dumped_data = book_schema.dump(booking_obj)
        return {"message":"CHECKEDIN","booking":dumped_data}


class CancelBooking(Resource):
    restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    def post(self,bookingId):
        """
        Step7: Cancel a booking which is booked priorly with respect to the input Booking Id provided
        :param bookingId:
        :return:
        """
        Bookings.change_status(bookingId,"CANCELLED")
        booking = Bookings.get_booking_status(bookingId)
        if booking:
            if booking=="CANCELLED":
                return {"message": "Booking Cancelled"}
            else:
                return {"message":booking}
        else:
            return {"message":"Booking not found"}





