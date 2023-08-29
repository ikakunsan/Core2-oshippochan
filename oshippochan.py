from m5stack import *
from m5stack_ui import *
from uiflow import *
from machine import Pin, PWM, Timer
import urequests as requests
import ujson
import ubinascii
import os
import time
import random
import network
import myconf

##### ユーザーごとの設定 (ID, Password, API Keys, etc)
sta_ssid = myconf.STA_SSID      # WiFi SSID
sta_pass = myconf.STA_PASS      # WiFi パスワード
Google_API_key = myconf.Google_API_key  
OpenAI_API_key = myconf.OpenAI_API_key  
try:
    my_ntp_server = myconf.MY_NTP_SERVER    # time.aws.com とか使ってもよし
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
offset_pan = 0    # minus for clockwise, plus for counterclockwise
offset_tilt = 0   # minus for down, plus for up
offset_tail = 0   # minus for left, plus for right
#####

##### PWM servo dependent settings
servo_cycle_ms = 20     # milisec
servo_90deg = 7.5       # テストの名残
servo_duty_min = 2.5    # 0 degree
servo_duty_max = 12.5   # 180 degree
#####

##### Servo related settings
tilt_step = 30 / 1000 * servo_cycle_ms  # degree per step
tilt_max_up = 41    # limit in degree, depends on hardware
tilt_max_down = 6   # limit in degree, depends on hardware
pan_step = 45 / 1000 * servo_cycle_ms   # degree per step
pan_max = 77        # limit in degree

pan_center = 90 + offset_pan
pan_current = 0
pan_target = pan_current
tilt_center = 90 + offset_tilt
tilt_current = 0
tilt_target = tilt_current

tail_center = 90 + offset_tail
tail_swing_max = 10
tail_right = True
tail_furifuri_ms = 1    # moving time in milisec
tail_pos_center = 8
tail_pos = 7.5
spf_ms = 1000
#####

##### Chat GPT related
word_items = ["動物", "歴史", "食べ物", "科学",]
#####

def buttonA_wasPressed():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms

#    lcd.print('Button A Pressed', 0, 20, 0xffffff)
    # tail_swing_max = 10
    tail_swing_max = random.uniform(8.5, 12)
    # spf_ms = 1200
    spf_ms = random.randint(800, 1200)
    tail_furifuri_ms = 4800
    
    tilt_target = 30
    time.sleep_ms(wait_tilt_ms())
    tilt_target = -5
    time.sleep_ms(wait_tilt_ms())
    tilt_target = 30
    time.sleep_ms(wait_tilt_ms())
    tilt_target = -5
    time.sleep_ms(wait_tilt_ms())
    tilt_target = 0


def buttonB_wasPressed():
    global tail_furifuri_ms, tail_swing_max
    global spf_ms, tail_furifuri_ms

#    lcd.print('Button B Pressed', 0, 40, 0xffbbff)
    # call OpenAI API and Google API, and speak something
    gpt_message_item = word_items[random.randrange(len(word_items))]
    print(gpt_message_item)
    gpt_message_content = gpt_message_item + "にちなんだ、うんちく話をして。60文字以内でお願い。"

    # アクションをとって考えてるフリ
    tail_swing_max = 10
    spf_ms = 1200
    tail_furifuri_ms = 10000

    print('Sending request to OpenAI API')
    r = request_gpt(gpt_message_content)
    print('Return from OpenAI API')
    print('Converting data to audio file...')
    get_wavfile(r)
    speaker.playWAV('/sd/response.wav')


def buttonC_wasPressed():
#    lcd.print('Button A Pressed', 0, 20, 0x000000)
    # call OpenAI API and Google API, and speak something
    tilt_target = 30
    time.sleep_ms(wait_tilt_ms())
    tilt_target = -5
    time.sleep_ms(wait_tilt_ms())
    tilt_target = 30
    time.sleep_ms(wait_tilt_ms())
    tilt_target = -5
    time.sleep_ms(wait_tilt_ms())
    tilt_target = 0
    pass

#btnC.wasPressed(buttonC_wasPressed)

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

    return int(abs(tilt_target-tilt_current) / tilt_step * servo_cycle_ms)


def wait_pan_ms():
    global pan_target, pan_current, pan_step, servo_cycle_ms

    return int(abs(pan_target-pan_current) / pan_step * servo_cycle_ms)


def actions(timer):
    pass


def servo_move(timer):
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


def request_gpt(input_text):
    req_url = "https://api.openai.com/v1/chat/completions"
    req_headers = {}
    #    req_headers["Authorization"] = "Bearer $(gcloud auth application-default print-access-token)"
    req_headers["Content-Type"] = "application/json"
    req_headers["Authorization"] = "Bearer " + OpenAI_API_key

    print('011')

    gpt_message_content = input_text

    gpt_send_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user", 
            "content": gpt_message_content,
        }],
        "temperature": 0.9,
        "max_tokens": 500,
    }

    print('012')

    req_data = ujson.dumps(gpt_send_data)
    req_data = req_data.encode()

    try:
        res = requests.post(
            url=req_url,
            headers=req_headers,
            data=req_data,
        )
        print('Get Res')

        d = ujson.loads(res.text)
        r = d['choices'][0]['message']['content']
        res.close()
    except:
        print("Failed to contact to OpenAI server. Maybe not connected to the Internet")
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
        "input": {
            "text": ""
        },
        "voice": {
            "languageCode": "ja-jp",
            "name": "ja-JP-Neural2-B",
            "ssmlGender": "FEMALE"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": 1.1,
            "pitch": 2
        }
    }

    req_data['input']['text'] = input_text

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
#    print(res.text)
    print('Converting json to dict')
    res_dict = ujson.loads(res.text)
#    print(res.text)
    print('Picking base64 part')
    b64 = res_dict["audioContent"]
    print(len(res.text))

#    b64 = res.text[21:-4]
#    print(type(b64))
#    print(b64)
    # wav = base64.b64decode(b64)
    print('Decoding base64')
    wav = ubinascii.a2b_base64(b64)
    print('Start file writing')
#    with open("res/response.wav", "bw") as f:
    with open("/sd/response.wav", "bw") as f:
        f.write(wav)
    print('End file writing')
    
    res.close()



if __name__ == "__main__":

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(sta_ssid, sta_pass)

    screen = M5Screen()
    screen.clean_screen()
    screen.set_screen_bg_color(0x000000)

    # Draw face (TODO: パーツで出すかビットマップか)
    lcd.circle(int(160-eyes_w), eyes_y, 9, 0xffffff, 0xffffff)
    lcd.circle(int(160+eyes_w), eyes_y, 9, 0xffffff, 0xffffff)
    lcd.triangle(int(160-mouth_w), mouth_y, int(160+mouth_w), mouth_y, 160, mouth_y+15, 0xffffff, 0xffffff)

    try:
        os.mount(sd, '/sd')
    except:
        # TODO: 悲しい顔
        speaker.playWAV('res/sdcardnotfound.wav')

    wifi_timeout = 60   # seconds for timeout
    wifi_connected = False
    lcd.print("WiFi connecting...", 100, 5, 0x00ffff)
    time_start = time.ticks_ms()
    time_expire = time.ticks_add(time_start, wifi_timeout*1000)
    nowtime = time_start
    eyes_offset_x = 15
    eyes_offset_y = -20
    lcd.circle(int(160-eyes_w), eyes_y, 9, 0x000000, 0x000000)
    lcd.circle(int(160+eyes_w), eyes_y, 9, 0x000000, 0x000000)
    while (not wlan.isconnected()) and (time.ticks_diff(time_expire, nowtime) > 0):
        print(eyes_offset_x)
#        if eyes_offset_x > 0:
        eyes_offset_x = 0 - eyes_offset_x
        lcd.circle(int(160-eyes_w+eyes_offset_x), eyes_y+eyes_offset_y, 9, 0xffffff, 0xffffff)
        lcd.circle(int(160+eyes_w+eyes_offset_x), eyes_y+eyes_offset_y, 9, 0xffffff, 0xffffff)
        time.sleep(2)
        nowtime = time.ticks_ms()
        lcd.circle(int(160-eyes_w+eyes_offset_x), eyes_y+eyes_offset_y, 9, 0x000000, 0x000000)
        lcd.circle(int(160+eyes_w+eyes_offset_x), eyes_y+eyes_offset_y, 9, 0x000000, 0x000000)

    lcd.print("WiFi connecting...", 100, 5, 0x000000)   # 前に書いたの消すよ
    if time.ticks_diff(time_expire, nowtime) > 0:
        wifi_connected = True
        rtc.settime('ntp', host=my_ntp_server, tzone=9)
        word_items.append(str(rtc.datetime()[1])+"月"+str(rtc.datetime()[2])+"日")
    else:
        speaker.playWAV('res/wifierror.wav')

    lcd.circle(int(160-eyes_w), eyes_y, 9, 0xffffff, 0xffffff)
    lcd.circle(int(160+eyes_w), eyes_y, 9, 0xffffff, 0xffffff)
    lcd.triangle(int(160-mouth_w), mouth_y, int(160+mouth_w), mouth_y, 160, mouth_y+15, 0xffffff, 0xffffff)

    btnA.wasPressed(buttonA_wasPressed)
    if wifi_connected:
        btnB.wasPressed(buttonB_wasPressed)
    btnC.wasPressed(buttonC_wasPressed)

    pin_pan = Pin(gpio_pan)
    pin_tilt = Pin(gpio_tilt)
    pin_tail = Pin(gpio_tail)

    pwm_pan = PWM(pin_pan, freq=int(1000/servo_cycle_ms))
    pwm_pan.duty(degree_to_pwm(pan_center))
    pwm_tilt = PWM(pin_tilt, freq=int(1000/servo_cycle_ms))
    pwm_tilt.duty(degree_to_pwm(tilt_center))
    pwm_tail = PWM(pin_tail, freq=int(1000/servo_cycle_ms))
    pwm_tail.duty(tail_pos_center)

    ### Note that Timer(-3) is used by the system
    # TODO: faceTimer = Timer()
    servoTimer = Timer(-1)
    servoTimer.init(mode=Timer.PERIODIC, period=servo_cycle_ms, callback=servo_move)
    actionTimer = Timer(-2)
    actionTimer.init(mode=Timer.PERIODIC, period=1000*60, callback=actions)
    

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
    tail_right = True
    tail_pos = 7.5
    tail_swing_max = 10
    spf_ms = 1200
    tail_furifuri_ms = 4800
    time.sleep(5)

#    servoTimer.deinit()
