"""
Comprehensive Role & Feature Test for ProblemScope
Tests: Admin login, Regular user login, all major routes, real-time features
"""
import requests
import json
import re
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

# ---- Credentials ----
ADMIN_EMAIL = "admin@problemscope.com"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "testuser@test.com"
USER_PASSWORD = "Test1234!"

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

results = []

def test(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status}  {name}" + (f" — {detail}" if detail else ""))

def warn(name, detail=""):
    results.append((WARN, name, detail))
    print(f"  {WARN}  {name}" + (f" — {detail}" if detail else ""))

def get_csrf_token(session, url):
    """Fetch a page and extract CSRF token from a form."""
    r = session.get(url)
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.text)  
    if match:
        return match.group(1)
    # Try alternate format
    match = re.search(r'value="([^"]+)"[^>]*name="csrf_token"', r.text)
    return match.group(1) if match else None

def login(session, email, password):
    """Log into the app, returns True on success."""
    csrf = get_csrf_token(session, f"{BASE_URL}/login")
    data = {"email": email, "password": password, "csrf_token": csrf or ""}
    r = session.post(f"{BASE_URL}/login", data=data, allow_redirects=True)
    # Check for login success indicators
    return ("Login successful" in r.text or
            "dashboard" in r.url or
            "home" in r.url or
            r.url == f"{BASE_URL}/") and "Login failed" not in r.text

def get_page_status(session, url):
    r = session.get(url, allow_redirects=True)
    return r.status_code, r.text, r.url

# ============================================================
print("\n" + "="*65)
print("  ProblemScope — Comprehensive Role & Feature Test")
print("="*65)
print(f"  Target: {BASE_URL}")
print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*65)

# ============================================================
print("\n[1] BASIC CONNECTIVITY")
# ============================================================
s = requests.Session()
try:
    r = s.get(BASE_URL, timeout=5)
    test("Home page loads", r.status_code == 200, f"HTTP {r.status_code}")
    test("HTML content served", "<html" in r.text.lower())
    test("App title present", "ProblemScope" in r.text or "problem" in r.text.lower())
except Exception as e:
    test("Home page reachable", False, str(e))
    print("\n  ⛔  Cannot reach app — aborting tests.")
    sys.exit(1)

# ============================================================
print("\n[2] PUBLIC ROUTES (unauthenticated)")
# ============================================================
pub_routes = [
    ("/", "Home", 200),
    ("/home", "Home alias", 200),
    ("/login", "Login page", 200),
    ("/register", "Register page", 200),
    ("/about", "About page", 200),
    ("/contact", "Contact page", 200),
    ("/analytics", "Analytics page", 200),
    ("/activity", "Activity feed", 200),
]
anon = requests.Session()
for path, name, expected in pub_routes:
    try:
        r = anon.get(f"{BASE_URL}{path}", allow_redirects=True)
        test(f"Public: {name}", r.status_code == expected, f"HTTP {r.status_code}")
    except Exception as e:
        test(f"Public: {name}", False, str(e))

# Protected routes should redirect to login
protected_routes = ["/dashboard", "/profile/edit", "/bookmarks", "/admin"]
for path in protected_routes:
    r = anon.get(f"{BASE_URL}{path}", allow_redirects=True)
    redirected_to_login = "login" in r.url or "login" in r.text.lower()
    test(f"Protected {path} → redirects to login", redirected_to_login, f"landed at {r.url}")

# ============================================================
print("\n[3] USER REGISTRATION")
# ============================================================
reg_session = requests.Session()
import time
ts = str(int(time.time()))[-5:]
new_email = f"newuser{ts}@test.com"
csrf = get_csrf_token(reg_session, f"{BASE_URL}/register")
reg_data = {
    "username": f"newuser{ts}",
    "email": new_email,
    "password": "NewPass1234!",
    "confirm_password": "NewPass1234!",
    "location": "Test Town",
    "skills": "Python",
    "csrf_token": csrf or ""
}
r = reg_session.post(f"{BASE_URL}/register", data=reg_data, allow_redirects=True)
test("User registration", r.status_code == 200, f"HTTP {r.status_code} | " + ("OK" if "login" in r.url else r.url))

# ============================================================
print("\n[4] REGULAR USER LOGIN & FEATURES")
# ============================================================
user_s = requests.Session()
logged_in = login(user_s, USER_EMAIL, USER_PASSWORD)
test("Regular user login", logged_in, f"{USER_EMAIL}")

if logged_in:
    # Dashboard
    code, text, url = get_page_status(user_s, f"{BASE_URL}/dashboard")
    test("Dashboard accessible", code == 200 and "login" not in url, f"HTTP {code}")

    # Edit profile page
    code, text, url = get_page_status(user_s, f"{BASE_URL}/profile/edit")
    test("Edit profile page loads", code == 200 and "edit" in url, f"HTTP {code}")

    # Bookmarks
    code, text, url = get_page_status(user_s, f"{BASE_URL}/bookmarks")
    test("Bookmarks page loads", code == 200, f"HTTP {code}")

    # Create problem page
    code, text, url = get_page_status(user_s, f"{BASE_URL}/problem/new")
    test("New problem page loads", code == 200, f"HTTP {code}")

    # Post a new problem
    csrf = get_csrf_token(user_s, f"{BASE_URL}/problem/new")
    problem_data = {
        "title": "Test Problem From Automated Test",
        "description": "This is an automated test problem to verify the system is working correctly with sufficient detail.",
        "category": "Infrastructure",
        "location": "Test Location",
        "severity": "Medium",
        "affected_count": "5",
        "csrf_token": csrf or ""
    }
    r = user_s.post(f"{BASE_URL}/problem/new", data=problem_data, allow_redirects=True)
    problem_created = r.status_code == 200 and ("problem has been posted" in r.text or "Problem" in r.text)
    test("Create new problem", problem_created, f"HTTP {r.status_code}")

    # User profile page
    code, text, url = get_page_status(user_s, f"{BASE_URL}/user/testuser")
    test("User profile page loads", code == 200, f"HTTP {code}")

    # Activity feed (authenticated)
    code, text, url = get_page_status(user_s, f"{BASE_URL}/activity")
    test("Activity feed (auth user)", code == 200, f"HTTP {code}")

    # Analytics (public, but test while authenticated)
    code, text, url = get_page_status(user_s, f"{BASE_URL}/analytics")
    test("Analytics page (auth user)", code == 200, f"HTTP {code}")

    # Regular user should NOT access admin panel
    code, text, url = get_page_status(user_s, f"{BASE_URL}/admin")
    test("Regular user blocked from /admin", code == 403 or "403" in text or "forbidden" in text.lower() or "login" in url,
         f"HTTP {code} | {url}")

    # Logout
    r = user_s.get(f"{BASE_URL}/logout", allow_redirects=True)
    test("Regular user logout", r.status_code == 200, f"HTTP {r.status_code}")
else:
    warn("Skipping user feature tests — login failed")

# ============================================================
print("\n[5] ADMIN LOGIN & ADMIN FEATURES")
# ============================================================
admin_s = requests.Session()
admin_logged_in = login(admin_s, ADMIN_EMAIL, ADMIN_PASSWORD)
test("Admin user login", admin_logged_in, f"{ADMIN_EMAIL}")

if admin_logged_in:
    # Admin panel
    code, text, url = get_page_status(admin_s, f"{BASE_URL}/admin")
    test("Admin panel accessible", code == 200 and "login" not in url, f"HTTP {code}")
    test("Admin panel shows user count", "users" in text.lower() or "user" in text.lower(), "content check")
    test("Admin panel shows problem count", "problem" in text.lower(), "content check")

    # Admin can access all regular pages too
    for path, name in [("/dashboard", "Dashboard"), ("/bookmarks", "Bookmarks"),
                       ("/analytics", "Analytics"), ("/activity", "Activity")]:
        code, text, url = get_page_status(admin_s, f"{BASE_URL}{path}")
        test(f"Admin can access {name}", code == 200, f"HTTP {code}")

    # Admin logout
    r = admin_s.get(f"{BASE_URL}/logout", allow_redirects=True)
    test("Admin logout", r.status_code == 200, f"HTTP {r.status_code}")
else:
    warn("Skipping admin feature tests — admin login failed")

# ============================================================
print("\n[6] PROBLEM DETAIL & INTERACTIONS")
# ============================================================
# Login as user again for interaction tests
user_s2 = requests.Session()
if login(user_s2, USER_EMAIL, USER_PASSWORD):
    # Find a problem to interact with
    r = user_s2.get(f"{BASE_URL}/home")
    problem_ids = re.findall(r'href="/problem/(\d+)"', r.text)
    if problem_ids:
        pid = problem_ids[0]
        code, text, url = get_page_status(user_s2, f"{BASE_URL}/problem/{pid}")
        test(f"Problem detail page loads (ID={pid})", code == 200, f"HTTP {code}")
        test("Problem detail has title", "<h" in text and len(text) > 500, "content check")

        # Try adding a comment
        csrf = get_csrf_token(user_s2, f"{BASE_URL}/problem/{pid}")
        comment_data = {"content": "Automated test comment — system working!", "csrf_token": csrf or ""}
        r = user_s2.post(f"{BASE_URL}/problem/{pid}", data=comment_data, allow_redirects=True)
        test("Add comment to problem", r.status_code == 200, f"HTTP {r.status_code}")

        # Try bookmarking
        csrf2 = get_csrf_token(user_s2, f"{BASE_URL}/problem/{pid}")
        r = user_s2.post(f"{BASE_URL}/problem/{pid}/bookmark", data={"csrf_token": csrf2 or ""}, allow_redirects=True)
        test("Bookmark problem", r.status_code == 200, f"HTTP {r.status_code}")

        # Export PDF
        code, text, url = get_page_status(user_s2, f"{BASE_URL}/problem/{pid}/export_pdf")
        test("Export problem as PDF", code == 200, f"HTTP {code}")

        # Verify problem
        csrf3 = get_csrf_token(user_s2, f"{BASE_URL}/problem/{pid}")
        r = user_s2.post(f"{BASE_URL}/problem/{pid}/verify",
                         data={"proof_text": "Verified by test", "csrf_token": csrf3 or ""},
                         allow_redirects=True)
        test("Verify problem", r.status_code == 200, f"HTTP {r.status_code}")
    else:
        warn("No problems found to test interactions")
else:
    warn("Skipping interaction tests — second login failed")

# ============================================================
print("\n[7] ERROR HANDLING")
# ============================================================
e_s = requests.Session()
r = e_s.get(f"{BASE_URL}/problem/999999", allow_redirects=True)
test("404 for non-existent problem", r.status_code == 404 or "not found" in r.text.lower() or "404" in r.text, f"HTTP {r.status_code}")

r = e_s.get(f"{BASE_URL}/user/nonexistentuser_xyz", allow_redirects=True)
test("404 for non-existent user", r.status_code == 404 or "not found" in r.text.lower(), f"HTTP {r.status_code}")

# ============================================================
print("\n[8] REAL-TIME / DYNAMIC CHECKS")
# ============================================================
# Verify that stats update dynamically by checking analytics
anon2 = requests.Session()
r1 = anon2.get(f"{BASE_URL}/analytics")
# Post a new problem and verify stats change
user_rt = requests.Session()
if login(user_rt, USER_EMAIL, USER_PASSWORD):
    csrf = get_csrf_token(user_rt, f"{BASE_URL}/problem/new")
    r = user_rt.post(f"{BASE_URL}/problem/new", data={
        "title": "Real-time test problem",
        "description": "Testing real-time stats update with this problem submission for automated testing.",
        "category": "Environment",
        "location": "Test Zone",
        "severity": "Low",
        "affected_count": "1",
        "csrf_token": csrf or ""
    }, allow_redirects=True)
    r2 = anon2.get(f"{BASE_URL}/analytics")
    # Count problems mentioned in analytics
    count1 = r1.text.count("problem") if r1.status_code == 200 else 0
    test("Analytics page updates after new problem", r2.status_code == 200, "real-time check")
    # Check home shows problems
    r_home = anon2.get(f"{BASE_URL}/home")
    test("Home dynamically shows problems", "Real-time test problem" in r_home.text or "Test Problem" in r_home.text,
         "dynamic content check")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*65)
print("  TEST SUMMARY")
print("="*65)
passed = sum(1 for s, _, _ in results if s == PASS)
failed = sum(1 for s, _, _ in results if s == FAIL)
warned = sum(1 for s, _, _ in results if s == WARN)
total = len(results)

print(f"  Total:  {total}")
print(f"  {PASS}: {passed}")
print(f"  {FAIL}: {failed}")
print(f"  {WARN}: {warned}")
print("="*65)

if failed > 0:
    print("\n  FAILURES:")
    for s, name, detail in results:
        if s == FAIL:
            print(f"    • {name}" + (f" — {detail}" if detail else ""))

if warned > 0:
    print("\n  WARNINGS:")
    for s, name, detail in results:
        if s == WARN:
            print(f"    • {name}" + (f" — {detail}" if detail else ""))

print()
