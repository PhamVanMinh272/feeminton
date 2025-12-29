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


def calculate_monthly_fee(member_gender, reservations_count):
    if member_gender == "female":
        return 50 * reservations_count
    elif member_gender == "male":
        return 60 * reservations_count


def get_member_monthly_fee(member_id, month):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count reservations in that month
    cursor.execute(
        "SELECT COUNT(*) FROM reservations WHERE strftime('%Y-%m', date)=?", (month,)
    )
    reservations_count = cursor.fetchone()[0]

    # Get member gender
    cursor.execute("SELECT gender FROM members WHERE id=?", (member_id,))
    gender = cursor.fetchone()[0]

    fee = calculate_monthly_fee(gender, reservations_count)
    conn.close()
    return fee
