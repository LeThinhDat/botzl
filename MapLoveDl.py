import requests
import time

class MusicDownloader:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Connection": "keep-alive",
            "Dnt": "1",
            "Host": "api-v2.soundcloud.com",
            "Origin": "https://soundcloud.com",
            "Referer": "https://soundcloud.com/",
            "Sec-Ch-Ua": '"Chromium";v="125", "Not.A/Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "X-Datadome-Clientid": "KKzJxmw11tYpCs6T24P4uUYhqmjalG6M"
        }

    def get_url_down(self, progressive_url):
        params = {"client_id": "KKzJxmw11tYpCs6T24P4uUYhqmjalG6M"}
        try:
            response = requests.get(progressive_url, headers=self.headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            check = response_json.get('data', None)
            if check:
                url = check.get('url', None)
            else:
                url = response_json.get('url', None)
            return url if url else False
        except requests.RequestException as e:
            print(f"Error in get_url_down: {e}")
            return False

    def catbox(self, url):
        cookies = {'PHPSESSID': 'gvbvau511395ct0o4472qr5tge'}
        headers = {
            'authority': 'catbox.moe',
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-AU;q=0.6,en;q=0.5,fr-FR;q=0.4,fr;q=0.3,en-US;q=0.2',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://catbox.moe',
            'referer': 'https://catbox.moe/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 12; SM-A037F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {'reqtype': 'urlupload', 'userhash': '', 'url': url}
        try:
            response = requests.post('https://catbox.moe/user/api.php', cookies=cookies, headers=headers, data=data).text
            return response
        except requests.RequestException as e:
            print(f"Error in catbox: {e}")
            return False

    def find_with_keyword(self, keyword):
        params = {
            'q': keyword,
            'client_id': 'KKzJxmw11tYpCs6T24P4uUYhqmjalG6M',
            'stage': '',
        }
        try:
            response = requests.get('https://api-mobi.soundcloud.com/search', params=params, headers=self.headers).json()
            return response
        except requests.RequestException as e:
            print(f"Error in find_with_keyword: {e}")
            return False

    def convertMillis(self, millis):
        millis = int(millis)
        seconds = int(millis / 1000) % 60
        minutes = int(millis / (1000 * 60)) % 60
        hours = int(millis / (1000 * 60 * 60))
        return f'{hours}:{minutes}:{seconds}'