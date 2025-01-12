import cv2
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Viewer")

        # VideoCaptureを初期化
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            raise RuntimeError("カメラを開けませんでした。")

        self.frame_count = 0

        # Tkinterウィジェット
        self.label = Label(root)
        self.label.pack()

        self.close_button = Button(root, text="終了", command=self.close)
        self.close_button.pack()

        # 初期フレームの表示を開始
        self.update_frame()

    def update_frame(self):
        # フレームカウントをインクリメント
        self.frame_count += 1

        # フレームを5フレームごとに更新
        if self.frame_count % 5 == 0:
            ret, frame = self.cap.read()
            if ret:
                # OpenCVのBGR画像をPillow用のRGB画像に変換
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image_tk = ImageTk.PhotoImage(image)

                # Tkinterラベルに画像を設定
                self.label.imgtk = image_tk
                self.label.configure(image=image_tk)

        # 次のフレーム更新をスケジュール
        self.root.after(10, self.update_frame)

    def close(self):
        # リソース解放
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = CameraApp(root)
    root.mainloop()
