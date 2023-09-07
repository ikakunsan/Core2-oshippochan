# Core2-oshippochan

こちらの参加作品です。
https://protopedia.net/prototype/4404

スタックチャンに尻尾が生えました。

# ハードウェア - Hardware
## 概要
- サーボは3つ。水平観点用 (Pan), 上下回転用 (Tilt), 尻尾用 (Tail)
- GPIOはそれぞれ、Pan: GPIO33, Tilt: GPIO32, Tail: GPIO27 を使っています。
- 脚部のUSBコネクタからは、M5Stackとサーボに給電します。電源のみでデータは繋がっていないので、M5Stackにアクセスする場合は本体側にUSBケーブルを接続する必要があります。（本体のUSBからはサーボでの電力は供給されません。サーボの貫通電流の関係です）

## 使ったもの - Items
1. M5Stack Core2 + SD card (本体のFlashを頻繁に書き込みたくなかったので) I don't want to write internal flash frequently
2. M5Stack プロトモジュール (基板とネジ) Proto-module (Using PCB and screw only)
1. サーボ (SG-90やSG-92等。上下はSG-92が良さげ。尻尾用は音の静かなSG-90がいいかも ) Servo
1. 整流用ダイオード (1A以上、ショットキーバリアは非推奨、今回はファストリカバリー使用) Diode (more than 1A. Schottky barrier diode is not recommended due to low Vf. I used fast recovery diode)
1. USB-C メスコネクタの付いた基板。今回使ったのはこれ。 PCB with USB-C female connector
1. ピンヘッダ (ライトアングル)、2pコネクタ(XH)、電線等。 Other components such as pin header, XH connector, wire etc.
1. 自作の3Dプリントパーツ (STLの下。自分のプリンタに合わせこんだので微妙なところがあるかもしれません…。素材は、筐体はなんでもいいですが、尻尾はPETG推奨。PLAは弾力に欠けるので非推奨です。ABSは試していません) Self-made 3D print parts (I put STL files in Github. Any material will be fine for body. PLA is not recommended for tail. PETG is recommended. (PLA is easy to deform so not suitable for usage like this)
1. 釣り用ナイロン糸 (0.8号) Nylon string. Thinner one is better. I used 0.155mm string for fishing.
1. M2x6mmなべタッピングビス 1個 (尻尾取り付け用)、M2x8mmなべタッピングビス 2個 (サーボ取り付け用) Tapping screw M2x6 1pcs (to fix tail), M2x8 2pcs (to fix servo)

注1) プログラム書き込み時はUSBケーブルを2本挿すことになるので、逆流防止でダイオードを入れています。Core2で使用している電源管理IC AXP192の仕様で不明の部分が多いため、安全側に振る目的で、ダイオードはVfの大きめのものを使っています。 Information in the AXP192 datasheet is insufficient and I couldn't find max voltage, so I used a fast recovery diode, it has bigger Vf, for safe. 

注2) サーボをギリギリまで寄せてしまったので付属のネジだと頭が壁にひっかかかるため、壁側は通常のM2のタッピングビスを使う必要があります。（付属のネジを無理に使うと途中で折れることがあります…） There are no (minus) margin on one side of the bottom servos, so standard M2 screw should be used on wall side.

## 製作 - How to make
（ガレキレベルの難易度です…。誰でも作れるレベルに落とし込めていません…） It will be hard to make this because parts dimensions are optimized to my 3D printer, and no pre-wred PCB (using ) etc...

1. M5Stack プロトモジュールの基板を外して、コネクタ等のパーツを取り付けて配線。写真4のように。 Detach PCB from M5Stack proto module. Assemble and wire components (header, connector diode etc). Refer to picture 4.
1. 8~9cmのワイヤにXHコネクタを取り付け、USB-C基板にはんだ付けする。このとき、基板に穴に差し込むけれど、裏には飛び出ないように。USB-C基板をプリント基板等の非金属の耐熱性のあるものにあてがって、ワイヤを穴に挿して上側からはんだ付けすると裏に飛び出ません。 Connect USB-C and XH connector to wire
1. プロトモジュール基板にM5Stackやサーボを取り付けて（筐体なしの状態での）動作確認。 Connect M5Stack and servo to the proto module and check the functions
1. シェル固定用のアームがボディーの穴に入ってスムーズに動くのを確認。アーム側を少し削るとか穴を少し広げるとか調整が必要かもしれません。ガタ防止であまり余裕もたせていないので。 Check if the arm to fix shell can set to the body and moves smoothly. (may need to trim the arm hole)
1. 足を組み立てる。ワイヤを穴に通して、サーボの取り付けパーツをはめて、カバーをスライドさせて閉じる。(写真5) Build a foot. Set the PCB and set the parts, then slide the cover.
1. 全部のサーボを90度の位置に設定。 Set all servos to 90 degree.
1. Bodyに下向きのサーボ２個を取り付ける。下面の壁側は付属のネジは使わずに、M2x8のタッピングビスを使ってください。 Fix two bottom servos to the body. Please use M2x8 screw on wall side of two bottom servos.
1. 足からのケーブルをサーボの間から通して上に出す。
1. サーボのケーブルの余るぶんは、丸くまとめてサーボの間に突っ込む。(写真3, 4) Arrange extra servo cables as shown in the picture 3 and 4.
1. 尻尾にナイロン糸を通す。長めに切って、まずは中央部を尻尾先端で二重結び。左右両方の糸を、根本まで、尻尾の穴を通す。糸を通したら、尻尾をM2x6mmのネジで本体に固定。 Tight a center of nylon string at the end of the tail and then through the holes to the base. Fix the tail to the body with M2x6 screw.
1. 尻尾側のサーボホーンを写真3のようにカットしてサーボに取り付ける。完全に平行にならない場合は写真4の向きに斜めになるように (ホーンの回転部が中心からオフセットしているので)。 Cut the servo horn as shown in the picture 3, then connect it to the servo.
糸をホーンに縛り付ける。二重結び。たるみが出ないように左右均等にピンと張ること。(ちょっと難しい) Tight the string to the horn. Make sure the string is not loose.
1. ワイヤを2回巻き付けてから上部のサーボをアームとともに取り付ける。アームをホーンで固定。 Fix the upper servo with the arm.
1. 全部のワイヤのコネクタを基板に挿す。 Connect all cables to the PCB
1. シェルをアームに取り付ける。スペーサーを介して基板とシェルをネジ止め（プロトモジュールのネジを使用）する。ワイヤ類が動作に影響しないか確認。影響するようなら基板を外してワイヤ位置を調整して組み直し。 Attach the shell to the arm. Screw the PCB with the spacer. Check if the wires interfares with body.

# ソフトウェア - Software
## 必要なもの - Requirements
- OpenAI APIのAPI Key (最初の3ヶ月は無料。以降の利用には料金引き落とし方法の登録が必要)
- Google Text to SpeechのAPI Key (引き落とし方法の登録が必要。毎月無料枠あり)

## 手順 - Procedure
1. UIFlowのファームウェアを入れる Install UIFlow firmware
2. myconf-sample.pyにWiFi接続に必要な情報やAPI Keyを入力。ファイル名を myconf.pyに変更。Edit myconf-sample.py and rename it to myconf.py
1. Githubに上がっているファイル (ルート及びresの下のWAVファイル) をM5Stack Core2に転送して実行。 - Transfer all files, including wav file to M5Stack Core2
