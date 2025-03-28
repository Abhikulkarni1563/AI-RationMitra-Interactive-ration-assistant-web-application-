from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import ration_mitraa_chatbot, listen_to_voice, speak_response
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime

import os
from flask_cors import CORS
from models import User, Admin, Commodity, Feedback

from flask_migrate import Migrate
from flask import Flask
from flask_cors import CORS
from extensions import db

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ration_mitraa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

db.init_app(app)

# Only import models AFTER db is initialized
from models import User, Admin, Commodity, Feedback

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    aadhar = db.Column(db.String(12), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)


# -------------------- ROUTES --------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_type'] = 'user'
            return redirect(url_for("user_dashboard"))
        else:
            flash("❌ Invalid user credentials. Please try again.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        age = request.form['age']
        aadhar = request.form['aadhar']
        mobile = request.form['mobile']

        if User.query.filter_by(email=email).first():
            flash("⚠️ User already exists. Please log in.")
            return redirect(url_for("login"))

        new_user = User(name=name, email=email, password=password, age=age, aadhar=aadhar, mobile=mobile)
        db.session.add(new_user)
        db.session.commit()
        flash("🎉 Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form['admin_email']
        password = request.form['admin_password']
        admin = Admin.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['user_type'] = 'admin'
            return redirect(url_for("admin_dashboard"))
        else:
            flash("❌ Invalid admin credentials.")
            return redirect(url_for("admin_login"))

    return render_template("admin.html")

@app.route("/user_dashboard")
def user_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash("Access denied.")
        return redirect(url_for("login"))

    user = User.query.get(session['user_id'])
    return render_template("user_dashboard.html", user_name=user.name)

@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash("Admins only.")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form['commodity_name']
        quantity = request.form['commodity_quantity']
        new_commodity = Commodity(name=name, quantity=quantity)
        db.session.add(new_commodity)
        db.session.commit()
        flash("✅ Commodity added.")

    users = User.query.all()
    commodities = Commodity.query.all()
    total_users = len(users)
    total_commodities = len(commodities)
    stock_dispensed = "567kg"  # Placeholder
    total_feedbacks = Feedback.query.count()

    return render_template("admin_dashboard.html",
        users=users,
        commodities=commodities,
        total_users=total_users,
        total_commodities=total_commodities,
        stock_dispensed=stock_dispensed,
        total_feedbacks=total_feedbacks
    )

@app.route("/chatbot", methods=["GET"])
def chatbot_ui():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return render_template("chatbot.html")

@app.route("/chatbot", methods=["POST"])
def chatbot_text():
    try:
        data = request.get_json()
        user_input = data.get("message")
        if not user_input:
            return jsonify({"response": "⚠️ Please say or type something."})
        response = ration_mitraa_chatbot(user_input)
        return jsonify({"response": response})
    except Exception as e:
        print("Chatbot text error:", e)
        return jsonify({"response": "⚠️ Oops! Something went wrong."})

@app.route("/chat_voice", methods=["POST"])
def chat_voice():
    user_input = listen_to_voice()
    if not user_input:
        return jsonify({"response": "⚠️ Could not understand voice.", "audio": None})

    ai_reply = ration_mitraa_chatbot(user_input)
    audio_path = speak_response(ai_reply)

    return jsonify({"response": ai_reply, "audio": audio_path})

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/about-us")
def about_us():
    return render_template("aboutus.html")

@app.route("/updates")
def updates():
    return render_template("govtschemes.html")
@app.route("/api/govtschemes")
def get_govt_schemes():
    state = request.args.get('state')
    district = request.args.get('district')

    dummy_data = [
        {
            "fps_name": "Chamundi Ration Depot",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100101",
            "lattitude": "12.2958",
            "lagnitude": "76.6394",
            "remark": "Digital Payments Available",
            "ration_available": ["Rice", "Wheat", "Sugar"],
            "price_per_kg": {"Rice": 3, "Wheat": 2, "Sugar": 13},
            "category": "Urban"
        },
        {
            "fps_name": "T. Narasipura Gram FPS",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100107",
            "lattitude": "12.2084",
            "lagnitude": "76.8983",
            "remark": "Serves 200+ low-income families",
            "ration_available": ["Rice", "Oil", "Dal"],
            "price_per_kg": {"Rice": 3, "Oil": 24, "Dal": 6},
            "category": "Rural"
        },
        {
            "fps_name": "Bannur Town Sahakari Store",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100108",
            "lattitude": "12.3327",
            "lagnitude": "76.8626",
            "remark": "Digitally Enabled + Women-Led",
            "ration_available": ["Wheat", "Dal", "Sugar"],
            "price_per_kg": {"Wheat": 2, "Dal": 6, "Sugar": 13},
            "category": "Semi-Urban"
        },
        {
            "fps_name": "Hunsur Janatha Ration Point",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100109",
            "lattitude": "12.3085",
            "lagnitude": "76.2892",
            "remark": "Ration Van visits remote areas weekly",
            "ration_available": ["Rice", "Salt", "Oil"],
            "price_per_kg": {"Rice": 3, "Salt": 2, "Oil": 25},
            "category": "Rural"
        },
        {
            "fps_name": "H.D. Kote Tribal Supply Store",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100110",
            "lattitude": "11.9852",
            "lagnitude": "76.3566",
            "remark": "Tribal support focused — outreach van supported",
            "ration_available": ["Rice", "Wheat", "Salt", "Oil"],
            "price_per_kg": {"Rice": 3, "Wheat": 2, "Salt": 2, "Oil": 25},
            "category": "Rural"
        },
        {
            "fps_name": "Periyapatna Farmers Coop Ration",
            "districtname": "MYSORE",
            "statename": "KARNATAKA",
            "fps_id": "291733100111",
            "lattitude": "12.3351",
            "lagnitude": "76.0981",
            "remark": "Serves farming families + digital billing",
            "ration_available": ["Rice", "Dal", "Oil"],
            "price_per_kg": {"Rice": 3, "Dal": 6, "Oil": 25},
            "category": "Semi-Urban"
        }
    ]

    # Optional filtering
    if state:
        dummy_data = [d for d in dummy_data if d["statename"].lower() == state.lower()]
    if district:
        dummy_data = [d for d in dummy_data if d["districtname"].lower() == district.lower()]

    return jsonify(dummy_data)

@app.route('/schemes')
def show_schemes():
    latest_schemes = [
        {
            "title": "New Ration Card Rules 2025",
            "description": "Major policy overhaul targeting efficient subsidy distribution and removal of ineligible cardholders.",
            "eligibility": "BPL/APL/Antyodaya card holders with income verification.",
            "link": "https://pib.gov.in/PressReleasePage.aspx?PRID=NEW_RULES_2025",
            "launch_date": "2025-01-01"
        },
        {
            "title": "Smart Ration Card Initiative",
            "description": "Smart cards embedded with chips to digitize ration distribution and reduce fraud.",
            "eligibility": "All NFSA beneficiaries eligible to upgrade to smart cards.",
            "link": "https://www.india.gov.in/smart-ration-card",
            "launch_date": "2024-12-15"
        },
        {
            "title": "PMGKAY Extension till 2029",
            "description": "Free food grains under PMGKAY for next five years to 81.35 crore beneficiaries.",
            "eligibility": "All NFSA beneficiaries.",
            "link": "https://pib.gov.in/PressReleasePage.aspx?PRID=PMGKAY_EXTENSION",
            "launch_date": "2024-01-01"
        },
        {
            "title": "e-Ration Mobile App Launch",
            "description": "New mobile app to track ration entitlement and transactions in real time.",
            "eligibility": "All registered ration card holders.",
            "link": "https://nfsa.gov.in/e-ration-app",
            "launch_date": "2023-11-20"
        },
        {
            "title": "Direct Benefit Transfer for Food Subsidy",
            "description": "Cash subsidies directly transferred into beneficiary accounts instead of grain distribution.",
            "eligibility": "Pilot districts and willing beneficiaries.",
            "link": "https://www.dbtbharat.gov.in/foodsubsidy",
            "launch_date": "2023-08-01"
        },
        {
            "title": "Digitization of FPS (Fair Price Shops)",
            "description": "Government mandates GPS-enabled POS machines in all FPS for tracking distribution.",
            "eligibility": "All licensed Fair Price Shop owners.",
            "link": "https://www.pdsportal.nic.in/FPSdigitization",
            "launch_date": "2023-06-15"
        },
        {
            "title": "Grievance Redressal Portal for Ration Services",
            "description": "24x7 complaint and feedback portal for ration-related services.",
            "eligibility": "Open to all citizens.",
            "link": "https://www.rationgrievance.gov.in",
            "launch_date": "2023-04-10"
        },
        {
            "title": "Wheat & Rice Fortification Expansion",
            "description": "Government expands fortified foodgrain supply across all PDS outlets.",
            "eligibility": "NFSA ration beneficiaries.",
            "link": "https://www.ffrc.fssai.gov.in",
            "launch_date": "2023-02-20"
        },
        {
            "title": "One Nation One Ration Card (ONORC) Scheme",
            "description": "Interoperable ration access from any state across India.",
            "eligibility": "NFSA ration card holders.",
            "link": "https://www.myscheme.gov.in/schemes/onorc",
            "launch_date": "2018-06-01"
        },
        {
            "title": "Antyodaya Anna Yojana (AAY) Upgrade",
            "description": "Enhanced monthly quota and nutritional grains for AAY households.",
            "eligibility": "Poorest families listed under AAY.",
            "link": "https://nfsa.gov.in/AAY-upgrade",
            "launch_date": "2022-10-01"
        },
        {
            "title": "Women-Led FPS Incentive Program",
            "description": "Special incentives for women-led ration outlets to encourage gender inclusion.",
            "eligibility": "Registered FPS owned or operated by women.",
            "link": "https://wfp.gov.in/women-fps",
            "launch_date": "2022-07-01"
        },
        {
            "title": "Ration at Doorstep Scheme",
            "description": "Pilot delivery system initiated to deliver grains to rural doorstep beneficiaries.",
            "eligibility": "Remote rural areas with limited FPS access.",
            "link": "https://ruralration.gov.in",
            "launch_date": "2022-04-15"
        },
        {
            "title": "Nutritional Security Scheme for Pregnant Women",
            "description": "Special ration kits with iron and protein-rich grains.",
            "eligibility": "Pregnant women under Janani Suraksha Yojana.",
            "link": "https://www.mohfw.gov.in/nutritionkits",
            "launch_date": "2021-12-01"
        },
        {
            "title": "Urban Slum Ration Card Outreach",
            "description": "Mass drive to register and issue ration cards to urban slum dwellers.",
            "eligibility": "Low-income urban slum households.",
            "link": "https://urbanpds.gov.in/slumcards",
            "launch_date": "2021-09-15"
        },
        {
            "title": "Green PDS Campaign",
            "description": "Initiative to promote biodegradable packaging in PDS distribution.",
            "eligibility": "All PDS shops encouraged to adopt.",
            "link": "https://greenpds.gov.in",
            "launch_date": "2020-10-10"
        }
    ]

    # Sort by most recent launch_date descending
    latest_schemes.sort(key=lambda x: datetime.datetime.strptime(x["launch_date"], "%Y-%m-%d"), reverse=True)
    return render_template('schemes.html', schemes=latest_schemes)


messages = []

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save message
        messages.append({'name': name, 'email': email, 'message': message, 'timestamp': timestamp})
        return redirect('/contactus')  # Redirect after submission

    return render_template('contactus.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html', messages=messages)

from flask import request, redirect, render_template, flash
from models import db, Feedback  # assuming you’ve imported Feedback model

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        rating = request.form.get('rating')

        print(f"Name: {name}, Rating: {rating}, Message: {message}")

        if not (name and message and rating):
            flash('All fields are required.', 'error')
            return redirect('/feedback')

        if not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash('Rating must be a number between 1 and 5.', 'error')
            return redirect('/feedback')

        # Save feedback to DB
        fb = Feedback(username=name, message=message, rating=int(rating))
        db.session.add(fb)
        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect('/feedback')

    return render_template('feedback.html')


from models import Feedback  # Make sure this import exists

@app.route("/admin/feedback")
def admin_feedback():
    if 'admin_id' not in session:
        flash("⚠️ Admin login required.")
        return redirect(url_for("admin_login"))

    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template("userfeedback.html", feedbacks=feedbacks, current_year=datetime.now().year)





@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))

# -------------------- MAIN --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(email='admin@rationmitra.in').first():
            default_admin = Admin(email='admin@rationmitra.in', password=generate_password_hash("admin1234"))
            db.session.add(default_admin)
            db.session.commit()
            print("✅ Default admin created.")
        else:
            print("ℹ️ Admin already exists.")

    app.run(debug=True)
