from bson.objectid import ObjectId

from main.db import MongoDB


class BillingService:
    """ doc string for BillService """

    def __init__(self):
        super(BillingService, self).__init__()
        self.collection = "bill"
        self.mongo = MongoDB()

    def add(self, address_obj):
        address = self.mongo.find(self.collection, {"client_secret": address_obj["client_secret"]})
        if not address:
            return (
                self.mongo.save(self.collection, address_obj),
                "Successfully added.",
                200,
            )
        else:
            return ("ok", "Payment error, please retry with another session and secret (client_secret).", 400)

    def bill_list(self):
        return self.mongo.find(self.collection)

    def delete_address(self, address_id, user_id):
        # TODO: add UID Check,
        return self.mongo.delete(self.collection, address_id)

    def update_address(self, address_id, address_obj, user_id):
        condition = {"$set": address_obj}
        # TODO: add UID Check,
        res, update_count = self.mongo.update(self.collection, address_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_address(self, address_id):
        condition = {"_id": ObjectId(address_id)}
        return self.mongo.find(self.collection, condition)
