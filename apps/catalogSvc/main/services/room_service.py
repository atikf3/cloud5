from bson.objectid import ObjectId

from main.db import MongoDB


class RoomService:
    """ doc string for RoomService """

    def __init__(self):
        super(RoomService, self).__init__()
        self.collection = "rooms"
        self.mongo = MongoDB()

    def add(self, room_obj):
        return (
            self.mongo.save(self.collection, room_obj),
            "Successfully added.",
            200,
        )

    def rooms_list(self):
        return self.mongo.find(self.collection)

    def delete_room(self, room_id):
        # TODO: add UID Check,
        return self.mongo.delete(self.collection, room_id)

    def update_room(self, room_id, room_obj):
        condition = {"$set": room_obj}
        # TODO: add UID Check,
        res, update_count = self.mongo.update(self.collection, room_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_room(self, room_id):
        condition = {"_id": ObjectId(room_id)}
        return self.mongo.find(self.collection, condition)
