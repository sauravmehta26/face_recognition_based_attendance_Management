import cv2
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

# Folder to save faces
faces_folder = "student_faces"
if not os.path.exists(faces_folder):
    os.makedirs(faces_folder)

# Function to prompt user for Name and Roll Number
def get_student_info():
    # Create the Tkinter root window and hide it
    root = tk.Tk()
    root.title("Add Student")

    # Heading Label
    heading_label = tk.Label(root, text="Add Student", font=("Helvetica", 14), pady=10)
    heading_label.grid(row=0, column=0, columnspan=2)

    # Name input field
    name_label = tk.Label(root, text="Name:")
    name_label.grid(row=1, column=0, sticky="e", padx=10)
    name_entry = tk.Entry(root, width=25)
    name_entry.grid(row=1, column=1)

    # Roll number input field
    roll_label = tk.Label(root, text="Roll Number:")
    roll_label.grid(row=2, column=0, sticky="e", padx=10)
    roll_entry = tk.Entry(root, width=25)
    roll_entry.grid(row=2, column=1)

    # Variable to hold student info
    student_info = None

    # Function to collect values and close the dialog
    def submit():
        nonlocal student_info
        name = name_entry.get().strip()
        roll_number = roll_entry.get().strip()
        if name and roll_number:
            student_info = f"{name}_{roll_number}"
            root.quit()  # Close the window and continue the program
        else:
            messagebox.showerror("Input Error", "❌ Both fields are required!")
            student_info = None

    # Submit button
    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Run the Tkinter loop until valid input is submitted
    root.mainloop()

    return student_info

# Ask for name and roll before starting the camera
student_info = get_student_info()

if student_info:
    filename = f"{student_info}.jpg"
    file_path = os.path.join(faces_folder, filename)

    # Load OpenCV's pre-trained face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Start webcam
    cap = cv2.VideoCapture(0)
    print("📸 Please position yourself in front of the camera.")

    captured_image = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access the camera.")
            break

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # If a face is detected, capture the image and save it
        if len(faces) > 0:
            # Draw rectangle around the first face detected
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Crop the face region
            face_roi = frame[y:y+h, x:x+w]
            captured_image = face_roi
            cv2.putText(frame, "Face Detected, Capturing...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Save the image and close the app after capturing
            cv2.imwrite(file_path, captured_image)
            messagebox.showinfo("Success", f"✅ Student image saved as {filename}")
            print(f"✅ Saved to {file_path}")
            break

        # Display the video feed
        cv2.imshow("Capture Student Face", frame)

        # Press 'q' to quit without capturing
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Capture canceled.")
            break

    cap.release()
    cv2.destroyAllWindows()

else:
    print("❌ Invalid or incomplete input.")
