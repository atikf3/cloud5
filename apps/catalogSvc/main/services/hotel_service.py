from bson.objectid import ObjectId

from main.db import MongoDB


class HotelService:
    """ doc string for HotelService """

    def __init__(self):
        super(HotelService, self).__init__()
        self.collection = "hotels"
        self.mongo = MongoDB()

    def add(self, hotel_obj):
        hotel = self.mongo.find(self.collection, {"hotel_name": hotel_obj["hotel_name"]})
        if not hotel:
            return (
                self.mongo.save(self.collection, hotel_obj),
                "Successfully added.",
                200,
            )
        else:
            return ("ok", "Hotel already added to the inventory.", 400)

    def hotels_list(self):
        return self.mongo.find(self.collection)

    def delete_property(self, hotel_id, user_id):
        # TODO: add UID Check,
        return self.mongo.delete(self.collection, hotel_id)

    def update_property(self, hotel_id, hotel_obj, user_id):
        condition = {"$set": hotel_obj}
        # TODO: add UID Check,
        res, update_count = self.mongo.update(self.collection, hotel_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_property(self, hotel_id):
        condition = {"_id": ObjectId(hotel_id)}
        return self.mongo.find(self.collection, condition)
