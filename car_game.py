import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk, ImageFont
import cv2
import numpy as np
import os
from ultralytics import YOLO
from rembg import remove

class BlockGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Game")

        # Initial setup
        self.current_screen = "main"
        self.blocknumber = None
        self.sample_image_path = None
        self.last_frame = None
        self.frame_count = 0
        self.captured_images = {"house": None, "cars": None}  # Store captured images for house and cars
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            messagebox.showerror("Error", "Cannot access the camera")
            root.destroy()

        # Load YOLO model
        self.model = YOLO('bestbest.pt')

        # Output directory for processed images
        self.output_dir = "output_images"
        os.makedirs(self.output_dir, exist_ok=True)

        # Main canvas
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        # Load background image
        try:
            self.bg_image = Image.open("image/town.jpg")
            self.bg_image = self.bg_image.resize((800, 600))
            self.bg_tk = ImageTk.PhotoImage(self.bg_image)
        except Exception as e:
            print(f"Background image error: {e}")
            self.bg_tk = None

        # Draw the initial screen
        self.draw_main_screen()

        # Mouse click event
        self.canvas.bind("<Button-1>", self.mouse_event)

        # Frame update
        self.update_frame()

    def draw_main_screen(self):
        self.canvas.delete("all")
        self.current_screen = "main"

        # Draw background image
        if self.bg_tk:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_tk)

        # Text
        self.canvas.create_text(400, 50, text="Lego Game", font=("Helvetica", 24), fill="black")
        self.canvas.create_text(400, 100, text="作りたいものをクリックしてください", font=font_subject, fill="black")

        # Buttons
        self.canvas.create_rectangle(200, 200, 400, 250, fill="lightblue", outline="black", tags="house")
        self.canvas.create_text(300, 225, text="家", font=font_subject, fill="black")

        self.canvas.create_rectangle(200, 300, 400, 350, fill="lightgreen", outline="black", tags="cars")
        self.canvas.create_text(300, 325, text="車", font=font_subject, fill="black")

        # Display captured images
        if self.captured_images["house"]:
            house_image = Image.open(self.captured_images["house"])
            house_image.thumbnail((50, 50))
            house_tk = ImageTk.PhotoImage(house_image)
            self.canvas.create_image(420, 225, anchor=tk.CENTER, image=house_tk)
            self.house_image_tk = house_tk  # Keep reference

        if self.captured_images["cars"]:
            cars_image = Image.open(self.captured_images["cars"])
            cars_image.thumbnail((50, 50))
            cars_tk = ImageTk.PhotoImage(cars_image)
            self.canvas.create_image(420, 325, anchor=tk.CENTER, image=cars_tk)
            self.cars_image_tk = cars_tk  # Keep reference

    def draw_next_screen(self):
        self.canvas.delete("all")
        self.current_screen = "next"

        # Display camera feed on the right
        if self.last_frame is not None:
            frame_rgb = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame_rgb)
            frame_image = frame_image.resize((300, 300))
            frame_tk = ImageTk.PhotoImage(image=frame_image)
            self.canvas.create_image(550, 200, anchor=tk.CENTER, image=frame_tk)
            self.image_tk = frame_tk  # Keep reference

        # Sample image
        if self.blocknumber == 0:
            self.sample_image_path = "image/house.jpg"
        elif self.blocknumber == 1:
            self.sample_image_path = "image/car.jpg"

        try:
            sample_image = Image.open(self.sample_image_path)
            sample_image.thumbnail((300, 300))
            sample_tk = ImageTk.PhotoImage(sample_image)
            self.canvas.create_image(250, 200, anchor=tk.CENTER, image=sample_tk)
            self.sample_image_tk = sample_tk  # Keep reference
        except Exception as e:
            print(f"Sample image error: {e}")

        # Shutter button
        self.canvas.create_rectangle(300, 400, 500, 450, fill="red", outline="black", tags="shutter")
        self.canvas.create_text(400, 425, text="撮影", font=font_subject, fill="white")

        # Back to main button (left bottom)
        self.canvas.create_rectangle(10, 500, 250, 550, fill="blue", outline="black", tags="back_to_main")
        self.canvas.create_text(125, 525, text="メイン画面に戻る", font=font_subject, fill="white")

        # Message area
        self.message_id = self.canvas.create_text(400, 500, text="", font=("Helvetica", 14), fill="red")

    def mouse_event(self, event):
        x, y = event.x, event.y

        if self.current_screen == "main":
            if 200 <= x <= 400 and 200 <= y <= 250:
                self.blocknumber = 0
                self.draw_next_screen()
            elif 200 <= x <= 400 and 300 <= y <= 350:
                self.blocknumber = 1
                self.draw_next_screen()

        elif self.current_screen == "next":
            if 300 <= x <= 500 and 400 <= y <= 450:
                self.capture_shutter()
            elif 50 <= x <= 200 and 500 <= y <= 550:
                self.draw_main_screen()  # メインページに戻る


    def capture_shutter(self):
        if self.last_frame is not None:
            filename = f"captured_image_{self.blocknumber}.jpg"
            cv2.imwrite(filename, self.last_frame)
            print(f"Image saved: {filename}")

            # YOLOモデルの適用
            results = self.model(filename)

            # 信頼値のしきい値
            confidence_threshold = 0.5  # ここでしきい値を設定

            if results and len(results[0].boxes) > 0:
                detected = False  # 検出結果の確認用

                for i, box in enumerate(results[0].boxes.xyxy):
                    confidence = results[0].boxes.conf[i]  # 信頼値を取得
                    if confidence < confidence_threshold:
                        continue  # 信頼値がしきい値以下の場合はスキップ

                    x1, y1, x2, y2 = map(int, box.tolist())
                    label_index = int(results[0].boxes.cls[i])  # クラスIDを取得
                    object_type = self.model.names[label_index]  # クラス名を取得
                    print(f"Detected object: {object_type} with confidence: {confidence}")

                    # ブロックナンバーに対応するオブジェクトかどうかを確認
                    if (self.blocknumber == 0 and object_type != "house") or \
                    (self.blocknumber == 1 and object_type != "cars"):
                        continue  # 対応しない場合はスキップ

                    detected = True  # 検出成功

                    # 検出されたオブジェクトを切り抜き
                    cropped = Image.open(filename).crop((x1, y1, x2, y2))

                    # 背景を削除
                    temp_path = os.path.join(self.output_dir, f"temp_{object_type}_{i}.jpg")
                    cropped.save(temp_path, "JPEG")
                    with open(temp_path, "rb") as input_file:
                        output_data = remove(input_file.read())
                    output_path = os.path.join(self.output_dir, f"result_{object_type}_{i}.png")
                    with open(output_path, "wb") as output_file:
                        output_file.write(output_data)

                    # 検出結果を保存
                    self.captured_images[object_type] = output_path

                if detected:
                    self.draw_main_screen()
                else:
                    self.canvas.itemconfig(self.message_id, text="Please capture a valid object!")
            else:
                self.canvas.itemconfig(self.message_id, text="No objects detected!")

    def update_frame(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.frame_count += 1
                if self.frame_count % 5 == 0:  # Update every 5 frames
                    self.last_frame = frame

                    if self.current_screen == "next":
                        frame_rgb = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
                        frame_image = Image.fromarray(frame_rgb)
                        frame_image = frame_image.resize((300, 300))
                        frame_tk = ImageTk.PhotoImage(image=frame_image)
                        self.canvas.create_image(550, 200, anchor=tk.CENTER, image=frame_tk)
                        self.image_tk = frame_tk  # Keep reference

        self.root.after(10, self.update_frame)

    def on_close(self):
        # リソース解放
        self.capture.release()

        # captured_image_0.jpg と captured_image_1.jpg を削除
        for i in range(2):
            filename = f"captured_image_{i}.jpg"
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"Deleted: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

        self.root.destroy()
# Main loop
root = tk.Tk()

# tkinter用のフォントを指定
font_subject = font.Font(family="ＭＳ ゴシック", size=20)

app = BlockGameApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
