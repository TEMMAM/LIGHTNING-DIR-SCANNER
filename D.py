#!/usr/bin/env python3
import requests
import argparse
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from tqdm import tqdm
import random
import difflib
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║   LIGHTNING DIR SCANNER - ULTRAFAST MODE ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
"""

# Configuration
MAX_THREADS = 50
REQUEST_TIMEOUT = 5
DELAY = 0.05
HOME_SAMPLE_SIZE = 1024

# Locks
print_lock = threading.Lock()
tqdm_lock = threading.Lock()

# User agents list for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"
    " (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
]

# Shared session
session = requests.Session()


homepage_content = b""
base_url = ""

def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def get_homepage_content(url):
    """Fetch homepage content for 404 similarity check."""
    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT, headers=get_random_headers())
        if r.status_code == 200:
            return r.content[:HOME_SAMPLE_SIZE]
    except requests.RequestException:
        pass
    return b""

def is_similar_content(a, b, threshold=0.9):
    """Return True if content similarity is above threshold (0-1)."""
    if not a or not b:
        return False
    seq = difflib.SequenceMatcher(None, a, b)
    return seq.ratio() >= threshold

def is_real_directory(url):
    try:
        headers = get_random_headers()
        r = session.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        with print_lock:
            print(f"[DEBUG] {url} → {r.status_code}")
        if r.status_code != 200:
            return False

        content_sample = r.content[:HOME_SAMPLE_SIZE]
        # If content is very similar to homepage, treat as 404-like (soft 404)
        if is_similar_content(content_sample, homepage_content):
            return False
        return True

    except requests.RequestException as e:
        with print_lock:
            print(f"[ERROR] {url} → {e}")
        return False

def scan_directory(base_url, directory, progress_bar):
    url = urljoin(base_url, directory)
    found = None
    if is_real_directory(url):
        with print_lock:
            print(f"{Fore.GREEN}[Found]{Style.RESET_ALL} {url}")
        found = url
    with tqdm_lock:
        progress_bar.update(1)
    return found

def main():
    global homepage_content
    global base_url

    print(BANNER)

    parser = argparse.ArgumentParser(description="Lightning-fast directory scanner with smart 404 detection, colors, and UA randomization")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=MAX_THREADS, help=f"Threads (default: {MAX_THREADS})")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()
    base_url = args.url if args.url.endswith('/') else args.url + '/'

    print(f"{Fore.YELLOW}[*]{Style.RESET_ALL} Fetching homepage content for 404 detection...")
    homepage_content = get_homepage_content(base_url)

    try:
        with open(args.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            directories = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[!]{Style.RESET_ALL} Wordlist not found: {args.wordlist}")
        return

    print(f"{Fore.YELLOW}[*]{Style.RESET_ALL} Launching {args.threads} threads...")
    print(f"{Fore.YELLOW}[*]{Style.RESET_ALL} Scanning {len(directories)} paths (ultra-fast mode)")
    print(f"{Fore.YELLOW}[*]{Style.RESET_ALL} Press Ctrl+C to stop\n")

    start_time = time.time()
    found_dirs = []

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            with tqdm(total=len(directories), desc="Scanning", ncols=80) as progress_bar:
                futures = [
                    executor.submit(scan_directory, base_url, d, progress_bar)
                    for d in directories
                ]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        found_dirs.append(result)
                    time.sleep(DELAY)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Scan stopped by user")

    elapsed = time.time() - start_time
    print(f"\n{Fore.YELLOW}[*]{Style.RESET_ALL} Scan completed in {elapsed:.2f} seconds!")

    if found_dirs:
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Found {len(found_dirs)} real directories:")
        for url in found_dirs:
            print(f" - {Fore.CYAN}{url}{Style.RESET_ALL}")

        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write("\n".join(found_dirs))
                print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Results saved to {args.output}")
            except Exception as e:
                print(f"{Fore.RED}[!]{Style.RESET_ALL} Error saving results: {e}")
    else:
        print(f"{Fore.RED}[!]{Style.RESET_ALL} No real directories found")

if __name__ == "__main__":
    main()
