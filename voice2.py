import pygame
import time


pygame.mixer.init()

# BGMの再生関数（重複して再生してもよい）
def play_bgm(file):
    if not pygame.mixer.music.get_busy():  # BGMが再生中でない場合
        # 音量を調整（0.0は無音、1.0は最大音量）
        pygame.mixer.music.set_volume(0.09)  # BGMの音量を50%
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(-1)  # -1でループ再生

# ボイスの再生関数（重複して再生しない）
def play_voice(file):
    # 音声が再生中なら停止
    pygame.mixer.stop()
    # 新しいボイスを再生
    voice = pygame.mixer.Sound(file)
    voice.play()

play_bgm("audio/BGM/maou_bgm_ethnic21.mp3")
time.sleep(5)

play_voice("audio/voice/add.wav")
time.sleep(2)

play_voice("audio/voice/start.wav")
time.sleep(7)

pygame.mixer.music.stop()

play_bgm("audio/BGM/maou_bgm_ethnic25.mp3")
time.sleep(5)

play_voice("audio/voice/add.wav")
time.sleep(3)

pygame.mixer.music.stop()