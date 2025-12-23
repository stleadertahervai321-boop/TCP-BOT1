import requests, os, sys, time, urllib3, asyncio, aiohttp, ssl
from xC4 import *
from xHeaders import *
from datetime import datetime
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2
from cfonts import render
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- GLOBAL CONFIGURATION ---
ADMIN_UID = "" 
BYPASS_TOKEN = "GODJEXAR"
SELECTED_LANG = "en" # Default

# Global Variables
online_writer = None
whisper_writer = None
connection_pool = None
bot_start_time = time.time()
join_loop_active = False
current_team_code = None

# --- LANGUAGE DICTIONARY (NATIVE SCRIPTS) ---
LANG_TEXT = {
    # 1. HINDI (Devanagari)
    "hindi": {
        "menu_opt": "[1] हिन्दी (Hindi)",
        "input_uid": "\n [>] कृपया अपना GAME UID डालें (जिसे Admin बनाना है): ",
        "req_sent": " [✓] फ्रेंड रिक्वेस्ट भेज दी गई है! गेम में एक्सेप्ट करें।",
        "req_fail": " [X] रिक्वेस्ट भेजने में त्रुटि आई।",
        "prompt_enter": " [>] रिक्वेस्ट ACCEPT करने के बाद ENTER दबाएं >> ",
        "welcome_chat": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR लेवल अप बोट ऑनलाइन है\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n\n"
            "[00FF00][B]कमांड्स की लिस्ट:\n"
            "[FFFFFF]/join [TEAM_CODE] - लूप शुरू करें\n"
            "[FFFFFF]/stop - लूप रोकें\n"
            "[FFFFFF]/help - मदद मेनू\n\n"
            "[808080]CREDIT: GOD JEXAR"
        ),
        "help_msg": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR हेल्प मेनू\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n"
            "[00FF00]कैसे इस्तेमाल करें:\n"
            "[FFFFFF]1. टीम बनाएं (Lone Wolf)।\n"
            "[FFFFFF]2. टाइप करें: /join CODE\n"
            "[FFFFFF]3. रोकने के लिए: /stop\n\n"
            "[808080]POWERED BY GOD JEXAR"
        ),
        "join_start": "[00FF00][B]🚀 JEXAR बोट सक्रिय\n[FFFFFF]टारगेट टीम: {code}\n[FFFFFF]भाषा: हिन्दी",
        "loop_join": "[00FF00][B]🔄 लूप {count}: ग्रुप जॉइन कर रहा हूँ... ({code})",
        "loop_wait": "[FFD700][B]⏳ ग्रुप में हूँ: {code} (35s इंतजार)",
        "loop_leave": "[FF6347][B]🚪 ग्रुप छोड़ रहा हूँ... (लूप {count})",
        "stop_msg": "[FF0000][B]⛔ बोट रोक दिया गया है! (कमांड प्राप्त)\n[808080]BY GOD JEXAR",
        "console_online": "JEXAR लेवल अप बोट सफलतापूर्वक ऑनलाइन है",
        "console_waiting": " [INFO] कमांड्स का इंतज़ार कर रहा हूँ..."
    },
    
    # 2. ENGLISH (Latin)
    "en": {
        "menu_opt": "[2] English (Global)",
        "input_uid": "\n [>] Enter your GAME UID (To set as Admin): ",
        "req_sent": " [✓] Friend Request Sent! Please accept it in-game.",
        "req_fail": " [X] Failed to send request.",
        "prompt_enter": " [>] Press ENTER after you ACCEPT the request >> ",
        "welcome_chat": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR LEVEL UP BOT IS ONLINE\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n\n"
            "[00FF00][B]Available Commands:\n"
            "[FFFFFF]/join [TEAM_CODE] - Start Loop\n"
            "[FFFFFF]/stop - Stop Loop\n"
            "[FFFFFF]/help - Show Menu\n\n"
            "[808080]CREDIT: GOD JEXAR"
        ),
        "help_msg": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR HELP MENU\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n"
            "[00FF00]How to Use:\n"
            "[FFFFFF]1. Create Group (Lone Wolf).\n"
            "[FFFFFF]2. Type: /join CODE\n"
            "[FFFFFF]3. To Stop: /stop\n\n"
            "[808080]POWERED BY GOD JEXAR"
        ),
        "join_start": "[00FF00][B]🚀 JEXAR BOT ACTIVE\n[FFFFFF]Target Team: {code}\n[FFFFFF]Language: English",
        "loop_join": "[00FF00][B]🔄 Loop {count}: Joining Team... ({code})",
        "loop_wait": "[FFD700][B]⏳ In Group: {code} (Waiting 35s)",
        "loop_leave": "[FF6347][B]🚪 Leaving Group... (Loop {count})",
        "stop_msg": "[FF0000][B]⛔ Bot Stopped! (Command Received)\n[808080]BY GOD JEXAR",
        "console_online": "JEXAR LEVEL UP BOT ONLINE SUCCESSFULLY",
        "console_waiting": " [INFO] Waiting for commands..."
    },

    # 3. BANGLA (Bengali Script)
    "bangla": {
        "menu_opt": "[3] বাংলা (Bangla)",
        "input_uid": "\n [>] আপনার GAME UID দিন (অ্যাডমিন হওয়ার জন্য): ",
        "req_sent": " [✓] ফ্রেন্ড রিকোয়েস্ট পাঠানো হয়েছে! গেমে এক্সেপ্ট করুন।",
        "req_fail": " [X] রিকোয়েস্ট পাঠাতে সমস্যা হয়েছে।",
        "prompt_enter": " [>] রিকোয়েস্ট ACCEPT করার পর ENTER চাপুন >> ",
        "welcome_chat": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR লেভেল আপ বট অনলাইন\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n\n"
            "[00FF00][B]কমান্ড তালিকা:\n"
            "[FFFFFF]/join [CODE] - লুপ শুরু করুন\n"
            "[FFFFFF]/stop - লুপ বন্ধ করুন\n"
            "[FFFFFF]/help - সাহায্য মেনু\n\n"
            "[808080]CREDIT: GOD JEXAR"
        ),
        "help_msg": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]GOD JEXAR সাহায্য মেনু\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n"
            "[00FF00]কিভাবে ব্যবহার করবেন:\n"
            "[FFFFFF]1. গ্রুপ তৈরি করুন (Lone Wolf)।\n"
            "[FFFFFF]2. টাইপ করুন: /join CODE\n"
            "[FFFFFF]3. বন্ধ করতে: /stop\n\n"
            "[808080]POWERED BY GOD JEXAR"
        ),
        "join_start": "[00FF00][B]🚀 JEXAR বট সক্রিয়\n[FFFFFF]টার্গেট টিম: {code}\n[FFFFFF]ভাষা: বাংলা",
        "loop_join": "[00FF00][B]🔄 লুপ {count}: গ্রুপে জয়েন করছি... ({code})",
        "loop_wait": "[FFD700][B]⏳ গ্রুপে আছি: {code} (35s অপেক্ষা)",
        "loop_leave": "[FF6347][B]🚪 গ্রুপ থেকে বের হচ্ছি... (লুপ {count})",
        "stop_msg": "[FF0000][B]⛔ বট বন্ধ করা হলো!\n[808080]BY GOD JEXAR",
        "console_online": "JEXAR লেভেল আপ বট সফলভাবে অনলাইনে আছে",
        "console_waiting": " [INFO] কমান্ডের জন্য অপেক্ষা করছি..."
    },

    # 4. ARABIC (Arabic Script)
    "arabic": {
        "menu_opt": "[4] العربية (Arabic)",
        "input_uid": "\n [>] أدخل معرف اللعبة UID (لتعيين الأدمن): ",
        "req_sent": " [✓] تم إرسال طلب الصداقة! يرجى القبول في اللعبة.",
        "req_fail": " [X] فشل في إرسال الطلب.",
        "prompt_enter": " [>] اضغط ENTER بعد قبول الطلب >> ",
        "welcome_chat": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]بوت GOD JEXAR لرفع المستوى متصل\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n\n"
            "[00FF00][B]الأوامر المتاحة:\n"
            "[FFFFFF]/join [CODE] - بدء الحلقة\n"
            "[FFFFFF]/stop - إيقاف الحلقة\n"
            "[FFFFFF]/help - قائمة المساعدة\n\n"
            "[808080]CREDIT: GOD JEXAR"
        ),
        "help_msg": (
            "[FFD700][B]━━━━━━━━━━━━━━━━━━━\n"
            "[FFFFFF][B]قائمة مساعدة GOD JEXAR\n"
            "[FFD700]━━━━━━━━━━━━━━━━━━━\n"
            "[00FF00]كيفية الاستخدام:\n"
            "[FFFFFF]1. إنشاء مجموعة (Lone Wolf).\n"
            "[FFFFFF]2. اكتب: /join CODE\n"
            "[FFFFFF]3. للإيقاف: /stop\n\n"
            "[808080]POWERED BY GOD JEXAR"
        ),
        "join_start": "[00FF00][B]🚀 JEXAR BOT نشط\n[FFFFFF]الفريق: {code}\n[FFFFFF]اللغة: العربية",
        "loop_join": "[00FF00][B]🔄 تكرار {count}: الانضمام للفريق... ({code})",
        "loop_wait": "[FFD700][B]⏳ في المجموعة: {code} (انتظار 35 ثانية)",
        "loop_leave": "[FF6347][B]🚪 مغادرة المجموعة... (تكرار {count})",
        "stop_msg": "[FF0000][B]⛔ تم إيقاف البوت!\n[808080]BY GOD JEXAR",
        "console_online": "تم اتصال بوت JEXAR بنجاح",
        "console_waiting": " [INFO] في انتظار الأوامر..."
    }
}

def get_msg(key, **kwargs):
    """Helper to get text in selected language"""
    lang_code = SELECTED_LANG
    try:
        text = LANG_TEXT[lang_code][key]
        if kwargs:
            return text.format(**kwargs)
        return text
    except KeyError:
        return LANG_TEXT["en"][key] # Fallback to English

# Headers
Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': 'v1 1',
    'ReleaseVersion': "OB51"
}

# --- ADD.PY LOGIC: ENCRYPTION & HELPERS ---
def Encrypt_ID(x):
    try:
        x = int(x)
        dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
        xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                if x > 128:
                    x = x / 128
                    strx = int(x)
                    y = (x - int(strx)) * 128
                    stry = str(int(y))
                    z = (y - int(stry)) * 128
                    strz = str(int(z))
                    n = (z - int(strz)) * 128
                    strn = str(int(n))
                    m = (n - int(strn)) * 128
                    return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
                else:
                    strx = int(x)
                    y = (x - int(strx)) * 128
                    stry = str(int(y))
                    z = (y - int(stry)) * 128
                    strz = str(int(z))
                    n = (z - int(strz)) * 128
                    strn = str(int(n))
                    return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
        return "" 
    except:
        return ""

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

async def SendFriendRequest(target_id, token, base_url):
    url = f"{base_url}/RequestAddingFriend"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB51",
        "Host": base_url.split("://")[1].split("/")[0], 
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Free%20Fire/2019117061 CFNetwork/1399 Darwin/22.1.0",
        "Connection": "keep-alive",
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "Accept": "/"
    }
    try:
        id_encrypted = Encrypt_ID(target_id)
        if not id_encrypted:
             pass 
        data0 = "08c8b5cfea1810" + id_encrypted + "18012008"
        data = bytes.fromhex(encrypt_api(data0))
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with connection_pool.post(url, headers=headers, data=data, ssl=ssl_context) as response:
            if response.status == 200:
                print(get_msg('req_sent'))
                return True
            else:
                print(get_msg('req_fail'))
                return False
    except Exception as e:
        print(f" [ERROR] Request Logic Failed: {e}")
        return False

# --- STANDARD BOT FUNCTIONS ---

def is_admin(uid):
    return str(uid) == ADMIN_UID

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    try:
        async with connection_pool.post(url, headers=Hr, data=data) as response:
            if response.status != 200:
                return None, None
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)
    except:
        return (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.118.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with connection_pool.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None
    except:
        return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    try:
        async with connection_pool.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None
    except:
        return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9:
        headers = '0000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 7:
        headers = '000000000'
    else:
        headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def cHTypE(H):
    if not H:
        return 'Squid'
    elif H == 1:
        return 'CLan'
    elif H == 2:
        return 'PrivaTe'

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid':
        msg_packet = await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan':
        msg_packet = await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
    elif TypE == 'PrivaTe':
        msg_packet = await xSEndMsg(message, 2, Uid, Uid, key, iv)
    return msg_packet

async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        whisper_writer.write(PacKeT)
        await whisper_writer.drain()
    elif TypE == 'OnLine':
        online_writer.write(PacKeT)
        await online_writer.drain()
    else:
        pass

async def join_leave_loop(team_code, key, iv, region, uid, chat_id, chat_type):
    global join_loop_active
    loop_count = 0
    try:
        while join_loop_active:
            loop_count += 1
            try:
                # JOIN MSG
                join_msg = get_msg('loop_join', count=loop_count, code=team_code)
                P = await SEndMsG(chat_type, join_msg, uid, chat_id, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                
                print(f"\n{'='*60}")
                print(f"🔵 LOOP {loop_count} - JOIN: {team_code} | Lang: {SELECTED_LANG}")
                
                join_packet = await GenJoinSquadsPacket(team_code, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
                
                # WAIT MSG
                status_msg = get_msg('loop_wait', code=team_code)
                P = await SEndMsG(chat_type, status_msg, uid, chat_id, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                
                for remaining in range(35, 0, -1):
                    if not join_loop_active: break
                    print(f"⏱️  Wait: {remaining}s", end='\r', flush=True)
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ JOIN ERROR: {e}")
            
            if not join_loop_active: break
            
            try:
                # LEAVE MSG
                leave_msg = get_msg('loop_leave', count=loop_count)
                P = await SEndMsG(chat_type, leave_msg, uid, chat_id, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                
                print(f"\n🔴 LEAVING TEAM: {team_code}")
                leave_packet = await ExiT(None, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
                await asyncio.sleep(2) 
            except Exception as e:
                print(f"❌ LEAVE ERROR: {e}")
            if not join_loop_active: break
        
        # STOP MSG
        final_msg = get_msg('stop_msg')
        P = await SEndMsG(chat_type, final_msg, uid, chat_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
        
    except Exception as e:
        print(f"❌ LOOP ERROR: {e}")
    finally:
        join_loop_active = False

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
            online_writer.close()
            await online_writer.wait_closed()
            online_writer = None
        except:
            online_writer = None
        await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region):
    global whisper_writer, join_loop_active, current_team_code
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                pK = await AuthClan(clan_id, clan_compiled_data, key, iv)
                if whisper_writer:
                    whisper_writer.write(pK)
                    await whisper_writer.drain()
            
            # SEND WELCOME IN SELECTED LANGUAGE
            try:
                if ADMIN_UID:
                    welcome_msg = get_msg('welcome_chat')
                    P = await SEndMsG(2, welcome_msg, int(ADMIN_UID), int(ADMIN_UID), key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    print(f" [INFO] Welcome Message Sent in {SELECTED_LANG.upper()}!")
            except: pass

            while True:
                data = await reader.read(9999)
                if not data: break
                
                if data.hex().startswith("120000"):
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        chat_type = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower().strip()
                    except: response = None
                    
                    if response and is_admin(uid):
                        if inPuTMsG.startswith('/help'):
                            P = await SEndMsG(chat_type, get_msg('help_msg'), uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        
                        elif inPuTMsG.startswith('/join '):
                            parts = inPuTMsG.split()
                            if len(parts) >= 2:
                                team_code = parts[1].upper()
                                current_team_code = team_code
                                join_loop_active = True
                                P = await SEndMsG(chat_type, get_msg('join_start', code=team_code), uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                asyncio.create_task(join_leave_loop(team_code, key, iv, region, uid, chat_id, chat_type))
                        
                        elif inPuTMsG.startswith('/stop'):
                            if join_loop_active:
                                join_loop_active = False
                                P = await SEndMsG(chat_type, get_msg('stop_msg'), uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            whisper_writer.close()
            await whisper_writer.wait_closed()
            whisper_writer = None
        except:
            whisper_writer = None
        await asyncio.sleep(0.5)

def select_language():
    """Colorful Language Selection Menu with Native Scripts"""
    global SELECTED_LANG
    os.system('clear')
    print(render('GOD JEXAR', colors=['yellow', 'red'], align='center'))
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("      SELECT YOUR BOT LANGUAGE / भाषा चुनें")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Printing options with colors
    print(f"\n \033[1;36m{LANG_TEXT['hindi']['menu_opt']}\033[0m")  # Cyan (Hindi)
    print(f" \033[1;32m{LANG_TEXT['en']['menu_opt']}\033[0m")       # Green (English)
    print(f" \033[1;33m{LANG_TEXT['bangla']['menu_opt']}\033[0m")   # Yellow (Bangla)
    print(f" \033[1;35m{LANG_TEXT['arabic']['menu_opt']}\033[0m")   # Purple (Arabic)
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    choice = input(" [?] Enter Option (1-4): ").strip()
    
    if choice == '1': SELECTED_LANG = 'hindi'
    elif choice == '2': SELECTED_LANG = 'en'
    elif choice == '3': SELECTED_LANG = 'bangla'
    elif choice == '4': SELECTED_LANG = 'arabic'
    else:
        print(" [!] Invalid Selection. Defaulting to English.")
        SELECTED_LANG = 'en'
    
    print(f" [✓] Language Set to: {SELECTED_LANG.upper()}")
    time.sleep(1)

async def MaiiiinE():
    global connection_pool, ADMIN_UID
    
    # 1. SELECT LANGUAGE
    select_language()
    
    connection_pool = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=20),
        connector=aiohttp.TCPConnector(limit=20, limit_per_host=10)
    )
    
    # 2. LOGIN
    Uid, Pw = '4281893837', '260CF28F2FF49CB27F0687FE978C32D81C0F9A173EDD8995BD44EE4EFB984465'
    print(" [INIT] Logging in Bot...")
    
    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id or not access_token:
        print("Error - Invalid Account")
        return None
    
    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE:
        print("Account Banned / Not Registered!")
        return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    region = MajoRLoGinauTh.region
    ToKen = MajoRLoGinauTh.token
    BotUID = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
    if not LoGinDaTa: return None
    
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP, OnLineporT = OnLinePorTs.split(":")
    ChaTiP, ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    
    # 3. SHOW SUCCESS & ASK UID (IN SELECTED LANG)
    os.system('clear')
    print(render('LEVEL UP', colors=['white', 'green'], align='center'))
    print(f"\n {get_msg('console_online')}")
    print(f" BOT NAME   : {acc_name}")
    print(f" BOT UID    : {BotUID}")
    print(f" BOT REGION : {region}")
    print(f" LANGUAGE   : {SELECTED_LANG.upper()}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        user_uid_input = input(get_msg('input_uid'))
        ADMIN_UID = user_uid_input.strip()
    except: pass

    if ADMIN_UID:
        print(f" [ACTION] Sending Friend Request to {ADMIN_UID}...")
        sent = await SendFriendRequest(ADMIN_UID, ToKen, UrL)
        if sent:
            input(get_msg('prompt_enter'))
    
    # 4. CONNECT
    equie_emote(ToKen, UrL)
    AutHToKen = await xAuThSTarTuP(int(BotUID), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region))
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen))
    
    print(get_msg('console_waiting'))
    
    await asyncio.gather(task1, task2)

async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print("Token Expired! Restarting...")
        except Exception as e:
            print(f"TCP Error - {e} => Restarting...")

if __name__ == '__main__':
    try:
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        pass
