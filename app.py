from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import time
import os

from parking.vehicle import Car, Bike
from parking.floor import ParkingFloor
from parking.parking_lot import ParkingLot

app = Flask(__name__)
# Use a cloud database URL if provided, otherwise fall back to local SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///parking_v2.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super-secret-key-change-me"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    car_rate = db.Column(db.Integer, default=40)
    bike_rate = db.Column(db.Integer, default=20)
    # Relationships
    floors = db.relationship("FloorConfig", backref="admin", lazy=True, cascade="all, delete-orphan")
    tickets = db.relationship("TicketRecord", backref="admin", lazy=True, cascade="all, delete-orphan")
    meta = db.relationship("SystemMeta", backref="admin", uselist=False, cascade="all, delete-orphan")


class FloorConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), nullable=False)
    floor_no = db.Column(db.Integer, nullable=False)
    # Configuration for specific vehicle types
    slots = db.relationship("SlotConfig", backref="floor", lazy=True, cascade="all, delete-orphan")


class SlotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor_id = db.Column(db.Integer, db.ForeignKey("floor_config.id"), nullable=False)
    vehicle_type = db.Column(db.String(16), nullable=False)  # CAR, BIKE
    count = db.Column(db.Integer, nullable=False)


class TicketRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), nullable=False)
    vehicle_number = db.Column(db.String(64), nullable=False, index=True)
    vehicle_type = db.Column(db.String(16), nullable=False)
    floor_no = db.Column(db.Integer, nullable=False)
    slot_id = db.Column(db.String(16), nullable=False)
    entry_time = db.Column(db.Float, nullable=False)
    exit_time = db.Column(db.Float)
    fee = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True, index=True)


class SystemMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), nullable=False)
    last_reset_time = db.Column(db.Float)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# Multi-admin parking lot instances
admin_parking_lots = {}


def build_dynamic_parking_lot(admin_id):
    admin = Admin.query.get(admin_id)
    if not admin or not admin.floors:
        return None

    floors_list = []
    for floor_cfg in admin.floors:
        slots_dict = {
            slot_cfg.vehicle_type: slot_cfg.count for slot_cfg in floor_cfg.slots
        }
        floors_list.append(ParkingFloor(floor_cfg.floor_no, slots_dict))

    if not floors_list:
        return None

    return ParkingLot(floors_list)


def get_or_create_system_meta(admin_id):
    meta = SystemMeta.query.filter_by(admin_id=admin_id).first()
    if not meta:
        meta = SystemMeta(admin_id=admin_id, last_reset_time=None)
        db.session.add(meta)
        db.session.commit()
    return meta


def get_parking_lot(admin_id):
    if admin_id not in admin_parking_lots:
        load_admin_state(admin_id)
    return admin_parking_lots.get(admin_id)


def load_admin_state(admin_id):
    """
    Initialize parking_lot for a specific admin from their config and active tickets.
    """
    global admin_parking_lots

    parking_lot = build_dynamic_parking_lot(admin_id)
    if not parking_lot:
        admin_parking_lots[admin_id] = None
        return

    # Ensure metadata row exists
    get_or_create_system_meta(admin_id)

    active_records = TicketRecord.query.filter_by(admin_id=admin_id, is_active=True).all()
    for record in active_records:
        if record.vehicle_type == "CAR":
            vehicle = Car(record.vehicle_number)
        else:
            vehicle = Bike(record.vehicle_number)

        slot = parking_lot.find_slot(record.floor_no, record.slot_id)
        if not slot:
            continue

        slot.park(vehicle)
        ticket = parking_lot.active_tickets.get(vehicle.number)
        if ticket:
            continue

        from parking.ticket import ParkingTicket

        restored_ticket = ParkingTicket(
            vehicle, record.floor_no, slot, entry_time=record.entry_time
        )
        parking_lot.active_tickets[vehicle.number] = restored_ticket

    admin_parking_lots[admin_id] = parking_lot


with app.app_context():
    db.create_all()


@app.template_filter("datetimeformat")
def datetimeformat_filter(value):
    if not value:
        return "-"
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
    except (TypeError, ValueError):
        return "-"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin_exists = Admin.query.filter_by(username=username).first()
        if admin_exists:
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))

        new_admin = Admin(
            username=username,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
        )
        db.session.add(new_admin)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for("home"))
        else:
            flash("Login failed. Check your username and password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/manage_floors", methods=["GET", "POST"])
@login_required
def manage_floors():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_rates":
            car_rate = request.form.get("car_rate", type=int)
            bike_rate = request.form.get("bike_rate", type=int)
            if car_rate is not None: current_user.car_rate = car_rate
            if bike_rate is not None: current_user.bike_rate = bike_rate
            db.session.commit()
            flash("Rates updated successfully.", "success")
            return redirect(url_for("manage_floors"))

        floor_no = request.form.get("floor_no", type=int)
        car_slots = request.form.get("car_slots", type=int, default=0)
        bike_slots = request.form.get("bike_slots", type=int, default=0)

        existing_floor = FloorConfig.query.filter_by(admin_id=current_user.id, floor_no=floor_no).first()
        if existing_floor:
            flash(f"Floor {floor_no} already exists.", "warning")
        else:
            new_floor = FloorConfig(admin_id=current_user.id, floor_no=floor_no)
            db.session.add(new_floor)
            db.session.flush()

            if car_slots > 0:
                car_cfg = SlotConfig(floor_id=new_floor.id, vehicle_type="CAR", count=car_slots)
                db.session.add(car_cfg)
            if bike_slots > 0:
                bike_cfg = SlotConfig(floor_id=new_floor.id, vehicle_type="BIKE", count=bike_slots)
                db.session.add(bike_cfg)
            
            db.session.commit()
            load_admin_state(current_user.id)
            flash(f"Floor {floor_no} added successfully.", "success")

    return render_template("manage_floors.html", floors=current_user.floors)


@app.route("/delete_floor/<int:floor_id>", methods=["POST"])
@login_required
def delete_floor(floor_id):
    floor = FloorConfig.query.get_or_404(floor_id)
    if floor.admin_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("manage_floors"))
    
    db.session.delete(floor)
    db.session.commit()
    load_admin_state(current_user.id)
    flash("Floor deleted.", "info")
    return redirect(url_for("manage_floors"))


@app.route("/park", methods=["GET", "POST"])
@login_required
def park():
    parking_lot = get_parking_lot(current_user.id)
    if not parking_lot:
        flash("Please configure floors first.", "warning")
        return redirect(url_for("manage_floors"))

    if request.method == "POST":
        number = request.form["vehicle_number"]
        vehicle_type = request.form["vehicle_type"]

        if vehicle_type == "CAR":
            vehicle = Car(number)
        else:
            vehicle = Bike(number)

        ticket = parking_lot.park_vehicle(vehicle)

        if ticket:
            record = TicketRecord(
                admin_id=current_user.id,
                vehicle_number=vehicle.number,
                vehicle_type=vehicle.get_type(),
                floor_no=ticket.floor_no,
                slot_id=ticket.slot.slot_id,
                entry_time=ticket.entry_time,
                is_active=True,
            )
            db.session.add(record)
            db.session.commit()
            return render_template("park_result.html", ticket=ticket)

        return render_template("park_result.html", ticket=None, error="Parking is full")

    return render_template("park.html")


@app.route("/exit", methods=["GET", "POST"])
@login_required
def exit_vehicle():
    parking_lot = get_parking_lot(current_user.id)
    if not parking_lot:
        flash("Please configure floors first.", "warning")
        return redirect(url_for("manage_floors"))

    if request.method == "POST":
        number = request.form["vehicle_number"]
        # Custom exit logic to use dynamic rates
        ticket = parking_lot.active_tickets.get(number)
        if ticket:
            # Overwrite vehicle rates with admin rates
            rate = current_user.car_rate if ticket.vehicle.get_type() == "CAR" else current_user.bike_rate
            
            # Manually calculate fee using dynamic rate
            hours_parked = (time.time() - ticket.entry_time) / 3600
            fee = int(max(1, round(hours_parked)) * rate)
            
            # Perform standard exit
            parking_lot.exit_vehicle(number)
        else:
            ticket, fee = None, None

        if ticket:
            record = TicketRecord.query.filter_by(
                admin_id=current_user.id, vehicle_number=number, is_active=True
            ).first()
            if record:
                record.exit_time = time.time()
                record.fee = fee
                record.is_active = False
                db.session.commit()

            duration = ticket.get_human_readable_duration()
            rate_to_show = current_user.car_rate if ticket.vehicle.get_type() == "CAR" else current_user.bike_rate
            return render_template(
                "exit_result.html",
                ticket=ticket,
                fee=fee,
                duration=duration,
                rate_per_hour=rate_to_show,
            )

        return render_template(
            "exit_result.html", ticket=None, fee=None, error="Invalid vehicle number"
        )

    return render_template("exit.html")


@app.route("/")
def home():
    if not current_user.is_authenticated:
        return render_template("landing.html")
    
    parking_lot = get_parking_lot(current_user.id)
    summary = parking_lot.get_occupancy_summary() if parking_lot else None
    return render_template("home.html", summary=summary)


@app.route("/dashboard")
@login_required
def dashboard():
    parking_lot = get_parking_lot(current_user.id)
    summary = parking_lot.get_occupancy_summary() if parking_lot else None
    meta = get_or_create_system_meta(current_user.id)
    last_reset_display = None
    if meta and meta.last_reset_time:
        last_reset_display = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(meta.last_reset_time)
        )
    return render_template(
        "dashboard.html", summary=summary, last_reset_time=last_reset_display
    )


@app.route("/floors")
@login_required
def floors_view():
    parking_lot = get_parking_lot(current_user.id)
    if not parking_lot:
        return redirect(url_for("manage_floors"))
    return render_template("floors.html", floors=parking_lot.floors)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search_vehicle():
    vehicle_number = None
    active_records = []
    history_records = []

    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number", "").strip()
        if vehicle_number:
            active_records = TicketRecord.query.filter_by(
                admin_id=current_user.id, vehicle_number=vehicle_number, is_active=True
            ).all()
            history_records = (
                TicketRecord.query.filter_by(
                    admin_id=current_user.id, vehicle_number=vehicle_number, is_active=False
                )
                .order_by(TicketRecord.entry_time.desc())
                .all()
            )

    return render_template(
        "search.html",
        vehicle_number=vehicle_number,
        active_records=active_records,
        history_records=history_records,
    )



if __name__ == "__main__":
    app.run(debug=True)