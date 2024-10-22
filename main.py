import argparse
import datetime
import requests
import time

SUBMIT_URL = "https://conjuguemos.com/verb/submit"
VOCAB_CHART_URL = "https://conjuguemos.com/vocabulary/vocab_chart/"
VERB_CHART_URL = "https://conjuguemos.com/verb/verb_chart/"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

def log(message: str, level="INFO"):
    print(f"[Hackeasteis] [{datetime.datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]}] [{level}] {message}")

current = lambda: int(time.time())

def build_cookies(cooke_string: str):
    # TODO: Parse cookie string
    return {
        'cookie_confirm': 'true',
        '_gid': 'GA1.2.571888667.1728411642',
        'ci_session': 'ujbc36n0s9lbhfejscmtsatopiq22lp3',
        '_gat_gtag_UA_24549138_1': '1',
        '_ga': 'GA1.1.1586623348.1723749248',
        '_ga_T1K7JW1579': 'GS1.1.1728411642.11.1.1728413513.0.0.0',
    }

def build_headers(activity_id: int):
    return {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://conjuguemos.com',
        'Referer': f'https://conjuguemos.com/verb/homework/{activity_id}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Opera GX";v="113", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

def build_data(activity_id: int, title: str, t: int, attempts: list[list[str, bool]]):
    return {
        'token': 'qxerymw',
        'activity_id': str(activity_id),
        'assignment_id': '0',
        'title': title,
        'mode': 'homework',
        'activity_start': current() - t,
        'activity_end': current(),
        'time': time.strftime('%M:%S', time.gmtime(t)),
        'data[attemps]': [[attempt[0], 1 if attempt[1] else 0, '0', '0', '0', '0', '0'] for attempt in attempts],
        'data[total_attemps]': len(attempts),
        'data[valid_attemps]': len([attempt for attempt in attempts if attempt[1]])
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--id", type=int, help="Assignment ID", required=True)

    args = parser.parse_args()

    page = ""
    r = requests.get(f"{VOCAB_CHART_URL}{args.id}", headers=UA)
    if r.status_code == 200:
        page = r.content.decode("utf-8")
    else:
        r = requests.get(f"{VERB_CHART_URL}{args.id}", headers=UA)
        if r.status_code == 200:
            print(f"{VERB_CHART_URL}{args.id}")
            page = r.content.decode("utf-8")
            print("wat da flieep")
        else:
            log("Invalid assignment ID", "ERROR")
            exit(1)
    print(page)

    cookies = build_cookies("")
    headers = build_headers(args.id)
    data = build_data(args.id, "Present Tense", 60, [["hablar", True], ["comer", True], ["vivir", True]])

    # response = requests.post(SUBMIT_URL, cookies=cookies, headers=headers, data=data)
    # print(response.json())