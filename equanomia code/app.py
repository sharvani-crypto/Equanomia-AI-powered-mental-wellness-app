"""
Equanomia – AI Powered Mental Wellness Platform
Main Flask Application
"""
 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import hashlib
from datetime import datetime, timedelta
import random
 
app = Flask(__name__)
app.secret_key = "equanomia_secret_key_2025"
 
# ──────────────────────────────────────────────
# DATA HELPER FUNCTIONS
# ──────────────────────────────────────────────
 
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
 
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
 
def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
 
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
 
def get_today():
    return datetime.now().strftime("%Y-%m-%d")
 
def get_user(username):
    data = load_json("users.json")
    for user in data.get("users", []):
        if user["username"] == username:
            return user
    return None
 
def save_user(user_obj):
    data = load_json("users.json")
    users = data.get("users", [])
    for i, u in enumerate(users):
        if u["username"] == user_obj["username"]:
            users[i] = user_obj
            data["users"] = users
            save_json("users.json", data)
            return
    users.append(user_obj)
    data["users"] = users
    save_json("users.json", data)
 
def get_today_checkin(username):
    data = load_json("daily_checkins.json")
    user_checkins = data.get("checkins", {}).get(username, [])
    today = get_today()
    for c in user_checkins:
        if c["date"] == today:
            return c
    return None
 
def get_daily_affirmation():
    data = load_json("affirmations.json")
    affirmations = data.get("affirmations", [])
    if not affirmations:
        return {"text": "You are enough.", "emoji": "💗"}
    day_index = datetime.now().timetuple().tm_yday % len(affirmations)
    return affirmations[day_index]
 
# ──────────────────────────────────────────────
# EMOTIONAL ANALYSIS ENGINE
# ──────────────────────────────────────────────
 
def analyze_emotional_state(responses):
    """Analyze questionnaire responses and return personalized recommendations."""
    stress = responses.get("q2", 5)
    anxiety = responses.get("q7", 5)
    sleep = responses.get("q3", "good")
    goal = responses.get("q4", "stress_relief")
    motivation = responses.get("q5", 5)
 
    # Map sleep text to score
    sleep_scores = {"excellent": 9, "good": 7, "fair": 5, "poor": 3, "terrible": 1}
    sleep_score = sleep_scores.get(sleep, 5)
 
    # Compute overall wellness score
    wellness_score = max(0, 10 - (stress * 0.3 + anxiety * 0.3) + (sleep_score * 0.2) + (motivation * 0.2))
    wellness_score = min(10, round(wellness_score, 1))
 
    # Select wellness plan
    plan_map = {
        "stress_relief": "stress_recovery",
        "better_sleep": "better_sleep",
        "anxiety_control": "anxiety_relief",
        "mood_boost": "mood_boost",
        "focus": "stress_recovery"
    }
    recommended_plan = plan_map.get(goal, "stress_recovery")
 
    # Generate insights
    insights = []
    if stress >= 7:
        insights.append("Your stress levels are high. A daily 5-minute breathing practice can help.")
    elif stress <= 3:
        insights.append("Your stress levels look good! Keep maintaining your calm habits.")
 
    if anxiety >= 7:
        insights.append("You're experiencing significant anxiety. CBT exercises and grounding may help.")
    elif anxiety <= 3:
        insights.append("Your anxiety is well-managed. Wonderful!")
 
    if sleep_score <= 4:
        insights.append("Your sleep needs attention. Try our Sleep Wind-Down meditation tonight.")
    elif sleep_score >= 8:
        insights.append("Excellent sleep quality! Good sleep is foundational to mental wellness.")
 
    if motivation <= 3:
        insights.append("Let's boost your motivation with small daily wins and wellness challenges.")
 
    return {
        "wellness_score": wellness_score,
        "recommended_plan": recommended_plan,
        "insights": insights,
        "stress_level": stress,
        "anxiety_level": anxiety,
        "sleep_score": sleep_score,
        "motivation": motivation
    }
 
def calculate_weekly_stats(username):
    """Calculate mood and wellness stats for the past 7 days."""
    data = load_json("daily_checkins.json")
    checkins = data.get("checkins", {}).get(username, [])
 
    today = datetime.now()
    week_data = []
    for i in range(6, -1, -1):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = next((c for c in checkins if c["date"] == date), None)
        week_data.append({
            "date": date,
            "day": (today - timedelta(days=i)).strftime("%a"),
            "stress": entry["stress"] if entry else None,
            "anxiety": entry["anxiety"] if entry else None,
            "sleep": entry["sleep_quality"] if entry else None,
            "energy": entry["energy"] if entry else None,
            "mood": entry["mood"] if entry else None
        })
    return week_data
 
def calculate_streak(username):
    """Calculate current check-in streak."""
    data = load_json("daily_checkins.json")
    checkins = data.get("checkins", {}).get(username, [])
    if not checkins:
        return 0
    dates = sorted([c["date"] for c in checkins], reverse=True)
    today = get_today()
    streak = 0
    current = datetime.strptime(today, "%Y-%m-%d")
    for d in dates:
        d_dt = datetime.strptime(d, "%Y-%m-%d")
        if (current - d_dt).days == streak:
            streak += 1
        else:
            break
    return streak
 
def get_ai_response(message, username=None):
    """Generate AI emotional support responses."""
    message_lower = message.lower()
 
    # Emotional keyword detection
    if any(w in message_lower for w in ["sad", "crying", "tears", "depressed", "hopeless", "worthless"]):
        responses = [
            "I'm so sorry you're feeling this way. Your pain is real and valid. 💙 Remember, dark moments don't last forever. Would you like to try a calming breathing exercise right now?",
            "It takes courage to express how you feel. I'm here with you. 🤗 Sometimes just naming our emotions can reduce their power. You're not alone in this.",
            "Feeling sad is part of being human. Be gentle with yourself. 🌸 Consider writing in your journal — it can help release these feelings."
        ]
    elif any(w in message_lower for w in ["anxious", "anxiety", "panic", "worried", "nervous", "scared"]):
        responses = [
            "Anxiety can feel overwhelming, but you're stronger than it. 🌊 Try the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "I hear you. Your nervous system is trying to protect you. 💚 Let's slow things down with a deep breath. In for 4 counts... hold for 4... out for 6. You're safe.",
            "Anxiety lies — it makes things seem worse than they are. 🌟 Would you like to try a quick CBT exercise to challenge anxious thoughts?"
        ]
    elif any(w in message_lower for w in ["stress", "stressed", "overwhelmed", "too much", "can't cope"]):
        responses = [
            "It sounds like you have a lot on your plate. 🍃 Let's break it down — what feels most overwhelming right now? Sometimes naming it makes it more manageable.",
            "Stress is your body's signal that it needs care. ✨ You've handled hard things before. What's one tiny thing you can do right now to feel a bit lighter?",
            "When everything feels heavy, focus on just the next breath. 🌬️ Then the next small step. You don't have to solve everything at once."
        ]
    elif any(w in message_lower for w in ["happy", "good", "great", "wonderful", "excited", "amazing"]):
        responses = [
            "That's wonderful to hear! 🌟 Your positive energy is beautiful. What's been making you feel this way? Celebrating good moments is so important.",
            "I love that! ✨ Hold onto that feeling — it's a reminder of your resilience and capacity for joy.",
            "You're radiating positive energy! 🌸 These are the moments that remind us life is beautiful. Keep going!"
        ]
    elif any(w in message_lower for w in ["tired", "exhausted", "fatigue", "sleep", "drained"]):
        responses = [
            "Rest is not laziness — it's wisdom. 🌙 Your body and mind are asking for care. Is there any part of your day you could simplify or pause today?",
            "When we're exhausted, everything feels harder. 💙 Please be kind to yourself. Even 10 minutes of rest can restore some energy. Try our Sleep Wind-Down meditation.",
            "Exhaustion is a sign you've been giving a lot. 🌿 It's okay to slow down. What's one thing you could let go of today?"
        ]
    elif any(w in message_lower for w in ["help", "support", "advice", "guidance", "what should"]):
        responses = [
            "I'm here to support you! 💗 Equanomia is your safe space. You can try: Meditation for calm, Journal for expression, CBT exercises for thought patterns, or just talk to me anytime.",
            "You reached out — that's already a brave step. 🌟 I'm here. Would you like to try a breathing exercise, log your mood, or explore your wellness plan?",
            "Supporting you is what I'm here for. 🤗 Let's figure this out together. What feels most helpful right now — calming down, processing emotions, or finding motivation?"
        ]
    elif any(w in message_lower for w in ["meditate", "meditation", "breathe", "breathing", "calm down"]):
        responses = [
            "Wonderful choice! 🧘 Meditation is one of the most powerful tools for mental wellness. Head to the Meditation section for guided sessions, or try this: breathe in for 4 counts, hold for 4, out for 6. Repeat 5 times.",
            "Let's breathe together. 🌬️ Place one hand on your chest, one on your belly. Take a slow deep breath in... and gently release. You're doing beautifully.",
            "Meditation rewires your brain for calm. 🌸 Even 5 minutes a day makes a real difference. Our Breathing Basics session is perfect to start with."
        ]
    elif any(w in message_lower for w in ["journal", "write", "thoughts", "express"]):
        responses = [
            "Writing is such a powerful way to process emotions. 📓 Your journal is a safe space — no judgment, no rules. Head to the Journal section and let your thoughts flow freely.",
            "Journaling can help you understand yourself better. 🌱 Try starting with 'Today I feel... because...' and see where it takes you.",
            "Your thoughts deserve to be heard — even if just by yourself. ✍️ Would you like a journaling prompt to get started?"
        ]
    else:
        responses = [
            "I'm here with you. 💙 Equanomia is your daily wellness companion. Whether you want to meditate, journal, track your mood, or just talk — I'm always here. How can I support you today?",
            "Thank you for sharing with me. 🌸 Every conversation is a step toward better understanding yourself. Is there something specific on your mind, or would you like a wellness suggestion?",
            "You matter, and your well-being matters. ✨ I'm here to listen and support. What's on your heart today?",
            "It's great to hear from you. 🌿 Remember to take care of yourself today. Would you like to check in with your mood, do a quick meditation, or explore your wellness plan?"
        ]
 
    return random.choice(responses)
 
# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────
 
@app.route("/")
def index():
    """Landing page."""
    affirmation = get_daily_affirmation()
    return render_template("index.html", affirmation=affirmation)
 
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = get_user(username)
        if user and user.get("password") == password:
            session["username"] = username
            session["user_name"] = user.get("name", username)
            # Update streak
            streak = calculate_streak(username)
            user["streak"] = streak
            save_user(user)
            # Check if questionnaire done
            if not user.get("questionnaire_done"):
                return redirect(url_for("questionnaire"))
            # Check if daily check-in done
            if not get_today_checkin(username):
                return redirect(url_for("daily_checkin"))
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password. Please try again.")
    return render_template("login.html")
 
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User sign-up."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()
        if get_user(username):
            return render_template("signup.html", error="Username already exists. Please choose another.")
        avatars = ["🌸", "🌿", "💙", "🌟", "✨", "🦋", "🌊", "🌻"]
        new_user = {
            "id": f"usr_{random.randint(100, 999)}",
            "username": username,
            "email": email,
            "password": password,
            "name": name,
            "joined": get_today(),
            "avatar": random.choice(avatars),
            "coins": 50,
            "xp": 0,
            "level": 1,
            "streak": 0,
            "badges": ["new_member"],
            "questionnaire_done": False,
            "last_checkin": None,
            "wellness_plan": None,
            "pin": None
        }
        save_user(new_user)
        session["username"] = username
        session["user_name"] = name
        return redirect(url_for("questionnaire"))
    return render_template("signup.html")
 
@app.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for("index"))
 
@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    """Onboarding emotional wellness questionnaire."""
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        responses = {}
        data = request.get_json()
        if data:
            responses = data
        else:
            for key, val in request.form.items():
                try:
                    responses[key] = int(val)
                except ValueError:
                    responses[key] = val
        # Analyze responses
        analysis = analyze_emotional_state(responses)
        # Save to questionnaire data
        q_data = load_json("questionnaire_data.json")
        q_data.setdefault("responses", {})[session["username"]] = {
            "date": get_today(),
            "responses": responses,
            "analysis": analysis
        }
        save_json("questionnaire_data.json", q_data)
        # Update user
        user = get_user(session["username"])
        if user:
            user["questionnaire_done"] = True
            user["wellness_plan"] = analysis["recommended_plan"]
            user["coins"] = user.get("coins", 0) + 100
            user["xp"] = user.get("xp", 0) + 200
            save_user(user)
        return jsonify({"status": "ok", "redirect": url_for("daily_checkin"), "analysis": analysis})
    q_data = load_json("questionnaire_data.json")
    questions = q_data.get("onboarding_questions", [])
    return render_template("questionnaire.html", questions=questions)
 
@app.route("/daily_checkin", methods=["GET", "POST"])
def daily_checkin():
    """Daily emotional check-in."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        data = request.get_json() or {}
        checkin_entry = {
            "date": get_today(),
            "mood": data.get("mood", "neutral"),
            "stress": int(data.get("stress", 5)),
            "anxiety": int(data.get("anxiety", 5)),
            "sleep_quality": int(data.get("sleep_quality", 5)),
            "sleep_hours": float(data.get("sleep_hours", 7)),
            "energy": int(data.get("energy", 5)),
            "motivation": int(data.get("motivation", 5)),
            "gratitude": data.get("gratitude", ""),
            "reflection": data.get("reflection", "")
        }
        ci_data = load_json("daily_checkins.json")
        ci_data.setdefault("checkins", {}).setdefault(username, [])
        # Remove today's entry if exists
        ci_data["checkins"][username] = [
            c for c in ci_data["checkins"][username] if c["date"] != get_today()
        ]
        ci_data["checkins"][username].append(checkin_entry)
        save_json("daily_checkins.json", ci_data)
        # Reward coins/xp
        user = get_user(username)
        if user:
            user["coins"] = user.get("coins", 0) + 15
            user["xp"] = user.get("xp", 0) + 30
            user["last_checkin"] = get_today()
            user["streak"] = calculate_streak(username)
            save_user(user)
        return jsonify({"status": "ok", "redirect": url_for("dashboard")})
    # Generate insights from history
    week_stats = calculate_weekly_stats(username)
    affirmation = get_daily_affirmation()
    return render_template("daily_checkin.html",
                           week_stats=week_stats,
                           affirmation=affirmation)
 
@app.route("/dashboard")
def dashboard():
    """Main user dashboard."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user = get_user(username)
    if not user:
        return redirect(url_for("login"))
    today_checkin = get_today_checkin(username)
    affirmation = get_daily_affirmation()
    week_stats = calculate_weekly_stats(username)
    # Load wellness plan
    wp_data = load_json("wellness_plans.json")
    user_plan = None
    if user.get("wellness_plan"):
        user_plan = next((p for p in wp_data.get("plans", []) if p["id"] == user["wellness_plan"]), None)
    # Recent moods
    mood_data = load_json("moods.json")
    recent_moods = mood_data.get("mood_logs", {}).get(username, [])[-5:]
    # Journal entries
    j_data = load_json("journal_data.json")
    recent_journals = j_data.get("journals", {}).get(username, [])[-3:]
    # Meditation data
    med_data = load_json("meditation_data.json")
    sessions = med_data.get("sessions", [])[:3]
    # Music
    music_data = load_json("music_data.json")
    tracks = music_data.get("tracks", [])[:4]
    return render_template("dashboard.html",
                           user=user,
                           today_checkin=today_checkin,
                           affirmation=affirmation,
                           week_stats=week_stats,
                           user_plan=user_plan,
                           recent_moods=recent_moods,
                           recent_journals=recent_journals,
                           med_sessions=sessions,
                           tracks=tracks)
 
@app.route("/mood_tracker", methods=["GET", "POST"])
def mood_tracker():
    """Mood tracking page."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        data = request.get_json() or {}
        mood_data = load_json("moods.json")
        mood_logs = mood_data.get("mood_logs", {})
        mood_logs.setdefault(username, [])
        new_entry = {
            "date": get_today(),
            "mood": data.get("mood", "neutral"),
            "note": data.get("note", ""),
            "score": data.get("score", 5)
        }
        mood_logs[username] = [e for e in mood_logs[username] if e["date"] != get_today()]
        mood_logs[username].append(new_entry)
        mood_data["mood_logs"] = mood_logs
        save_json("moods.json", mood_data)
        user = get_user(username)
        if user:
            user["coins"] = user.get("coins", 0) + 10
            user["xp"] = user.get("xp", 0) + 20
            save_user(user)
        return jsonify({"status": "ok"})
    mood_data = load_json("moods.json")
    mood_options = mood_data.get("mood_options", [])
    mood_logs = mood_data.get("mood_logs", {}).get(username, [])
    return render_template("mood_tracker.html",
                           mood_options=mood_options,
                           mood_logs=mood_logs[-14:])
 
@app.route("/meditation")
def meditation():
    """Meditation and relaxation page."""
    if "username" not in session:
        return redirect(url_for("login"))
    med_data = load_json("meditation_data.json")
    sessions = med_data.get("sessions", [])
    return render_template("meditation.html", sessions=sessions)
 
@app.route("/meditation/complete", methods=["POST"])
def complete_meditation():
    """Mark meditation session as complete."""
    if "username" not in session:
        return jsonify({"status": "error"})
    username = session["username"]
    data = request.get_json() or {}
    session_id = data.get("session_id")
    med_data = load_json("meditation_data.json")
    sessions = med_data.get("sessions", [])
    xp_reward = next((s.get("xp_reward", 10) for s in sessions if s["id"] == session_id), 10)
    user = get_user(username)
    if user:
        user["coins"] = user.get("coins", 0) + 20
        user["xp"] = user.get("xp", 0) + xp_reward
        save_user(user)
    return jsonify({"status": "ok", "xp": xp_reward, "coins": 20})
 
@app.route("/sleep_tracker", methods=["GET", "POST"])
def sleep_tracker():
    """Sleep tracking page."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        data = request.get_json() or {}
        ci_data = load_json("daily_checkins.json")
        entries = ci_data.get("checkins", {}).get(username, [])
        today_entry = next((e for e in entries if e["date"] == get_today()), None)
        if today_entry:
            today_entry["sleep_quality"] = int(data.get("sleep_quality", 5))
            today_entry["sleep_hours"] = float(data.get("sleep_hours", 7))
        else:
            ci_data.setdefault("checkins", {}).setdefault(username, []).append({
                "date": get_today(),
                "sleep_quality": int(data.get("sleep_quality", 5)),
                "sleep_hours": float(data.get("sleep_hours", 7)),
                "mood": "neutral", "stress": 5, "anxiety": 5,
                "energy": 5, "motivation": 5, "gratitude": "", "reflection": ""
            })
        save_json("daily_checkins.json", ci_data)
        user = get_user(username)
        if user:
            user["coins"] = user.get("coins", 0) + 10
            save_user(user)
        return jsonify({"status": "ok"})
    ci_data = load_json("daily_checkins.json")
    sleep_history = [
        {"date": c["date"], "hours": c.get("sleep_hours", 0), "quality": c.get("sleep_quality", 0)}
        for c in ci_data.get("checkins", {}).get(username, [])[-14:]
    ]
    return render_template("sleep_tracker.html", sleep_history=sleep_history)
 
@app.route("/journal", methods=["GET", "POST"])
def journal():
    """Journal and reflection page."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        data = request.get_json() or {}
        j_data = load_json("journal_data.json")
        entries = j_data.get("journals", {}).setdefault(username, [])
        new_entry = {
            "id": f"j{random.randint(1000, 9999)}",
            "date": get_today(),
            "title": data.get("title", "Journal Entry"),
            "content": data.get("content", ""),
            "mood": data.get("mood", "neutral"),
            "tags": data.get("tags", []),
            "type": data.get("type", "journal")
        }
        entries.append(new_entry)
        j_data["journals"][username] = entries
        save_json("journal_data.json", j_data)
        user = get_user(username)
        if user:
            user["coins"] = user.get("coins", 0) + 15
            user["xp"] = user.get("xp", 0) + 25
            save_user(user)
        return jsonify({"status": "ok"})
    j_data = load_json("journal_data.json")
    entries = j_data.get("journals", {}).get(username, [])
    prompts = j_data.get("prompts", [])
    prompt = random.choice(prompts) if prompts else "What's on your mind today?"
    return render_template("journal.html",
                           entries=sorted(entries, key=lambda x: x["date"], reverse=True),
                           prompt=prompt)
 
@app.route("/journal/delete/<journal_id>", methods=["DELETE"])
def delete_journal(journal_id):
    """Delete a journal entry."""
    if "username" not in session:
        return jsonify({"status": "error"})
    username = session["username"]
    j_data = load_json("journal_data.json")
    entries = j_data.get("journals", {}).get(username, [])
    j_data["journals"][username] = [e for e in entries if e["id"] != journal_id]
    save_json("journal_data.json", j_data)
    return jsonify({"status": "ok"})
 
@app.route("/statistics")
def statistics():
    """Statistics and analytics dashboard."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user = get_user(username)
    week_stats = calculate_weekly_stats(username)
    ci_data = load_json("daily_checkins.json")
    all_checkins = ci_data.get("checkins", {}).get(username, [])
    # Monthly mood averages
    mood_counts = {}
    for c in all_checkins:
        m = c.get("mood", "neutral")
        mood_counts[m] = mood_counts.get(m, 0) + 1
    # Weekly averages
    weekly_stress = [w["stress"] for w in week_stats if w["stress"] is not None]
    weekly_sleep = [w["sleep"] for w in week_stats if w["sleep"] is not None]
    weekly_energy = [w["energy"] for w in week_stats if w["energy"] is not None]
    avg_stress = round(sum(weekly_stress) / len(weekly_stress), 1) if weekly_stress else 0
    avg_sleep = round(sum(weekly_sleep) / len(weekly_sleep), 1) if weekly_sleep else 0
    avg_energy = round(sum(weekly_energy) / len(weekly_energy), 1) if weekly_energy else 0
    return render_template("statistics.html",
                           user=user,
                           week_stats=week_stats,
                           mood_counts=mood_counts,
                           avg_stress=avg_stress,
                           avg_sleep=avg_sleep,
                           avg_energy=avg_energy,
                           total_checkins=len(all_checkins))
 
@app.route("/wellness_analysis")
def wellness_analysis():
    """Wellness plans and analysis page."""
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user = get_user(username)
    wp_data = load_json("wellness_plans.json")
    all_plans = wp_data.get("plans", [])
    q_data = load_json("questionnaire_data.json")
    user_analysis = q_data.get("responses", {}).get(username, {})
    analysis = user_analysis.get("analysis", {})
    return render_template("wellness_analysis.html",
                           user=user,
                           plans=all_plans,
                           analysis=analysis)
 
@app.route("/wellness_analysis/select_plan", methods=["POST"])
def select_plan():
    """Select a wellness plan."""
    if "username" not in session:
        return jsonify({"status": "error"})
    data = request.get_json() or {}
    user = get_user(session["username"])
    if user:
        user["wellness_plan"] = data.get("plan_id")
        save_user(user)
    return jsonify({"status": "ok"})
 
@app.route("/chatbot")
def chatbot():
    """AI emotional support chatbot page."""
    if "username" not in session:
        return redirect(url_for("login"))
    user = get_user(session["username"])
    return render_template("chatbot.html", user=user)
 
@app.route("/chatbot/message", methods=["POST"])
def chatbot_message():
    """Handle chatbot messages."""
    if "username" not in session:
        return jsonify({"status": "error"})
    data = request.get_json() or {}
    message = data.get("message", "")
    response = get_ai_response(message, session["username"])
    return jsonify({"status": "ok", "response": response})
 
@app.route("/emergency")
def emergency():
    """Emergency support page."""
    return render_template("emergency.html")
 
# ──────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────
 
@app.route("/api/user_stats")
def api_user_stats():
    """API: Get current user stats."""
    if "username" not in session:
        return jsonify({"error": "Not logged in"})
    user = get_user(session["username"])
    if not user:
        return jsonify({"error": "User not found"})
    return jsonify({
        "coins": user.get("coins", 0),
        "xp": user.get("xp", 0),
        "level": user.get("level", 1),
        "streak": user.get("streak", 0),
        "badges": user.get("badges", [])
    })
 
@app.route("/api/weekly_data")
def api_weekly_data():
    """API: Get weekly check-in data for charts."""
    if "username" not in session:
        return jsonify({"error": "Not logged in"})
    week_stats = calculate_weekly_stats(session["username"])
    return jsonify(week_stats)
 
@app.route("/api/mood_history")
def api_mood_history():
    """API: Get mood history."""
    if "username" not in session:
        return jsonify({"error": "Not logged in"})
    mood_data = load_json("moods.json")
    logs = mood_data.get("mood_logs", {}).get(session["username"], [])
    return jsonify(logs[-30:])
 
@app.route("/api/affirmation")
def api_affirmation():
    """API: Get today's affirmation."""
    return jsonify(get_daily_affirmation())
 
@app.route("/api/cbt_exercise")
def api_cbt_exercise():
    """API: Get a random CBT exercise."""
    exercises = [
        {
            "title": "Thought Record",
            "description": "Write down an anxious thought, then challenge it with evidence.",
            "steps": [
                "Identify the automatic thought",
                "Rate how much you believe it (0-100%)",
                "List evidence that supports this thought",
                "List evidence that contradicts this thought",
                "Create a balanced alternative thought",
                "Re-rate your belief in the original thought"
            ],
            "icon": "📝",
            "xp": 30
        },
        {
            "title": "Gratitude Anchoring",
            "description": "Ground yourself in gratitude to shift emotional state.",
            "steps": [
                "Find a quiet, comfortable spot",
                "Close your eyes and take 3 deep breaths",
                "Think of 3 things you are genuinely grateful for",
                "For each one, feel the emotion fully for 30 seconds",
                "Notice how your body feels after this exercise",
                "Write down your reflections"
            ],
            "icon": "🙏",
            "xp": 25
        },
        {
            "title": "Behavioral Activation",
            "description": "Break the cycle of low mood by scheduling pleasant activities.",
            "steps": [
                "List 5 activities that you used to enjoy",
                "Rate how much pleasure each might give you (0-10)",
                "Choose the highest-rated activity",
                "Schedule it for today or tomorrow",
                "Do the activity — even if motivation is low",
                "Record how you feel after"
            ],
            "icon": "🎯",
            "xp": 35
        },
        {
            "title": "Cognitive Defusion",
            "description": "Distance yourself from unhelpful thoughts.",
            "steps": [
                "Notice a difficult thought you're having",
                "Say: 'I notice I'm having the thought that...'",
                "Imagine the thought as a leaf floating on a stream",
                "Watch it drift away without getting on the leaf",
                "Return to the present moment",
                "Notice how you feel now"
            ],
            "icon": "🍃",
            "xp": 25
        },
        {
            "title": "Worry Time",
            "description": "Contain worries to a specific time to reduce their impact.",
            "steps": [
                "Schedule 15 minutes of 'worry time' today",
                "When worries arise before that time, postpone them",
                "Note the worry briefly and remind yourself to address it later",
                "During your worry time, address each worry mindfully",
                "Ask: Can I do something about this? If yes, plan it.",
                "After the time is up, return to your day"
            ],
            "icon": "⏱️",
            "xp": 30
        }
    ]
    return jsonify(random.choice(exercises))
 
@app.route("/api/wellness_music")
def api_wellness_music():
    """API: Get music tracks."""
    music_data = load_json("music_data.json")
    return jsonify(music_data.get("tracks", []))
 
@app.route("/api/update_xp", methods=["POST"])
def api_update_xp():
    """API: Update user XP and coins."""
    if "username" not in session:
        return jsonify({"status": "error"})
    data = request.get_json() or {}
    user = get_user(session["username"])
    if user:
        user["xp"] = user.get("xp", 0) + data.get("xp", 0)
        user["coins"] = user.get("coins", 0) + data.get("coins", 0)
        # Level up check
        xp_per_level = 500
        new_level = (user["xp"] // xp_per_level) + 1
        leveled_up = new_level > user.get("level", 1)
        user["level"] = new_level
        save_user(user)
        return jsonify({"status": "ok", "xp": user["xp"], "coins": user["coins"],
                        "level": user["level"], "leveled_up": leveled_up})
    return jsonify({"status": "error"})
 
# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
 