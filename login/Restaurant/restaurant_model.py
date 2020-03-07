from login import db, ma
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import INCLUDE, fields
from ..Authentication.auth_model import User

class RestaurantModel(db.Model):
    __tablename__ = 'restaurants'

    Id = db.Column(db.Integer,
                   primary_key=True)
    Name = db.Column(db.String(100),
                     nullable=False,
                     unique=True)
    Location = db.Column(db.String(100),
                         primary_key=False,
                         unique=False,
                         nullable=False)
    Contact = db.Column(db.String(13),
                        unique=True,
                        nullable=False)

    def __init__(self,data):
        self.Id = data.get('Id')
        self.Name = data.get('Name')
        self.Location = data.get('Location')
        self.Contact = data.get('Contact')

    def create_restaurant(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_restaurant(self) -> None:
        db.session.remove(self)
        db.session.commit()

    def __repr__(self):
        return '<Restaurant {}>'.format(self.Name)

    @classmethod
    def show_all_restaurants(cls)-> list:
        records = RestaurantModel.query.all()
        print(records)
        return records


class Restaurant_schema(ma.SQLAlchemySchema):
    class Meta:
        model=RestaurantModel
        Unkown= INCLUDE
    Id = ma.auto_field(dump_only= True)
    Name = ma.auto_field()
    Location = ma.auto_field()
    Contact = ma.auto_field()


class TableModel(db.Model):

    __tablename__ = "tabletypes"

    Id = db.Column(db.Integer,
                   primary_key=True)
    TableType = db.Column(db.String(100),
                     nullable=False,
                     unique=True)


class TabelSchema(ma.SQLAlchemySchema):
    class Meta:
        model=TableModel
    Id = ma.auto_field(dump_only= True)
    TableType = ma.auto_field()


class RestTableMapModel(db.Model):

    __tablename__ = "restauranttabletypemapping"

    Id = db.Column(db.Integer,
                   primary_key=True)
    RestaurantId = db.Column(db.Integer(),
                     db.ForeignKey('restaurants.Id'))
    TableTypeId = db.Column(db.Integer(),
                             db.ForeignKey('tabletypes.Id'))
    TableCount = db.Column(db.Integer(),
                           nullable=False,
                           unique=False)
    BookingCharges = db.Column(db.Integer(), nullable=False, unique=False)

    def __init__(self,data):
        self.Id = data.get("Id")
        self.RestaurantId = data.get("RestaurantId")
        self.TableTypeId = data.get("TableTypeId")
        self.BookingCharges= data.get("BookingCharges")

    def update_table_count(self):
        self.TableCount -= 1
        db.session.commit()

    @classmethod
    def book_table(cls,data,userId):
        """data = {"Name":"",
                "TableType":""}"""
        result = db.session.query(RestaurantModel.Name,
                                   RestaurantModel.Location,
                                   RestaurantModel.Contact,
                                   TableModel.TableType,
                                   RestTableMapModel.TableCount,
                                   RestTableMapModel.BookingCharges,
                                   RestTableMapModel.Id). \
            join(RestTableMapModel, RestaurantModel.Id == RestTableMapModel.RestaurantId). \
            join(TableModel, TableModel.Id == RestTableMapModel.TableTypeId). \
            filter(RestaurantModel.Name == data["Name"]).\
            filter(TableModel.TableType==int(data["TableType"])).first()

        record ={"Name": getattr(result, "Name"),
                        "Location": getattr(result, "Location"),
                        "Contact": getattr(result, "Contact"),
                        "TableType": getattr(result, "TableType") + "seater",
                        "BookingCharges": getattr(result, "BookingCharges"),
                        }

        if result.TableCount<=0:
            return None

        map_obj = RestTableMapModel.query.filter(RestTableMapModel.Id==result.Id).first()
        map_obj.update_table_count()
        bill = Bookings(MapId=map_obj.Id, UserId=userId)
        bill.create_booking()
        return record


    @classmethod
    def show_table(cls, restaurantName)->list:

        results = db.session.query(RestaurantModel.Name,
                                  RestaurantModel.Location,
                                  RestaurantModel.Contact,
                                  TableModel.TableType,
                                  RestTableMapModel.TableCount,
                                   RestTableMapModel.BookingCharges).\
            join(RestTableMapModel,RestaurantModel.Id==RestTableMapModel.RestaurantId).\
            join(TableModel, TableModel.Id==RestTableMapModel.TableTypeId).\
            filter(RestaurantModel.Name==restaurantName).all()

        records = list()
        for result in results:
            records.append({"Name":getattr(result,"Name"),
                            "Location": getattr(result,"Location"),
                            "Contact":getattr(result,"Contact"),
                            "TableType":getattr(result,"TableType")+"seater",
                            "TableCount":getattr(result,"TableCount"),
                            "BookingCharges":getattr(result, "BookingCharges")})
        return records


class RestTableMapSchema(ma.SQLAlchemySchema):
    class Meta:
        model=RestTableMapModel
    Id = ma.auto_field(dump_only= True)
    RestaurantId = ma.auto_field()
    TableTypeId = ma.auto_field()
    TableCount = ma.auto_field()
    BookingCharges = ma.auto_field()


class Bookings(db.Model):
    __tablename__ = "bookings"

    Id = db.Column(db.Integer,
                   primary_key=True,autoincrement=True)
    MapId = db.Column(db.Integer())
    UserId = db.Column(db.Integer())
    PaymentStatus = db.Column(db.Enum('PAID', 'NOTPAID'))
    BookingStatus = db.Column(db.Enum('BOOKED','CHECKEDIN','CANCELLED'))

    def __init__(self, MapId, UserId, paymentStatus="NOTPAID", bookingStatus="BOOKED"):
        self.MapId = MapId
        self.UserId = UserId
        self.PaymentStatus = paymentStatus
        self.BookingStatus = bookingStatus

    def create_booking(self)->None:
        """self.Id = mapped_obj.Id
        self.MapId = mapped_obj.MapId
        self.UserId = userId
        self.PaymentStatus = mapped_obj.PaymentStatus
        self.BookingStatus = mapped_obj.BookingStatus"""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_booking_by_userId(cls, userId)->list:

        results = db.session.query(RestaurantModel.Name,
                                  RestaurantModel.Location,
                                  RestaurantModel.Contact,
                                  TableModel.TableType,
                                  RestTableMapModel.TableCount,
                                   RestTableMapModel.BookingCharges,
                                   Bookings.BookingStatus,
                                   Bookings.PaymentStatus,
                                   Bookings.Id).\
            join(RestTableMapModel,RestaurantModel.Id==RestTableMapModel.RestaurantId).\
            join(TableModel, TableModel.Id==RestTableMapModel.TableTypeId).join(cls,Bookings.MapId==RestTableMapModel.Id).\
            filter(cls.UserId==userId).all()

        return results

    @classmethod
    def unpaid_booking(cls,userId)->list:
        results = db.session.query(RestaurantModel.Name,
                                   RestaurantModel.Location,
                                   RestaurantModel.Contact,
                                   TableModel.TableType,
                                   RestTableMapModel.TableCount,
                                   RestTableMapModel.BookingCharges,
                                   Bookings.BookingStatus,
                                   Bookings.PaymentStatus,
                                   Bookings.Id). \
            join(RestTableMapModel, RestaurantModel.Id == RestTableMapModel.RestaurantId). \
            join(TableModel, TableModel.Id == RestTableMapModel.TableTypeId).join(cls,
                                                                                  Bookings.MapId == RestTableMapModel.Id). \
            filter(cls.UserId == userId).filter(cls.PaymentStatus=="NOTPAID").filter(cls.BookingStatus!="CANCELLED").all()

        return results

    @classmethod
    def change_status(cls,bookingId,status)->bool:
        booking_obj = Bookings.query.get(bookingId)
        if booking_obj:
            booking_obj.BookingStatus = status
            db.session.commit()
            return True
        else:
            return False


    @classmethod
    def get_booking_by_id(cls,bookingId:int)->"Bookings":
        booking_obj = Bookings.query.get(bookingId)
        print(booking_obj)
        return booking_obj

    @classmethod
    def get_booking_status(cls,bookingId:int)->str:
        booking_obj = Bookings.query.filter(Bookings.Id==bookingId).one()
        return booking_obj.BookingStatus


class Booking_schema(ma.SQLAlchemySchema):
    class Meta:
        model=Bookings
        unknown=INCLUDE

    Id = ma.auto_field(dump_only=True)
    MapId = ma.auto_field()
    UserId = ma.auto_field()
    PaymentStatus = ma.auto_field(default="NOTPAID")
    BookingStatus = ma.auto_field(default="BOOKED")
    BookingCharges = fields.String()
    Location = fields.String()
    Name = fields.String()
    TableType = fields.String()



