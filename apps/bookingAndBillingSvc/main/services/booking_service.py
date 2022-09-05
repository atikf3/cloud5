from bson.objectid import ObjectId

from main.db import MongoDB


class BookingService:
    """ doc string for BookingService """

    def __init__(self):
        super(BookingService, self).__init__()
        self.collection = "bookings"
        self.mongo = MongoDB()

    def add(self, booking_obj):
        return (
            self.mongo.save(self.collection, booking_obj),
            "Successfully added.",
            200,
        )

    def bookings_list(self):
        return self.mongo.find(self.collection)

    def delete_booking(self, booking_id, user_id):
        # TODO: add UID Check,
        return self.mongo.delete(self.collection, booking_id)

    def update_booking(self, booking_id, booking_obj, user_id):
        condition = {"$set": booking_obj}
        # TODO: add UID Check,
        res, update_count = self.mongo.update(self.collection, booking_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_booking(self, booking_id):
        condition = {"_id": ObjectId(booking_id)}
        return self.mongo.find(self.collection, condition)
