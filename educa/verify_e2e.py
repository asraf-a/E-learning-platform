import os
import re
import urllib.request
import urllib.parse
import http.cookiejar

def get_csrf(html):
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
    return match.group(1) if match else None

# Cookie jar and opener
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING CHAPTER 10 & 11 VERIFICATION ===")

# 1. Check Public Course Catalog at Root
resp = opener.open('http://127.0.0.1:8000/')
assert resp.status == 200
catalog_html = resp.read().decode('utf-8')
assert 'All courses' in catalog_html
assert 'Programming' in catalog_html
assert 'Python for Beginners' in catalog_html
print("[PASS] Public course catalog at root '/' successfully rendered.")

# 2. Check Subject Filter
resp = opener.open('http://127.0.0.1:8000/course/subject/programming/')
assert resp.status == 200
subject_html = resp.read().decode('utf-8')
assert 'Programming courses' in subject_html
assert 'Python for Beginners' in subject_html
print("[PASS] Subject filtering by slug '/course/subject/programming/' verified.")

# 3. Check Public Course Overview (Anonymous)
resp = opener.open('http://127.0.0.1:8000/course/python-for-beginners/')
assert resp.status == 200
course_overview_html = resp.read().decode('utf-8')
assert 'Python for Beginners' in course_overview_html
assert 'Register to enroll' in course_overview_html
print("[PASS] Course overview page with 'Register to enroll' verified.")

# 4. Student Registration
resp = opener.open('http://127.0.0.1:8000/students/register/')
csrf = get_csrf(resp.read().decode('utf-8'))
student_user = f"newstudent_{os.urandom(3).hex()}"
reg_data = urllib.parse.urlencode({
    'username': student_user,
    'password1': 'Str0ngP@ssw0rd!123',
    'password2': 'Str0ngP@ssw0rd!123',
    'csrfmiddlewaretoken': csrf,
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/students/register/',
    data=reg_data,
    headers={'Referer': 'http://127.0.0.1:8000/students/register/'}
)
resp = opener.open(req)
assert resp.status == 200
reg_result_html = resp.read().decode('utf-8')
assert 'My courses' in reg_result_html
print(f"[PASS] Student registration for '{student_user}' completed and logged in.")

# 5. Course Enrollment as newly registered student
resp = opener.open('http://127.0.0.1:8000/course/python-for-beginners/')
overview_auth_html = resp.read().decode('utf-8')
assert 'Enroll now' in overview_auth_html
enroll_csrf = get_csrf(overview_auth_html)

# Extract course id from form
match_course = re.search(r'name=["\']course["\'] value=["\'](\d+)["\']', overview_auth_html)
course_id = match_course.group(1) if match_course else '1'

enroll_data = urllib.parse.urlencode({
    'course': course_id,
    'csrfmiddlewaretoken': enroll_csrf,
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/students/enroll-course/',
    data=enroll_data,
    headers={'Referer': 'http://127.0.0.1:8000/course/python-for-beginners/'}
)
resp = opener.open(req)
assert resp.status == 200
course_detail_html = resp.read().decode('utf-8')
assert 'Introduction to Python' in course_detail_html
assert 'Welcome to Python' in course_detail_html
print("[PASS] Course enrollment succeeded and redirected to course contents.")

# 6. Check Student Course List
resp = opener.open('http://127.0.0.1:8000/students/courses/')
assert resp.status == 200
student_list_html = resp.read().decode('utf-8')
assert 'Python for Beginners' in student_list_html
assert 'Access contents' in student_list_html
print("[PASS] Student enrolled courses list '/students/courses/' verified.")

# 7. Check Content Rendering (Text, Video, Images)
resp = opener.open(f'http://127.0.0.1:8000/students/course/{course_id}/')
assert resp.status == 200
contents_rendered_html = resp.read().decode('utf-8')
assert 'Welcome to Python' in contents_rendered_html
assert 'Python is a high-level, interpreted programming language.' in contents_rendered_html
# Video embed should be present
assert 'iframe' in contents_rendered_html or 'youtube' in contents_rendered_html
print("[PASS] Polymorphic content rendering (Text & Video embed) verified.")

# 8. Instructor CMS and AJAX reordering check
cj_inst = http.cookiejar.CookieJar()
opener_inst = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_inst))

login_resp = opener_inst.open('http://127.0.0.1:8000/accounts/login/')
login_csrf = get_csrf(login_resp.read().decode('utf-8'))
inst_data = urllib.parse.urlencode({
    'username': 'instructor',
    'password': 'password123',
    'csrfmiddlewaretoken': login_csrf,
    'next': '/course/mine/'
}).encode('utf-8')

inst_req = urllib.request.Request(
    'http://127.0.0.1:8000/accounts/login/',
    data=inst_data,
    headers={'Referer': 'http://127.0.0.1:8000/accounts/login/'}
)
resp = opener_inst.open(inst_req)
assert resp.status == 200
assert 'My courses' in resp.read().decode('utf-8')

# Reorder AJAX
req = urllib.request.Request(
    'http://127.0.0.1:8000/course/module/order/',
    data=b'{"1": 0, "2": 1, "3": 2}',
    headers={'Content-Type': 'application/json'}
)
resp = opener_inst.open(req)
assert resp.status == 200
assert b'"saved": "OK"' in resp.read()
print("[PASS] Instructor CMS and AJAX drag-and-drop ordering verified.")

# 9. Check Chat Room (Enrolled student)
chat_resp = opener.open(f'http://127.0.0.1:8000/chat/room/{course_id}/')
assert chat_resp.status == 200
chat_html = chat_resp.read().decode('utf-8')
assert 'Chat room for' in chat_html
assert 'chat-message-input' in chat_html
assert 'ws://' in chat_html
print("[PASS] Course real-time chat room view and WebSocket client verified.")

print("\n>>> ALL CHAPTER 10, 11, 12 & 13 VERIFICATIONS PASSED SUCCESSFULLY! <<<")
