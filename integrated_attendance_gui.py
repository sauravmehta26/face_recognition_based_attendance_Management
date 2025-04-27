import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import os
import numpy as np
from PIL import Image
from datetime import datetime
import csv

# Create necessary folders
if not os.path.exists("student_faces"):
    os.makedirs("student_faces")
if not os.path.exists("attendanceSHEET"):
    os.makedirs("attendanceSHEET")

root = tk.Tk()
root.title("Face Recognition Based Attendance System")
root.geometry("900x500")
root.configure(bg="#2c4c4c")

# Global variables
name_var = tk.StringVar()
roll_var = tk.StringVar()
registration_count = tk.IntVar(value=len(os.listdir("student_faces")))

# Layout frames
left_frame = tk.Frame(root, bg="white", padx=20, pady=20)
right_frame = tk.Frame(root, bg="white", padx=20, pady=20)
left_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="right", fill="both", expand=True)

# Register New Student Section
tk.Label(left_frame, text="Register New Student", bg="black", fg="white", font=("Helvetica", 14)).pack(fill="x")

tk.Label(left_frame, text="Enter ID", bg="white", anchor="w").pack(fill="x", pady=(10, 0))
entry_roll = tk.Entry(left_frame, textvariable=roll_var)
entry_roll.pack(fill="x")

tk.Label(left_frame, text="Enter Name", bg="white", anchor="w").pack(fill="x", pady=(10, 0))
entry_name = tk.Entry(left_frame, textvariable=name_var)
entry_name.pack(fill="x")

def clear_inputs():
    name_var.set("")
    roll_var.set("")

tk.Button(left_frame, text="Clear", bg="blue", fg="white", command=clear_inputs).pack(pady=(10, 0))

tk.Label(left_frame, text="Follow the steps...\n1)Take Images  ===>  2)Save Profile", bg="white").pack(pady=10)

def take_images():
    roll = roll_var.get()
    name = name_var.get()
    if not roll or not name:
        messagebox.showerror("Error", "Please enter both Name and ID")
        return

    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            return img[y:y+h, x:x+w]

    cap = cv2.VideoCapture(0)
    img_id = 0

    def capture_frame():
        nonlocal img_id
        ret, my_frame = cap.read()
        if face_cropped(my_frame) is not None:
            img_id += 1
            face = cv2.resize(face_cropped(my_frame), (450, 450))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            file_name_path = f"student_faces/{name}_{roll}_{img_id}.jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Cropped Face", face)
        if img_id < 20:
            root.after(100, capture_frame)  # Call capture_frame every 100 ms

    capture_frame()  # Start the capture loop
    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Result", "Images Saved Successfully")
    registration_count.set(len(os.listdir("student_faces")))


    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            return img[y:y+h, x:x+w]

    cap = cv2.VideoCapture(0)
    img_id = 0

    while True:
        ret, my_frame = cap.read()
        if face_cropped(my_frame) is not None:
            img_id += 1
            face = cv2.resize(face_cropped(my_frame), (450, 450))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            file_name_path = f"student_faces/{name}_{roll}_{img_id}.jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Cropped Face", face)
        if cv2.waitKey(1) == 13 or img_id == 20:
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Result", "Images Saved Successfully")
    registration_count.set(len(os.listdir("student_faces")))

tk.Button(left_frame, text="Take Images", bg="deepskyblue", command=take_images).pack(pady=5)

def save_profile():
    name = name_var.get()
    roll = roll_var.get()
    if not name or not roll:
        messagebox.showerror("Error", "Please enter Name and ID")
        return
    messagebox.showinfo("Saved", "Student Profile Saved")

tk.Button(left_frame, text="Save Profile", bg="deepskyblue", command=save_profile).pack(pady=5)
tk.Label(left_frame, textvariable=registration_count, text="Total Registrations", bg="white").pack(pady=5)

# Attendance Section
tk.Label(right_frame, text="Mark Student's attendance", bg="black", fg="white", font=("Helvetica", 14)).pack(fill="x")
tk.Button(right_frame, text="Take Attendance", bg="deepskyblue").pack(pady=10)

columns = ("ID", "Name", "Date", "Time")
tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")
tree.pack(pady=10, fill="x")

tk.Button(right_frame, text="Quit", bg="blue", fg="white", command=root.destroy).pack(pady=5)

root.mainloop()
