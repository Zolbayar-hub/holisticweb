from flask import Blueprint, render_template, request, jsonify
from db import db
from db.models import Booking
from datetime import datetime

booking_bp = Blueprint("booking_bp", __name__, url_prefix="/booking")

# 📅 Calendar page
@booking_bp.route("/")
def booking_page():
    return render_template("booking.html")

# 📅 API: Get all bookings (for FullCalendar)
@booking_bp.route("/events")
def booking_events():
    bookings = Booking.query.all()
    events = [
        {
            "id": b.id,
            "title": f"{b.user_name} ({b.status})",  # Show name + status
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
        }
        for b in bookings
    ]
    return jsonify(events)

# 📅 API: Add new booking
@booking_bp.route("/events", methods=["POST"])
def add_booking():
    data = request.get_json()
    try:
        booking = Booking(
            user_name=data["user_name"],
            email=data["email"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            status="pending"
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify({"success": True, "id": booking.id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
