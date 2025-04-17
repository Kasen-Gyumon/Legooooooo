import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk, ImageFont
import cv2
import numpy as np
import os
from ultralytics import YOLO
from rembg import remove
import pygame

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
        self.capture = cv2.VideoCapture(1)

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

    def update_background_image(self):
    
        if self.captured_images["house"] and self.captured_images["cars"]:
            background_path = "image/house_car_less.jpg"
        elif self.captured_images["house"]:
            background_path = "image/house_less.jpg"
        elif self.captured_images["cars"]:
            background_path = "image/car_less.jpg"
        else:
            background_path = "image/town.jpg"  # 初期背景

        try:
            new_bg_image = Image.open(background_path)
            new_bg_image = new_bg_image.resize((800, 600))
            self.bg_tk = ImageTk.PhotoImage(new_bg_image)
        except Exception as e:
            print(f"Error updating background image: {e}")
            self.bg_tk = None


    def draw_main_screen(self):
        global tome_car, tome_home

        self.update_background_image()
        self.canvas.delete("all")
        self.current_screen = "main"

        # Draw background image
        if self.bg_tk:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_tk)

        # Text
        self.canvas.create_text(400, 30, text="Legoooooo", font=("Helvetica", 24), fill="black")
        self.canvas.create_text(420, 70, text="まちをかんせいさせよう！", font=font_subject, fill="black")

        # Buttons and images
        # House button
        if self.captured_images["house"]:
            # Display captured house image
            house_image = Image.open(self.captured_images["house"])
            house_image = house_image.resize((300, 350))  # Match button size
            house_tk = ImageTk.PhotoImage(house_image)
            self.canvas.create_image(420, 265+30, anchor=tk.CENTER, image=house_tk)
            self.house_image_tk = house_tk  # Keep reference

            # Transparent button overlay
            self.canvas.create_rectangle(270, 90, 570, 440, fill="", outline="", tags="house")

        else:
            # Draw house button (visible if no image yet)
            self.canvas.create_rectangle(270, 90, 570, 440, fill="#ADD8E6", outline="black", stipple="gray50", tags="house")
            self.canvas.create_text(415, 290, text="🏠️おうち", font=font_title2, fill="black")

        # Car button
        if self.captured_images["cars"]:
            # Display captured car image
            cars_image = Image.open(self.captured_images["cars"])
            cars_image = cars_image.resize((260, 120))  # Match button size
            cars_tk = ImageTk.PhotoImage(cars_image)
            self.canvas.create_image(370, 520, anchor=tk.CENTER, image=cars_tk)
            self.cars_image_tk = cars_tk  # Keep reference

            # Transparent button overlay
            self.canvas.create_rectangle(240, 440, 500, 560, fill="", outline="", tags="cars")

        else:
            # Draw car button (visible if no image yet)
            self.canvas.create_rectangle(240, 440, 500, 560, fill="#90EE90", outline="black", stipple="gray50", tags="cars")
            self.canvas.create_text(360, 495, text="🚗くるま", font=font_title2, fill="black")

    def draw_next_screen(self):
        self.canvas.delete("all")
        self.current_screen = "next"

        # 背景画像として Sam.jpg を表示
        try:
            bg_image = Image.open("sample.jpg")
            bg_image = bg_image.resize((800, 600))  # キャンバスサイズに合わせてリサイズ
            bg_tk = ImageTk.PhotoImage(bg_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=bg_tk)
            self.bg_next_screen_tk = bg_tk  # 参照を保持
        except Exception as e:
            print(f"Error loading Sam.jpg: {e}")
        self.canvas.create_text(400, 30, text="ひだりのおてほんとおなじものをつくってね", font=font_subject, fill="black")
        if self.blocknumber == 0:
            self.canvas.create_text(240, 80, text="まえからとってね！", font=font_subject, fill="black")
        elif self.blocknumber == 1:
            self.canvas.create_text(240, 80, text="よこむきにとってね！", font=font_subject, fill="black")

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
            self.sample_image_path = "image/house.png"
            imageSizeX = 300 
            imageSizeY = 300

        elif self.blocknumber == 1:
            self.sample_image_path = "image/car.png"
            imageSizeX = 400 
            imageSizeY = 400

        try:
            sample_image = Image.open(self.sample_image_path)
            sample_image.thumbnail((imageSizeX,imageSizeY))

            # Create frame around the sample image
            x1, y1, x2, y2 = 150, 100, 350, 300
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=4)

            # Place the sample image within the frame
            sample_tk = ImageTk.PhotoImage(sample_image)
            self.canvas.create_image((x1 + x2) // 2, (y1 + y2) // 2, anchor=tk.CENTER, image=sample_tk)
            self.sample_image_tk = sample_tk  # Keep reference

        except Exception as e:
            print(f"Sample image error: {e}")

        # Shutter button
        self.canvas.create_rectangle(300, 400, 500, 450, fill="red", outline="black", tags="shutter")
        self.canvas.create_text(400, 425, text="しゃしん", font=font_subject, fill="white")

        # Back to main button (left bottom)
        self.canvas.create_rectangle(10, 500, 250, 550, fill="blue", outline="black", tags="back_to_main")
        self.canvas.create_text(125, 525, text="さいしょにもどる", font=font_subject, fill="white")

        # Message area
        self.message_id = self.canvas.create_text(400, 500, text="", font=("Helvetica", 14), fill="red")

    def mouse_event(self, event):
        x, y = event.x, event.y

        if self.current_screen == "main":
            if 270 <= x <= 570 and 90 <= y <= 440:
                self.blocknumber = 0#house選択
                self.draw_next_screen()
            elif 240 <= x <= 500 and 440 <= y <= 560:
                self.blocknumber = 1#car選択
                self.draw_next_screen()

        elif self.current_screen == "next":
            if 300 <= x <= 500 and 400 <= y <= 450:
                self.capture_shutter()
            elif 50 <= x <= 200 and 500 <= y <= 550:
                self.draw_main_screen()  # メインページに戻る

    def capture_shutter(self):
        global tome_home, tome_car
        if self.last_frame is not None:
            filename = f"captured_image_{self.blocknumber}.jpg"
            cv2.imwrite(filename, self.last_frame)
            print(f"Image saved: {filename}")

            # YOLOモデルの適用
            results = self.model(filename)

            # 信頼値のしきい値
            confidence_threshold = 0.3  # ここでしきい値を設定

            if results and len(results[0].boxes) > 0:
                detected = False  # 検出結果の確認用
                self.canvas.itemconfig(self.message_id, text="すこしまってね")

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

                    #ボタンの透過度を変更
                    if (self.blocknumber == 0 and object_type == "house"):
                        tome_home ="gray25"

                    if (self.blocknumber == 1 and object_type == "car"):
                        tome_car ="gray25"

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

                    trimmed_output_path = os.path.join(self.output_dir, f"trimmed_{object_type}_{i}.png")

                    # 透過部分をトリミング
                    if self.trim_transparent_area(output_path, trimmed_output_path):
                        # トリミング後の画像パスを保存    
                        self.captured_images[object_type] = output_path
                    # トリミング後の画像パスを保存
                        self.captured_images[object_type] = trimmed_output_path
                    else:
                        print(f"Trimming failed for {output_path}")
                if detected:
                    self.draw_main_screen()
                else:#物体は検知されているが、対象の物体がないor精度が低すぎる
                    self.canvas.itemconfig(self.message_id, text="あとちょっと！")
            else:#そもそも物体がない
                self.canvas.itemconfig(self.message_id, text="みつからないよ～")

    def trim_transparent_area(self, input_path, output_path):
        """
        PNG画像の透過部分をトリミングし、物体ができるだけ大きくなるように画像の端に配置します。
        
        Args:
            input_path (str): トリミング対象の画像パス。
            output_path (str): トリミング後の画像を保存するパス。
            
        Returns:
            bool: トリミングが成功した場合はTrue、失敗した場合はFalse。
        """
        try:
            # 入力画像を開く
            img = Image.open(input_path).convert("RGBA")
            
            # アルファチャンネルを使って非透過部分の範囲を取得
            bbox = img.getbbox()

            if bbox:
                # 物体部分が画像の端に触れるように画像を拡大
                img_cropped = img.crop(bbox)
                
                # 新しい画像サイズを設定（物体が画像端に触れるように）
                img_width, img_height = img_cropped.size
                new_img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

                # 物体を新しい画像内で最適に配置
                new_img.paste(img_cropped, (0,0), img_cropped)  # 物体を画像の左上に配置
                
                # 保存
                new_img.save(output_path, "PNG")
                print(f"Trimmed and enlarged image saved: {output_path}")
                return True
            else:
                print("No non-transparent pixels found in the image.")
                return False

        except Exception as e:
            print(f"Error trimming transparent image: {e}")
            return False

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
font_title = font.Font(family="ＭＳ ゴシック", size=50)
font_title2 = font.Font(family="ＭＳ ゴシック", size=30)
font_subject = font.Font(family="ＭＳ ゴシック", size=20)
tome_home ="gray75"
tome_car ="gray75"

app = BlockGameApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
