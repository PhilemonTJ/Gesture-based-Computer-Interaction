import cv2
import numpy as np
import threading
import time
import mouse
import os
import pyautogui
import winsound

from utils.hand_detector import HandDetector
from utils.button import TextButton

def main():
    detector = HandDetector(detectionCon=0.9, maxHands=1)

    cap = cv2.VideoCapture(0)
    cam_width, cam_height, cam_fps = 640, 480, 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
    cap.set(cv2.CAP_PROP_FPS, cam_fps)

    screen_width, screen_height = pyautogui.size()

    frameR = 120  # Increased Frame Reduction for better edge handling
    rect_height = 240
    rect_x1, rect_y1 = 120, 20
    rect_x2, rect_y2 = cam_width - rect_x1, rect_height + rect_y1

    # Mouse smoothing variables
    smoothening = 5
    prev_x, prev_y = 0, 0
    curr_x, curr_y = 0, 0

    # Delay for the mouse to move
    l_delay = 0 
    r_delay = 0

    # Screenshot gesture state
    SCREENSHOT_IDLE = 0
    SCREENSHOT_FIST = 1
    SCREENSHOT_OPEN = 23

    screenshot_state = SCREENSHOT_IDLE
    screenshot_timer = 0
    SCREENSHOT_TIMEOUT = 2.0
    SCREENSHOT_COOLDOWN = 3.0
    last_screenshot_time = 0

    os.makedirs("screenshots", exist_ok=True)

    def l_clk_delay():
        nonlocal l_delay, l_clk_thread
        time.sleep(1) # Delay for the mouse to move
        l_delay = 0
        l_clk_thread = threading.Thread(target=l_clk_delay)

    def r_clk_delay():
        nonlocal r_delay, r_clk_thread
        time.sleep(1) # Delay for the mouse to move
        r_delay = 0
        r_clk_thread = threading.Thread(target=r_clk_delay)

    l_clk_thread = threading.Thread(target=l_clk_delay)
    r_clk_thread = threading.Thread(target=r_clk_delay)

    # Create buttons
    button_start_y = cam_height - frameR + 5
    button_gap_y = 40

    buttons = [
        TextButton("Mouse Moving", 10, button_start_y),
        TextButton("Mouse Lock", 200, button_start_y),
        TextButton("Left Click", 10, button_start_y + button_gap_y),
        TextButton("Right Click", 200, button_start_y + button_gap_y),
        TextButton("Double Click", 390, button_start_y + button_gap_y),
        TextButton("Scroll Up", 10, button_start_y + 2 * button_gap_y),
        TextButton("Scroll Down", 200, button_start_y + 2 * button_gap_y),
        TextButton("Screenshot", 390, button_start_y + 2 * button_gap_y)
    ]

    def reset_buttons():
        for button in buttons:
            if button.active_until == 0:  # Only reset if not in timed active state
                button.is_active = False

    def is_fist(fingers):
        return fingers == [1, 0, 0, 0, 0]
    
    def is_open_palm(fingers):
        return fingers == [0, 1, 1, 1, 1]
    
    def play_screenshot_sound():
        winsound.Beep(1200, 150)

    def flash_feedback(img):
        flash = np.full_like(img, 255)
        return cv2.addWeighted(img, 0.3, flash, 0.7, 0)

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to grab frame")
                break

            img = cv2.flip(img, 1)
            hands, img = detector.findHands(img, flipType=False)
            
            # Reset all buttons to default state
            reset_buttons()
            
            cv2.rectangle(img, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 0, 0), 2)

            if hands:
                lmlist = hands[0]["lmList"]
                ind_x, ind_y = lmlist[8][0], lmlist[8][1]
                mid_x, mid_y = lmlist[12][0], lmlist[12][1]

                cv2.circle(img, (ind_x, ind_y), 10, (0, 255, 0), cv2.FILLED)
                fingers = detector.fingersUp(hands[0])

                current_time = time.time()
                if current_time - last_screenshot_time > SCREENSHOT_COOLDOWN:
                    if screenshot_state == SCREENSHOT_IDLE:
                        if is_fist(fingers):
                            screenshot_state = SCREENSHOT_FIST
                            screenshot_timer = current_time

                    elif screenshot_state == SCREENSHOT_FIST:
                        if current_time - screenshot_timer > SCREENSHOT_TIMEOUT:
                            screenshot_state = SCREENSHOT_IDLE
                        elif is_open_palm(fingers):
                            screenshot_state = SCREENSHOT_OPEN

                    elif screenshot_state == SCREENSHOT_OPEN:
                        if current_time - screenshot_timer > SCREENSHOT_TIMEOUT:
                            screenshot_state = SCREENSHOT_IDLE
                        elif is_fist(fingers):
                            filename = f"screenshots/screenshot_{int(time.time())}.png"
                            screenshot = pyautogui.screenshot()
                            screenshot.save(filename)
                            play_screenshot_sound()
                            img = flash_feedback(img)
                            buttons[7].set_active(1.0)
                            print(f"Screenshot saved: {filename}")
                            last_screenshot_time = current_time
                            screenshot_state = SCREENSHOT_IDLE

                # Reset moving and lock buttons
                buttons[0].is_active = False
                buttons[1].is_active = False
                # fingers [thumb, index, middle, ring, pinky]
                # Mouse Movement
                if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:
                    buttons[0].is_active = True  # Mouse Moving - instant state
                    converted_x = np.interp(ind_x, [rect_x1, rect_x2], [0, screen_width])
                    converted_y = np.interp(ind_y, [rect_y1, rect_y2], [0, screen_height])
                    
                    curr_x = prev_x + (converted_x - prev_x) / smoothening
                    curr_y = prev_y + (converted_y - prev_y) / smoothening
                    
                    curr_x = max(0, min(curr_x, screen_width))
                    curr_y = max(0, min(curr_y, screen_height))
                    
                    mouse.move(int(curr_x), int(curr_y))
                    prev_x, prev_y = curr_x, curr_y
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                    buttons[1].is_active = True  # Mouse Lock - instant state
                    
                # Mouse Click actions
                if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                    length, _, img = detector.findDistance((ind_x, ind_y), (mid_x, mid_y), img)
                    if length < 40:
                        if fingers[3] == 0 and fingers[4] == 0 and l_delay == 0:
                            buttons[2].set_active()  # Left Click
                            mouse.click(button='left')
                            l_delay = 1
                            l_clk_thread.start()
                        elif fingers[3] == 1 and fingers[4] == 0 and r_delay == 0:
                            buttons[3].set_active()  # Right Click
                            mouse.click(button='right')
                            r_delay = 1
                            r_clk_thread.start()
                        elif fingers[3] == 0 and fingers[4] == 1:
                            buttons[4].set_active()  # Double Click
                            mouse.double_click(button='left')
                            
                # Scroll actions
                if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0:
                    length, _, img = detector.findDistance((ind_x, ind_y), (mid_x, mid_y), img)
                    if length < 30:
                        if fingers[4] == 1:
                            buttons[5].set_active()  # Scroll Up
                            mouse.wheel(delta=1)
                        else:
                            buttons[6].set_active()  # Scroll Down
                            mouse.wheel(delta=-1)
            
            # Draw all buttons
            for button in buttons:
                button.draw(img)

            #Camera Feed
            cv2.imshow("AI Mouse - Camera Feed", img)
            key = cv2.waitKey(1)
            if key & 0xFF in [27, ord('q')]:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()