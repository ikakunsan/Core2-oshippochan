# wifi initial settings
#
#   This assumes a file named "myconf.py", that contains below lines;
#     STA_SSID = "your WiFi SSID name"
#     STA_PASS = "your WiFi password"
#
import network
import myconf

sta_ssid = myconf.STA_SSID
sta_pass = myconf.STA_PASS
# ap_ssid = myconf.AP_SSID      # In case of activating AP
# ap_pass = myconf.AP_PASS      # In case of activating AP

def wifiinit():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(sta_ssid, sta_pass)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    # ap.active(True)
    # ap.config(essid=ap_ssid, password=ap_pass, hidden=True)
    # ap.config(max_clients=10)
