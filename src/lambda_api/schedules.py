import json

from src.api_logic import schedules
from src.common.api_utils import exception_handler
from src.settings import logger


@exception_handler
def lambda_handler(event, context):

    get_paths = {
        "/api/schedules": schedules.get_schedules,
        "/api/schedules/{schedule_id}": schedules.get_schedule,
    }
    post_paths = {
        "/api/schedules": schedules.create_schedule,
    }
    patch_paths = {
        "/api/attendances/{attendance_id}": schedules.patch_attendance,
    }
    delete_paths = {
        "/api/schedules/{schedule_id}": schedules.delete_schedule,
    }

    path = event.get("path", "")
    logger.info(f"Path: {path}")
    method = event.get("httpMethod", "GET")
    body = json.loads(event.get("body", "{}") or "{}")
    if method == "GET":
        paths = get_paths
    elif method == "POST":
        paths = post_paths
    elif method == "PATCH":
        paths = patch_paths
    elif method == "DELETE":
        paths = delete_paths
    else:
        raise Exception("Method Not Allowed")
    if path in paths:
        function_name = paths[path]
        result = function_name(**body)
    else:
        raise Exception("Not found")
    return result


if __name__ == "__main__":
    event = {
        "body": json.dumps(
            {
                "players": ["Đạt", "Thảo", "Văn", "Huy", "Vu", "Thinh"],
                "numberOfPlayers": 6,
                "rentalCost": 200,
                "shuttleAmount": 3,
                "shuttlePrice": 26,
            }
        ),
        "path": "/api/players",
        "httpMethod": "GET",
    }
    response = lambda_handler(event, None)
    body = response["body"]
    body_json = json.loads(body)
    print(json.dumps(body_json, indent=4, ensure_ascii=False))
