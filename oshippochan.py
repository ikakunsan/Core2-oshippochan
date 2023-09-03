#
# Oshippo-Chan (A variant of Stack-Chan. 変種第n号)
#

from m5stack import *
from m5stack_ui import *
from uiflow import *
from machine import Pin, PWM, Timer
import urequests as requests
import ujson
import ubinascii
import time
import random
import network
import myconf

##### ユーザーごとの設定 (ID, Password, API Keys, etc)
sta_ssid = myconf.STA_SSID  # WiFi SSID
sta_pass = myconf.STA_PASS  # WiFi パスワード
Google_API_key = myconf.Google_API_key
OpenAI_API_key = myconf.OpenAI_API_key
try:
    my_ntp_server = myconf.MY_NTP_SERVER  # time.aws.com とか使ってもよし
except:
    my_ntp_server = "time.aws.com"
#####

##### Face parts ;-) (tentative, to be updated)
eyes_w = 90 / 2
eyes_y = 110
mouth_w = 40 / 2
mouth_y = 140
#####

##### Unit demendent settings
gpio_pan = 33
gpio_tilt = 32
gpio_tail = 27
offset_pan = 0  # minus for clockwise, plus for counterclockwise
offset_tilt = 0  # minus for down, plus for up
offset_tail = 0  # minus for left, plus for right
#####

##### PWM servo dependent settings
servo_cycle_ms = 20  # milisec
servo_90deg = 7.5  # テストの名残
servo_duty_min = 2.5  # 0 degree
servo_duty_max = 12.5  # 180 degree
#####

##### Servo related settings
tilt_step = 30 / 1000 * servo_cycle_ms  # degree per step
tilt_max_up = 41  # limit in degree, depends on hardware
tilt_max_down = 6  # limit in degree, depends on hardware
pan_step = 45 / 1000 * servo_cycle_ms  # degree per step
pan_max = 77  # limit in degree

pan_center = 90 + offset_pan
pan_current = 0
pan_target = pan_current
pan_actions = []
tilt_center = 80 + offset_tilt  # デフォルトは10度上向き
tilt_current = 0
tilt_target = tilt_current
tilt_actions = []

tail_center = 90 + offset_tail
tail_swing_max = 10
tail_right = True
tail_furifuri_ms = 1  # moving time in milisec
tail_pos_center = 8
tail_pos = 7.5
spf_ms = 1000
#####

##### Face related
mouth_actions = ()
mouth_mode = 0  # 0:open, 1:surprise
mouth_status = 0  # 0:not closed, 1:closed
mouth_cycle_ms = 200
#####

##### Chat GPT related
word_items = [
    "動物",
    "歴史",
    "食べ物",
    "科学",
]
#####

##### Others
pressed_button_A = False
pressed_button_B = False
pressed_button_C = False

# sound_path = "res/"
sound_path = "/sd/sound/"

idle_cycle_ms = 1000
idle_action_interval = 10 * 60   # seconds
idle_actions_time_next = 0      # seconds
idle_actions_time_current = 0
idle_state = True
#####


def buttonA_wasPressed():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target
    global pressed_button_A

    print("*** button A was pressed")
    # lcd.print("Button A Pressed", 0, 20, 0xFFBBFF)
    # time.sleep(1)
    # lcd.print("Button A Pressed", 0, 20, lcd.BLACK)
    pressed_button_A = True


def buttonB_wasPressed():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target
    global tilt_actions
    global pressed_button_B

    print("*** button B was pressed")
    # lcd.print("Button B Pressed", 0, 40, 0xFFBBFF)
    # time.sleep(1)
    # lcd.print("Button B Pressed", 0, 40, lcd.BLACK)
    pressed_button_B = True


def buttonC_wasPressed():
    global tilt_target, pan_target
    global tilt_actions
    global pressed_button_C

    print("*** button C was pressed")
    # lcd.print("Button C Pressed", 0, 60, 0xFFBBFF)
    # time.sleep(1)
    # lcd.print("Button C Pressed", 0, 60, lcd.BLACK)
    pressed_button_C = True


def buttonA_handler():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target
    global tilt_actions
    global idle_actions_time_next

    idle_actions_time_next = time.ticks_add(idle_actions_time_next, 5*60*1000)
    # tail_swing_max = 10
    tail_swing_max = random.uniform(8.5, 12)
    # spf_ms = 1200
    spf_ms = random.randint(800, 1200)
    tail_furifuri_ms = 4800

    tilt_actions.clear()
    tilt_actions = [30, -5, 30, -5, 30, 0]
    do_actions()


def buttonB_hander():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target
    global tilt_actions
    global idle_actions_time_next

    idle_actions_time_next = time.ticks_add(idle_actions_time_next, 5*60*1000)
    tilt_actions.clear()
    tilt_actions = [30, -5, 30, -5, 30, 0]
    do_actions()
    pass


def buttonC_hander():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target, tilt_actions
    global mouth_mode
    global idle_actions
    global idle_actions_time_next

    idle_actions_time_next = time.ticks_add(idle_actions_time_next, 5*60*1000)
    tail_swing_max = random.uniform(8.5, 12)
    spf_ms = random.randint(800, 1200)
    tail_furifuri_ms = 4800
    mouth_mode = 0
    
    timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
    speaker.playWAV(sound_path + "haai.wav")
    timerSch.stop("timer_Mouth")
    
    draw_mouth(1, lcd.WHITE)
    tilt_actions.clear()
    tilt_actions = [35, -5, 0]
    do_actions()

    # call OpenAI API and Google API, and speak something

    gpt_message_item = word_items[random.randrange(len(word_items))]
    # print(word_items)
    # print(random.randrange(len(word_items)))
    # print(gpt_message_item)
    gpt_message_content = gpt_message_item + "にちなんだ、うんちく話をして。60文字以内でお願い。"

    print("Sending request to OpenAI API")
    r = request_gpt(gpt_message_content)
    print(len(r))
    print("Got response from OpenAI API")
    print("Converting text data to audio file...")
    
    timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
    speaker.playWAV(sound_path + "chottomatte.wav")
    timerSch.stop("timer_Mouth")
    
    draw_mouth(1, lcd.WHITE)
    get_wavfile(r)
    mouth_mode = 0
    timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
    speaker.playWAV("/sd/response.wav")
    timerSch.stop("timer_Mouth")
    draw_mouth(0, lcd.WHITE)


def idle_action_handler():
    pass

def draw_eyes(style, offset_x, offset_y, color):
    global eyes_w, eyes_y

    print("drawing eyes")
    print(style, eyes_w, eyes_y, color)
    if style == 0:  # Opened eye
        print("opened eye")
        #        eye_l_x = int(160-eyes_w+offset_x)
        eye_l_x = int(160 - eyes_w - offset_x)
        eye_r_x = int(160 + eyes_w + offset_x)
        eye_l_y = eyes_y + offset_y
        eye_r_y = eyes_y + offset_y
        lcd.rect(
            int(160 - eyes_w - 25),
            int(eyes_y - 40),
            int(eyes_w * 2 + 50),
            60,
            lcd.BLACK,
            lcd.BLACK,
        )
        #        lcd.rect(int(160-eyes_w-25), int(eyes_y-40) , int(eyes_w*2+50), 60, lcd.BLUE)
        lcd.circle(eye_l_x, eye_l_y, 9, color, color)
        lcd.circle(eye_r_x, eye_r_y, 9, color, color)
    elif style == 1:  # Closed eye
        lcd.rect(
            int(160 - eyes_w - 25),
            int(eyes_y - 40),
            int(eyes_w * 2 + 50),
            60,
            lcd.BLACK,
            lcd.BLACK,
        )
        lcd.line(int(eye_l_x - 9), eye_l_y, eye_l_x + 9, eye_l_y, color)
        lcd.line(int(eye_l_x - 9), eye_l_y, eye_l_x + 9, eye_l_y, color)
    elif style == 2:  # Puzzled eye
        lcd.rect(
            int(160 - eyes_w - 25),
            int(eyes_y - 40),
            int(eyes_w * 2 + 50),
            60,
            lcd.BLACK,
            lcd.BLACK,
        )
        lcd.line(
            int(160 - eyes_w - 9), int(eyes_y - 9), int(160 - eyes_w + 9), eyes_y, color
        )
        lcd.line(
            int(160 - eyes_w - 9), int(eyes_y + 9), int(160 - eyes_w + 9), eyes_y, color
        )
        lcd.line(
            int(160 + eyes_w + 9), int(eyes_y - 9), int(160 + eyes_w - 9), eyes_y, color
        )
        lcd.line(
            int(160 + eyes_w + 9), int(eyes_y + 9), int(160 + eyes_w - 9), eyes_y, color
        )


def draw_mouth(style, color):  # 0:opened, 1:closeed, 2:surprised, 3:angry
    global mouth_w, mouth_y

    # print("drawing mouth ... ", end="")
    left_x = int(160 - mouth_w)
    left_y = mouth_y
    right_x = int(160 + mouth_w)
    right_y = mouth_y
    center_x = 160
    center_y = int(mouth_y + 15)
    if style == 0:  # Opened mouth
        # print("OPEN")
        #        lcd.line(left_x, left_y, right_x, right_y, lcd.BLACK)
        lcd.rect(160 - 40, mouth_y, 80, 25, lcd.BLACK, lcd.BLACK)
 #       lcd.rect(160 - 40, mouth_y, 80, 25, lcd.BLUE)
        lcd.triangle(left_x, left_y, right_x, right_y, center_x, center_y, color, color)
    elif style == 1:  # Closed mouth
        # print("CLOSE")
        #        lcd.triangle(left_x, left_y, right_x, right_y, center_x, center_y, lcd.BLACK, lcd.BLACK)
        lcd.rect(160 - 40, mouth_y, 80, 25, lcd.BLACK, lcd.BLACK)
#        lcd.rect(160 - 40, mouth_y, 80, 20, lcd.BLUE)
        lcd.line(left_x, left_y, right_x, right_y, color)
    elif style == 2:  # Surprised
        pass
    elif style == 3:  # Angry
        pass


def wink():
    # to be implemented
    pass


def random_wink():
    # to be implemented
    pass


def degree_to_pwm(degree):
    global servo_90deg, servo_duty_min, servo_duty_max

    return servo_duty_min + degree * (servo_duty_max - servo_duty_min) / 180


def wait_tilt_ms():
    global tilt_target, tilt_current, tilt_step, servo_cycle_ms

    return int(abs(tilt_target - tilt_current) / tilt_step * servo_cycle_ms)


def wait_pan_ms():
    global pan_target, pan_current, pan_step, servo_cycle_ms

    return int(abs(pan_target - pan_current) / pan_step * servo_cycle_ms)


def do_actions():
    global tilt_actions, pan_actions
    global tilt_target, pan_target

    for i in range(len(tilt_actions)):
        tilt_target = tilt_actions[i]
        time.sleep_ms(wait_tilt_ms())
    for i in range(len(pan_actions)):
        tilt_target = pan_actions[i]
        time.sleep_ms(wait_tilt_ms())
    pass


def request_gpt(input_text):
    req_url = "https://api.openai.com/v1/chat/completions"
    req_headers = {}
    #    req_headers["Authorization"] = "Bearer $(gcloud auth application-default print-access-token)"
    req_headers["Content-Type"] = "application/json"
    req_headers["Authorization"] = "Bearer " + OpenAI_API_key

    gpt_message_content = input_text

    gpt_send_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": gpt_message_content,
            }
        ],
        "temperature": 0.9,
        "max_tokens": 500,
    }

    req_data = ujson.dumps(gpt_send_data)
    req_data = req_data.encode()

    print("Post data")
    try:
        res = requests.post(
            url=req_url,
            headers=req_headers,
            data=req_data,
        )
        print("Get Res")

        d = ujson.loads(res.text)
        r = d["choices"][0]["message"]["content"]
        res.close()
    except:
        print("Failed to connect to OpenAI server. Maybe not connected to the Internet")
        r = ""

    return r


def get_wavfile(input_text):
    req_url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
    req_url = req_url + "?key=" + Google_API_key
    req_headers = {}
    req_headers["Content-Type"] = "application/json; charset=utf-8"
    req_headers["X-goog-api-key"] = Google_API_key
    # req_data内のパラメータ変更はお好みで（参考リンク）：
    # https://cloud.google.com/text-to-speech/docs/reference/rest/v1beta1/AudioConfig
    # https://cloud.google.com/text-to-speech/docs/voices?hl=ja
    req_data = {
        "input": {"text": ""},
        "voice": {
            "languageCode": "ja-jp",
            "name": "ja-JP-Neural2-B",
            "ssmlGender": "FEMALE",
        },
        "audioConfig": {"audioEncoding": "LINEAR16", "speakingRate": 1.1, "pitch": 2},
    }

    req_data["input"]["text"] = input_text

    req_data = ujson.dumps(req_data)
    req_data = req_data.encode()

    print("Posting info to Google Cloud")
    res = requests.post(
        url=req_url,
        headers=req_headers,
        data=req_data,
    )
    print(res.status_code)
    print(res.reason)

    b64 = res.text[20:-202]

    # # ujosnで処理すると超遅い・・・
    # print("Converting json to dict")
    # res_dict = ujson.loads(res.text)
    # print("Picking base64 part")
    # b64 = res_dict["audioContent"]
    
    print(len(res.text))

    print("Decoding base64")
    wav = ubinascii.a2b_base64(b64)
    print("Start file writing")
    #    with open("res/response.wav", "bw") as f:
    with open("/sd/response.wav", "bw") as f:
        f.write(wav)
    print("End file writing")

    res.close()


def junbi_taiso():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms
    global tilt_target, pan_target

    # 電源投入後の準備運動 B-)
    pan_target = 30
    time.sleep_ms(wait_pan_ms())
    pan_target = -30
    time.sleep_ms(wait_pan_ms())
    pan_target = 0
    time.sleep_ms(wait_pan_ms())
    tilt_target = 30
    time.sleep_ms(wait_tilt_ms())
    tilt_target = -5
    time.sleep_ms(wait_tilt_ms())
    tilt_target = 0
    time.sleep_ms(wait_tilt_ms())
    time.sleep(1)


########## Timer Events

# 駆動系
@timerSch.event("timer_Servo")
def ttimer_Servo():
    # def servo_move(timer):
    global tail_furifuri_ms
    global tail_pos
    global tail_right
    global tail_swing_max, servo_90deg, offset_tail
    global tilt_center, tilt_current, tilt_target, tilt_step
    global tilt_max_up, tilt_max_down
    global pan_center, pan_current, pan_target, pan_step
    global pan_max

    ##### Tail
    tail_swing_width = tail_swing_max - servo_90deg + offset_tail
    if tail_furifuri_ms > 0:
        tail_furifuri_ms -= servo_cycle_ms
        if tail_right == True:
            tail_pos += tail_swing_width * 4 / spf_ms * servo_cycle_ms
            pwm_tail.duty(tail_pos)
            if tail_pos >= tail_pos_center + tail_swing_width:
                tail_right = False
        else:
            tail_pos -= tail_swing_width * 4 / spf_ms * servo_cycle_ms
            pwm_tail.duty(tail_pos)
            if tail_pos <= tail_pos_center - tail_swing_width:
                tail_right = True
    #    print(tail_furifuri_ms, tail_pos)

    ##### Tilt
    if tilt_current < tilt_target:
        tilt_current += tilt_step
    elif tilt_current > tilt_target:
        tilt_current -= tilt_step
    if abs(tilt_target - tilt_current) < tilt_step:
        tilt_current = tilt_target
    angle_current = tilt_center - tilt_current
    #    print(tilt_center-tilt_target, angle_current, tilt_current)
    pwm_tilt.duty(degree_to_pwm(angle_current))

    ##### Pan
    if pan_current < pan_target:
        pan_current += pan_step
    elif pan_current > pan_target:
        pan_current -= pan_step
    if abs(pan_target - pan_current) < pan_step:
        pan_current = pan_target
    angle_current = pan_center + pan_current

    #    print(pan_center+pan_target, angle_current, pan_current)
    pwm_pan.duty(degree_to_pwm(angle_current))

### 目
# @timerSch.event("timer_Eyes")
# def ttimer_Eyes():
#    pass

### 口
@timerSch.event("timer_Mouth")
def ttimer_Mouth():
    global mouth_actions, mouth_mode, mouth_status

    if mouth_status == 0:
        draw_mouth(mouth_mode, lcd.WHITE)
        mouth_status = 1
    else:
        draw_mouth(1, lcd.WHITE)
        mouth_status = 0

# アイドル時のランダムな動き
@timerSch.event("timer_IdleAction")
def ttimer_IdleAction():
    global idle_action_interval, idle_actions_time_next
    global tail_swing_max, tail_furifuri_ms, spf_ms
    
    if time.ticks_diff(time.ticks_ms(), idle_actions_time_next) >= 0:
        print("### idle event")
        tail_swing_max = random.uniform(8.5, 12)
        spf_ms = random.randint(1200, 1800)
        tail_furifuri_ms = random.randint(1000, 2000)
        idle_actions_time_next = time.ticks_add(time.ticks_ms(), idle_action_interval*1000)


################################# Main

if __name__ == "__main__":
    print("wifi connect")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(sta_ssid, sta_pass)

    print("initialize screen")
    screen = M5Screen()
    screen.clean_screen()
    screen.set_screen_bg_color(lcd.BLACK)

    # Draw face (TODO: パーツで出すかビットマップか)
    print("draw face")
    draw_eyes(0, 0, 0, lcd.WHITE)
    draw_mouth(0, lcd.WHITE)

    print("mount SD card")
    try:
        os.mount(sd, "/sd")
    except:
        # TODO: 悲しい顔
        mouth_mode = 0
        timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
        speaker.playWAV("res/sdcardnotfound.wav")
        timerSch.stop("timer_Mouth")
        draw_mouth(1, lcd.WHITE)

    print("wait until wifi connection is made")
    wifi_timeout = 60  # seconds for timeout
    wifi_connected = False
    lcd.print("WiFi connecting...", 100, 5, 0x00FFFF)  # 日本語は表示できない…
    time_start = time.ticks_ms()
    time_expire = time.ticks_add(time_start, wifi_timeout * 1000)

    nowtime = time_start
    eyes_offset_x = 15
    eyes_offset_y = -15

    draw_eyes(0, 0, 0, lcd.WHITE)
    draw_mouth(0, lcd.WHITE)

    eyes_offset_x = 15
    eyes_offset_y = 0
    while (not wlan.isconnected()) and (time.ticks_diff(time_expire, nowtime) > 0):
        print(eyes_offset_x)
        #        if eyes_offset_x > 0:
        eyes_offset_x = 0 - eyes_offset_x
        draw_eyes(0, eyes_offset_x, eyes_offset_y, lcd.WHITE)
        time.sleep(2)
        nowtime = time.ticks_ms()
        draw_eyes(0, -eyes_offset_x, eyes_offset_y, lcd.WHITE)

    lcd.print("WiFi connecting...", 100, 5, lcd.BLACK)  # 前に書いたの消すよ
    print(time_expire, nowtime)
    if time.ticks_diff(time_expire, nowtime) > 0:
        wifi_connected = True
        rtc.settime("ntp", host=my_ntp_server, tzone=9)
        word_items.append(str(rtc.datetime()[1]) + "月" + str(rtc.datetime()[2]) + "日")
    else:
        draw_eyes(2, 0, 0, lcd.WHITE)
        mouth_mode = 0
        timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
        speaker.playWAV(sound_path + "wifierror.wav")
        timerSch.stop("timer_Mouth")
        draw_mouth(0, lcd.WHITE)

    draw_eyes(0, 0, 0, lcd.WHITE)
    draw_mouth(0, lcd.WHITE)

    btnA.wasPressed(buttonA_wasPressed)
    btnB.wasPressed(buttonB_wasPressed)
    if wifi_connected:
        btnC.wasPressed(buttonC_wasPressed)

    pin_pan = Pin(gpio_pan)
    pin_tilt = Pin(gpio_tilt)
    pin_tail = Pin(gpio_tail)

    pwm_pan = PWM(pin_pan, freq=int(1000 / servo_cycle_ms))
    pwm_pan.duty(degree_to_pwm(pan_center))
    pwm_tilt = PWM(pin_tilt, freq=int(1000 / servo_cycle_ms))
    pwm_tilt.duty(degree_to_pwm(tilt_center))
    pwm_tail = PWM(pin_tail, freq=int(1000 / servo_cycle_ms))
    pwm_tail.duty(tail_pos_center)

    ### Note that Timer(-3) is used by the system
    timerSch.run("timer_Servo", servo_cycle_ms, 0x00)
    # timerSch.run("timer_Mouth", mouth_cycle_ms, 0x00)
    idle_actions_time_current = time.ticks_ms()
    idle_actions_time_next = time.ticks_add(idle_actions_time_current, idle_action_interval*1000)
    timerSch.run("timer_IdleAction", idle_cycle_ms, 0x00)

    junbi_taiso()

    timerSch.run("timer_IdleAction", idle_cycle_ms, 0x00)
    tail_right = True
    tail_pos = 7.5
    tail_swing_max = 10
    spf_ms = 1200
    tail_furifuri_ms = 3000
    # time.sleep(30)

    timeout = 60  # seconds for timeout for functional testing
    time_start = time.ticks_ms()
    time_expire = time.ticks_add(time_start, timeout * 1000)
    nowtime = time_start

    # while time.ticks_diff(time_expire, nowtime) > 0:    # Limited time running for testing
    while True:   # Endless
        if pressed_button_A:
            print("Button A was pressed")
            pressed_button_A = False
            buttonA_handler()
            pass
        elif pressed_button_B:
            print("Button B was pressed")
            pressed_button_B = False
            buttonB_hander()
            pass
        elif pressed_button_C:
            print("Button C was pressed")
            pressed_button_C = False
            buttonC_hander()
        nowtime = time.ticks_ms()

    print("*************************************************************")
    #    servoTimer.deinit()
    timerSch.stop("timer_Servo")
    timerSch.stop("timer_Mouth")
    timerSch.stop("timer_IdleAction")
