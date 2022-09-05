from bson.objectid import ObjectId

from main.db import MongoDB


class MailerService:
    """ doc string for MailerService """

    def __init__(self):
        super(MailerService, self).__init__()
        self.collection = "orders"
        self.mongo = MongoDB()

    def add(self, order_obj):
        return (
            self.mongo.save(self.collection, order_obj),
            "Successfully added.",
            200,
        )

    def orders_list(self):
        return self.mongo.find(self.collection)

    def delete_order(self, order_id, user_id):
        # TODO: add UID Check,
        return self.mongo.delete(self.collection, order_id)

    def update_order(self, order_id, order_obj, user_id):
        condition = {"$set": order_obj}
        # TODO: add UID Check,
        res, update_count = self.mongo.update(self.collection, order_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_order(self, order_id):
        condition = {"_id": ObjectId(order_id)}
        return self.mongo.find(self.collection, condition)
