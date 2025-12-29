# python
import json
import sqlite3
import os
import tempfile
from pathlib import Path

# from src.services.fund import calculate_refund

project_root = Path(__file__).resolve().parents[2]
DB_PATH = os.environ.get("DB_PATH") or os.path.join(project_root, "badminton.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# def lambda_handler(event, context):
#     action = event.get("action")
#
#     with sqlite3.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
#
#         if action == "list_members":
#             cursor.execute("SELECT * FROM members")
#             members = cursor.fetchall()
#             return {"members": members}
#
#         elif action == "list_reservations":
#             cursor.execute("SELECT * FROM reservations")
#             reservations = cursor.fetchall()
#             return {"reservations": reservations}
#
#         elif action == "unjoin":
#             member_id = event["member_id"]
#             reservation_id = event["reservation_id"]
#
#             # Count dropouts
#             cursor.execute(
#                 "SELECT COUNT(*) FROM attendance WHERE reservation_id=? AND joined=0",
#                 (reservation_id,),
#             )
#             num_dropouts = cursor.fetchone()[0] + 1  # include current dropout
#
#             # Get member gender
#             cursor.execute("SELECT gender FROM members WHERE id=?", (member_id,))
#             row = cursor.fetchone()
#             gender = row[0] if row else None
#
#             refund = calculate_refund(num_dropouts, gender)
#
#             # Update attendance
#             cursor.execute(
#                 "UPDATE attendance SET joined=0, refund_amount=? WHERE member_id=? AND reservation_id=?",
#                 (refund, member_id, reservation_id),
#             )
#             conn.commit()
#
#             return {"refund": refund}
#
#         elif action == "monthly_refund":
#             member_id = event["member_id"]
#             cursor.execute(
#                 "SELECT SUM(refund_amount) FROM attendance WHERE member_id=?", (member_id,)
#             )
#             total_refund = cursor.fetchone()[0] or 0
#             return {"member_id": member_id, "total_refund": total_refund}
#
#         elif action == "update_refund_status":
#             member_id = event["member_id"]
#             status = event["status"]
#             cursor.execute("UPDATE refunds SET status=? WHERE member_id=?", (status, member_id))
#             conn.commit()
#             return {"status": status}
#
#     return {"message": "Action completed"}
#
# import json
# import sqlite3
# import os
#
# DB_PATH = "/tmp/badminton.db"


# Refund formula
def calculate_refund(num_dropouts, gender):
    if num_dropouts == 0:
        return 0
    elif num_dropouts == 1:
        return 30 if gender == "female" else 40
    elif num_dropouts == 2:
        return 20 if gender == "female" else 30
    elif num_dropouts == 3:
        return 10 if gender == "female" else 20
    else:
        return 0


# Monthly fee calculation based on reservations count
def calculate_monthly_fee(gender, reservations_count):
    if gender == "female":
        return 50 * reservations_count
    elif gender == "male":
        return 60 * reservations_count


def lambda_handler(event, context):
    action = event.get("action")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if action == "list_members":
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        return {"members": members}

    elif action == "list_reservations":
        cursor.execute("SELECT * FROM reservations")
        reservations = cursor.fetchall()
        return {"reservations": reservations}

    elif action == "unjoin":
        member_id = event["member_id"]
        reservation_id = event["reservation_id"]

        # Count current dropouts for this reservation
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE reservation_id=? AND joined=0",
            (reservation_id,),
        )
        num_dropouts = cursor.fetchone()[0] + 1  # include this dropout

        # Get member gender
        cursor.execute("SELECT gender FROM members WHERE id=?", (member_id,))
        gender = cursor.fetchone()[0]

        refund = calculate_refund(num_dropouts, gender)

        # Update attendance
        cursor.execute(
            "UPDATE attendance SET joined=0, refund_amount=? WHERE member_id=? AND reservation_id=?",
            (refund, member_id, reservation_id),
        )
        conn.commit()

        return {"refund": refund}

    elif action == "monthly_fee":
        member_id = event["member_id"]
        month = event["month"]  # format 'YYYY-MM'

        # Count reservations in that month
        cursor.execute(
            "SELECT COUNT(*) FROM reservations WHERE strftime('%Y-%m', date)=?",
            (month,),
        )
        reservations_count = cursor.fetchone()[0]

        # Get member gender
        cursor.execute("SELECT gender FROM members WHERE id=?", (member_id,))
        gender = cursor.fetchone()[0]

        fee = calculate_monthly_fee(gender, reservations_count)
        return {"member_id": member_id, "month": month, "fee": fee}

    elif action == "monthly_refund":
        member_id = event["member_id"]
        month = event["month"]

        cursor.execute(
            """
            SELECT SUM(refund_amount) 
            FROM attendance a
            JOIN reservations r ON a.reservation_id = r.id
            WHERE a.member_id=? AND strftime('%Y-%m', r.date)=?
        """,
            (member_id, month),
        )
        total_refund = cursor.fetchone()[0] or 0

        return {"member_id": member_id, "month": month, "total_refund": total_refund}

    elif action == "update_refund_status":
        member_id = event["member_id"]
        month = event["month"]
        status = event["status"]

        cursor.execute(
            "UPDATE refunds SET status=? WHERE member_id=? AND month=?",
            (status, member_id, month),
        )
        conn.commit()
        return {"status": status}

    conn.close()
    return {"message": "Action completed"}


if __name__ == "__main__":
    # For local testing: ensure stdout uses UTF-8 and pretty-print Unicode (Vietnamese)
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # test_event = {"action": "list_members"}
    # test_event = {"action": "list_reservations"}
    # test_event = {"action": "unjoin", "member_id": 2, "reservation_id": 1}
    # test_event = {"action": "monthly_refund", "member_id": 2, "month": "2024-06"}
    test_event = {"action": "update_refund_status", "member_id": 2, "status": "sent", "month": "2024-06"}
    result = lambda_handler(test_event, None)
    body = json.dumps(result, indent=4, ensure_ascii=False)
    print(body)
