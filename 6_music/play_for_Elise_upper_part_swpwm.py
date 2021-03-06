import RPi.GPIO as GPIO
import re
import time

PIN = 12

TEMPO = 60  # テンポ（1分あたりの四分音符の数）
DURATION_PER_NOTE = 60 / TEMPO  # 4分音符1つあたりの発音時間

# 楽譜（音名と音の分割数の組のリストからなる。例えば、16は16分音符を意味する。）
UPPER_PART = [
    ["e5",16],["e-5",16],
    ["e5",16],["e-5",16],["e5",16],["b4",16],["d5",16],["c5",16],
    ["a4",8],["r",16],["c4",16],["e4",16],["a4",16],
    ["b4",8],["r",16],["e4",16],["a-4",16],["b4",16],
    ["c5",8],["r",16],["e4",16],["e5",16],["e-5",16],
    ["e5",16],["e-5",16],["e5",16],["b4",16],["d5",16],["c5",16],
    ["a4",8],["r",16],["c4",16],["e4",16],["a4",16],
    ["b4",8],["r",16],["e4",16],["c5",16],["b4",16],
    ["a4",4]
]

NOTE_DIFF = {"c":  -9, "c+": -8, "d-": -8, "d":  -7, "d+": -6,
             "e-": -6, "e":  -5, "f":  -4, "f+": -3, "g-": -3,
             "g":  -2, "g+": -1, "a-": -1, "a":   0, "a+":  1,
             "b-": 1, "b": 2, "r": None}

note_pattern = re.compile(r"^([a-gr])(\+|\-)?(\d+)?", re.IGNORECASE)
TUNING = 440  # 基準となるオクターブ4の「ラ」の周波数


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

def play_tone(p,tone):
    note_match = note_pattern.search(tone[0])
    (note_code, accidential, octave) = note_match.groups()
    #print((note_code, accidential, octave))
    note_acc = note_code + (accidential if accidential else "")  # シャープやフラットの文字を付加
    # 音程の取得と周波数の計算
    if note_code == "r":  # 休符（rest）の場合
        p.start(0)  # デューティ比0%でPWM信号の出力を開始（つまり、PWM信号を止める。）
    else:  # 音符の場合
        note_diff = NOTE_DIFF[note_acc]
        octave = int(octave)  # 文字列を整数に変換
        frequency = TUNING * \
                    (2 ** (octave - 4)) * \
                    ((2 ** note_diff) ** (1 / 12.0))
        p.ChangeFrequency(frequency)
        p.start(0.5)  # デューティ比50%でPWM信号の出力を開始
    duration = 4 * DURATION_PER_NOTE / tone[1]  # 発音（または非発音）時間を計算
    if len(tone) > 2:
        if tone[2] == ".":  # 付点音符（または休符）の場合
            duration *= 1.5
    time.sleep(duration)
    p.stop()

def play():
    p = GPIO.PWM(PIN, 440)
    for t in UPPER_PART:
        play_tone(p,t)

def destroy():
    GPIO.cleanup()


# 以降はメインプログラム
setup()

try:
    play()
except KeyboardInterrupt:
    pass

destroy()
