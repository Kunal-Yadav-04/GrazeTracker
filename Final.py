import cv2
import numpy as np
import time
from gpiozero import DigitalInputDevice
from pynput.mouse import Button, Controller

# Initialize mouse controller
mouse = Controller()

# Initialize IR sensors
left_sensor = DigitalInputDevice(17)  # GPIO 17 (Pin 11) for left eye
right_sensor = DigitalInputDevice(27)  # GPIO 27 (Pin 13) for right eye

# OpenCV face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Screen resolution (adjust as per your monitor)
screen_width, screen_height = 1920, 1080  # Best resolution for accuracy

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set high-resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Variables for head movement detection
prev_x, prev_y = 0, 0  # Previous head position
smoothing_factor = 1.5  # Balanced smoothing for cursor movement

# Variables for blink detection
left_blink_start_time = 0
right_blink_start_time = 0
blink_threshold = 1  # 1 second to differentiate between natural and intentional blink
debounce_delay = 0.5  # 0.5-second debounce delay to prevent false clicks

# Function to map head position to screen coordinates
def map_head_to_screen(head_x, head_y, frame_width, frame_height):
    screen_x = np.interp(head_x, [0, frame_width], [0, screen_width])
    screen_y = np.interp(head_y, [0, frame_height], [0, screen_height])
    return int(screen_x), int(screen_y)

# Main loop
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Calculate the center of the face
            head_center_x = x + w // 2
            head_center_y = y + h // 2

            # Map head position to screen coordinates
            mouse_x, mouse_y = map_head_to_screen(head_center_x, head_center_y, frame.shape[1], frame.shape[0])

            # Smooth the cursor movement
            mouse_x = prev_x + (mouse_x - prev_x) / smoothing_factor
            mouse_y = prev_y + (mouse_y - prev_y) / smoothing_factor

            # Move the mouse cursor
            mouse.position = (mouse_x, mouse_y)

            # Update previous head position
            prev_x, prev_y = mouse_x, mouse_y

        # Blink detection for left eye (left mouse button)
        if not left_sensor.value:  # Left eye blink detected
            if left_blink_start_time == 0:
                left_blink_start_time = time.time()
            else:
                if time.time() - left_blink_start_time >= blink_threshold:
                    print("Left eye intentional blink detected - performing left mouse click")
                    mouse.click(Button.left, 1)  # Left mouse click
                    left_blink_start_time = 0
                    time.sleep(debounce_delay)  # Debounce delay
        else:
            left_blink_start_time = 0

        # Blink detection for right eye (right mouse button)
        if not right_sensor.value:  # Right eye blink detected
            if right_blink_start_time == 0:
                right_blink_start_time = time.time()
            else:
                if time.time() - right_blink_start_time >= blink_threshold:
                    print("Right eye intentional blink detected - performing right mouse click")
                    mouse.click(Button.right, 1)  # Right mouse click
                    right_blink_start_time = 0
                    time.sleep(debounce_delay)  # Debounce delay
        else:
            right_blink_start_time = 0

        # Display the frame
        cv2.imshow("Head and Eye Control", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

