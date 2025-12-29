import json

from pydantic import ValidationError

from src.common.exceptions import FileS3NotFound, AlreadyExist, NotFound, InvalidData
from src.settings import logger


def exception_handler(func):
    def wrapper(event, context):
        try:
            data = func(event, context)
            # if isinstance(data, bytes):
            #     return make_bytes_response(data)
            return make_success_response(data)
        except (AlreadyExist, InvalidData) as e:
            logger.exception(e)
            return make_error_response(str(e), 400)
        except NotFound as e:
            logger.exception(e)
            return make_error_response(str(e), 404)
        except FileS3NotFound as e:
            logger.exception(e)
            return make_error_response(str(e), 500)
        except ValidationError as e:
            logger.exception(e)
            json_data = json.loads(e.json())[0]
            msg = json_data["loc"][0] + " " + json_data["msg"]
            return make_error_response(msg, 400)
        except Exception as e:
            logger.exception(e)
            return make_error_response(str(e), 500)

    return wrapper


def make_success_response(body: dict, status_code: int = 200):
    print(
        {
            "statusCode": status_code,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",  ## Allow from anywhere
                "Access-Control-Allow-Methods": "*",  ## Allow only GET request,
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "max-age=3600",
            },
            "body": json.dumps(body, ensure_ascii=False),
        }
    )
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",  ## Allow from anywhere
            "Access-Control-Allow-Methods": "*",  ## Allow only GET request,
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "max-age=3600",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def make_error_response(message: str, status_code: int = 500):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",  ## Allow from anywhere
            "Access-Control-Allow-Methods": "GET",  ## Allow only GET request
        },
        "body": json.dumps({"message": message}),
    }
