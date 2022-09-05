from flask import current_app as app
import requests
import json

class Utils:
    def __init__(self):
        pass

    def http_status(self, code):
        return "success" if code == 200 else "error"

    # def get_config(self):
    #     config = yaml.safe_load(open(os.path.join(os.getcwd(), "main/database.yml")))
    #     return config
    
    def validations(self):
        return True

    def checkEntityKeysInRequest(self, entity, request):
        for key in entity.keys():
            checkField = key not in request.json or request.json[key] == ""
            if checkField and entity[key].required == True:
                app.logger.error(f'required key [{key}] should not be empty.')
                # return api.abort(400, f'required key [{addressKey}] should not be empty.', status="error", status_code=400)
                return False
            elif checkField and entity[key].required == False:
                app.logger.warning("Missing optional field: {}".format(key))
        return True

    def post_json(self, url, data):
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.json()