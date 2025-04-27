import cv2
import face_recognition
import os
import pandas as pd
from datetime import datetime
import pickle

# Folders i use 
attendance_folder = "attendanceSHEET"
faces_folder_path = "student_faces"
encodings_file = "encodings.pkl"

os.makedirs(attendance_folder, exist_ok=True)

# face encodings
known_face_encodings = []
known_face_names = []
known_roll_numbers = []

def save_encodings():
    for file_name in os.listdir(faces_folder_path):
        if file_name.endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(faces_folder_path, file_name)
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if encs:
                known_face_encodings.append(encs[0])
                name_roll = file_name.rsplit('.', 1)[0]
                parts = name_roll.split('_')
                name = "_".join(parts[:-1])
                roll = parts[-1]
                known_face_names.append(name)
                known_roll_numbers.append(roll)
            else:
                print(f"[!] No face found in {file_name}")
    with open(encodings_file, "wb") as f:
        pickle.dump((known_face_encodings, known_face_names, known_roll_numbers), f)

if os.path.exists(encodings_file):
    with open(encodings_file, "rb") as f:
        known_face_encodings, known_face_names, known_roll_numbers = pickle.load(f)
else:
    save_encodings()

# Excel Setup 
today_str = datetime.now().strftime("%Y-%m-%d")
excel_file = os.path.join(attendance_folder, f"{today_str}.xlsx")
if not os.path.exists(excel_file):
    pd.DataFrame(columns=["Name", "Roll Number", "Timestamp"]).to_excel(excel_file, index=False)

attendance_log = set()
counter = 0
frame_count = 0

# Camera 
video_capture = cv2.VideoCapture(0)
for _ in range(10):
    video_capture.read()

# GUI making
button_coords = {}
button_clicked = ""

def draw_rounded_rectangle(img, pt1, pt2, color, thickness, radius):
    x1, y1 = pt1
    x2, y2 = pt2
    if thickness < 0:
        cv2.rectangle(img, (x1+radius, y1), (x2-radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1+radius), (x2, y2-radius), color, -1)
        for cx, cy in [(x1+radius, y1+radius), (x2-radius, y1+radius), (x1+radius, y2-radius), (x2-radius, y2-radius)]:
            cv2.circle(img, (cx, cy), radius, color, -1)
    else:
        cv2.line(img, (x1+radius, y1), (x2-radius, y1), color, thickness)
        cv2.line(img, (x1+radius, y2), (x2-radius, y2), color, thickness)
        cv2.line(img, (x1, y1+radius), (x1, y2-radius), color, thickness)
        cv2.line(img, (x2, y1+radius), (x2, y2-radius), color, thickness)
        angles = [(180, 90), (270, 90), (90, 90), (0, 90)]
        centers = [(x1+radius, y1+radius), (x2-radius, y1+radius), (x1+radius, y2-radius), (x2-radius, y2-radius)]
        for (start, span), center in zip(angles, centers):
            cv2.ellipse(img, center, (radius, radius), start, 0, span, color, thickness)

def draw_button(frame, text, x, y, w, h, color):
    global button_coords
    button_coords[text] = (x, y, x + w, y + h)
    draw_rounded_rectangle(frame, (x, y), (x + w, y + h), color, -1, 20)
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = cv2.getTextSize(text, font, 0.6, 2)[0]
    text_x = x + (w - size[0]) // 2
    text_y = y + (h + size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y), font, 0.6, (255, 255, 255), 2)

def mouse_callback(event, x, y, flags, param):
    global button_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        for text, (x1, y1, x2, y2) in button_coords.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                button_clicked = text
                if text == "Show Attendance":
                    os.startfile(excel_file)

cv2.namedWindow("Attendance Camera")
cv2.setMouseCallback("Attendance Camera", mouse_callback)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 5 == 0:
        small = cv2.resize(frame, (0, 0), fx=0.20, fy=0.20)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        encs = face_recognition.face_encodings(rgb, locs)

        for enc, loc in zip(encs, locs):
            matches = face_recognition.compare_faces(known_face_encodings, enc)
            name, roll = "Unknown", ""

            if True in matches:
                idx = matches.index(True)
                name = known_face_names[idx]
                roll = known_roll_numbers[idx]

                if name not in attendance_log:
                    attendance_log.add(name)
                    counter += 1
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{name} (Roll No: {roll}) marked present at {ts}")
                    new_row = pd.DataFrame([[name, roll, ts]], columns=["Name", "Roll Number", "Timestamp"])
                    df = pd.read_excel(excel_file)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_excel(excel_file, index=False)

            top, right, bottom, left = [v * 5 for v in loc]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    # Buttons
    h, w, _ = frame.shape
    btn_w, btn_h, gap = 200, 50, 20
    x0 = (w - (3 * btn_w + 2 * gap)) // 2
    y = h - btn_h - 20

    draw_button(frame, "Show Attendance", x0, y, btn_w, btn_h, (255, 0, 0))
    draw_button(frame, "Close Application", x0 + btn_w + gap, y, btn_w, btn_h, (0, 0, 255))
    draw_button(frame, f"Present: {counter}", x0 + 2 * (btn_w + gap), y, btn_w, btn_h, (255, 0, 0))

    cv2.imshow("Attendance Camera", frame)
    if button_clicked == "Close Application" or cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
