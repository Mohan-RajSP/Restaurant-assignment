from .restaurant_model import RestaurantModel, RestTableMapModel,Bookings, Booking_schema,TableModel
from .restaurant_model import Restaurant_schema, TabelSchema, RestTableMapSchema
from flask import request
from flask_restx import Resource
from . import restaurant_namespace
from utils import field_check
from flask_jwt_extended import (
    get_jwt_identity, jwt_required,jwt_optional,fresh_jwt_required
)

"""restaurant_bp = Blueprint("restaurant_bp",__name__)
restaurant_api = Api(restaurant_bp)"""

rest_schema = Restaurant_schema()
table_schema = TabelSchema()
rest_table_schema = RestTableMapSchema()
book_schema = Booking_schema()

from . import restaurant_dto


class Show_Restaurants(Resource):

    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @restaurant_namespace.response(200, 'OK', restaurant_dto.allRestaurant_response)
    @jwt_required
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


class CreateTableTypes(Resource):

    @restaurant_namespace.expect(restaurant_dto.tabletype_create_request)
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def post(self):
        """
        Step2: Feed in the table type each restaurant are expected to have like 2,4,8,12 seater"""
        req_data = request.get_json()
        print("req", req_data)
        loaded_data = table_schema.load(req_data)
        obj = TableModel(loaded_data)
        obj = obj.insert_tableType(obj)
        dumped_data = table_schema.dump(obj)
        return {"message":"CREATED","TableType":dumped_data},200


class CreateRestaurant(Resource):

    @restaurant_namespace.expect(restaurant_dto.restaurant_create_request)
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def post(self):
        """
        Step3: Feed in the new restuarants to be populated and booked by people. Taken care from admin user"""
        req_data = request.get_json()
        rest_obj = RestaurantModel.check_by_name(req_data["Name"])
        if rest_obj:
            return {"message": "Restaurant already exist"}, 424
        loaded_data = rest_schema.load(req_data,partial=True)
        rest_obj = RestaurantModel(loaded_data)
        rest_obj = rest_obj.create_restaurant()
        dumped_data = rest_table_schema.dump(rest_obj)
        return {"message": "CREATED", "Restaurant": dumped_data}, 200


class Table_Rest_Mapping(Resource):
    @restaurant_namespace.expect(restaurant_dto.rest_table_map_request)
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def post(self):
        """
        Step3: Feed in the new restuarants to be populated and booked by people. Taken care from admin user"""
        req_data = request.get_json()
        req_data["TableTypeId"] = TableModel.get_by_type(req_data["TableType"])
        #del req_data["TableType"]
        loaded_data = rest_table_schema.load(req_data, partial=True)
        rest_tab_obj = RestTableMapModel(loaded_data)
        rest_tab_obj = rest_tab_obj.create_mapping()
        dumped_data = rest_table_schema.dump(rest_tab_obj)
        return {"message": "CREATED", "Restaurant": dumped_data}, 200



class Show_Tables(Resource):
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def get(self,restaurant_name):
        """
        Step4: Shows the type and count of table available with respect to the input restaurant name
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
    @restaurant_namespace.doc(security='apikey',
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    @jwt_required
    def post(self):
        """
        Step5: Book the table needed and the count of availabe restaurant reduces by 1, if the count of table is 0,
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
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def get(self):
        """
        Step6: Gives overall order history of a particular user"""
        userId = get_jwt_identity()
        booking_obj = Bookings.get_booking_by_userId(userId=userId)
        dumped_data = book_schema.dump(booking_obj, many=True)
        return {"message":"Retrieved","Orders":dumped_data},200


class Bill(Resource):
    @restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def get(self):
        """
        Step7: Gives the bill amount of unpaid bookings together
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
    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def get(self,bookingId):
        """
        Step8: Checking in of the booked order with respect to the input booking Id provided.
        :param bookingId:
        """
        Bookings.change_status(bookingId,"CHECKEDIN")
        booking_obj = Bookings.get_booking_by_id(bookingId)
        dumped_data = book_schema.dump(booking_obj)
        return {"message":"CHECKEDIN","booking":dumped_data}


class CancelBooking(Resource):
    restaurant_namespace.doc(
        responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY', 500: 'SERVER_ERROR'})

    @restaurant_namespace.doc(security='apikey',
                              responses={404: 'NOT FOUND', 412: 'INVALID INPUT', 424: 'FAILED DEPENDENCY',
                                         500: 'SERVER_ERROR'})
    @jwt_required
    def post(self,bookingId):
        """
        Step9: Cancel a booking which is booked priorly with respect to the input Booking Id provided
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





