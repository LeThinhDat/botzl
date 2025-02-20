import threading
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, BOT_ID ,PREFIX
from ngoc import CommandHandler
from zlapi import ZaloAPI
from zlapi.models import Message, MessageStyle, MultiMsgStyle
from colorama import Fore, Style, init
import requests
from MapLoveDl import MusicDownloader

init(autoreset=True)

class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies, bot_id):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.command_handler = CommandHandler(self)
        self.del_enabled = {}
        self.default_del_enabled = True
        self.bot_id = bot_id
        self.music_downloader = MusicDownloader()
        self.next_step = {}
        self.user_data = {}

    def make_color(self, color_symbol: str, color_text: str, font: str) -> MultiMsgStyle:
        style = [
            MessageStyle(offset=0, length=1000, style='font', size=font, auto_format=False),
            MessageStyle(offset=0, length=1, style='color', color=color_symbol, auto_format=False),
            MessageStyle(offset=2, length=1000, style='color', color=color_text, auto_format=False)
        ]
        return MultiMsgStyle(style)

    def get_count(self, string: str, word: str) -> list:
        indices = []
        start = 0
        while True:
            idx = string.find(word, start)
            if idx == -1:
                break
            indices.append(idx)
            start = idx + 1
        return indices

    def handle_message(self, mid, author_id, message, message_object, thread_id, thread_type):
        felic = PREFIX + "scl"
        print(f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
              f"**Message Details:**\n"
              f"- **Message:** {Style.BRIGHT}{message} {Style.NORMAL}\n"
              f"- **Author ID:** {Fore.MAGENTA}{Style.BRIGHT}{author_id} {Style.NORMAL}\n"
              f"- **Thread ID:** {Fore.YELLOW}{Style.BRIGHT}{thread_id}{Style.NORMAL}\n"
              f"- **Thread Type:** {Fore.BLUE}{Style.BRIGHT}{thread_type}{Style.NORMAL}\n"
              f"- **Message Object:** {Fore.RED}{Style.BRIGHT}{message_object}{Style.NORMAL}\n"
              f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
              )
        contains_link = False
        if isinstance(message, str) and ("t.me/" in message or "zalo.me" in message):
            contains_link = True

        elif hasattr(message_object, 'content') and isinstance(message_object.content, dict):
            if 'href' in message_object.content and ("t.me/" in message_object.content['href'] or "zalo.me" in message_object.content['href']):
                contains_link = True
            elif "t.me/" in message_object.content.get('text', '') or "zalo.me" in message_object.content.get('text', ''):
                contains_link = True

        if contains_link and author_id != self.bot_id:
            try:
                self.deleteGroupMsg(
                    msgId=message_object.msgId,
                    ownerId=author_id,
                    clientMsgId=message_object.cliMsgId,
                    groupId=thread_id
                )
                print(f"Deleted a message containing a link from {author_id} in group {thread_id}")
            except Exception as e:
                print(f"Error while deleting message: {e}")
        message_content = self.extract_message_content(message, message_object)
        if not message_content:
            return

        if isinstance(message, str):
            self.command_handler.handle_command(message, author_id, message_object, thread_id, thread_type)

        if message_content.startswith(felic):
            self.handle_scl_command(message_content, message_object, thread_id, thread_type, author_id)
        elif author_id in self.next_step and self.next_step[author_id] == 'wait_select':
            self.handle_selection(message_content, message_object, thread_id, thread_type, author_id)
        if self.del_enabled.get(thread_id, self.default_del_enabled):
            contains_link = False

            if isinstance(message, str) and ("t.me/" in message or "zalo.me" in message):
                contains_link = True
            elif hasattr(message_object, 'content') and isinstance(message_object.content, dict):
                if 'href' in message_object.content and ("t.me/" in message_object.content['href'] or "zalo.me" in message_object.content['href']):
                    contains_link = True

            if contains_link and author_id != self.bot_id:
                try:
                    self.deleteGroupMsg(
                        msgId=message_object.msgId,
                        ownerId=author_id,
                        clientMsgId=message_object.cliMsgId,
                        groupId=thread_id
                    )
                    print(f"Deleted a message containing a link from {author_id} in group {thread_id}")
                except Exception as e:
                    print(f"Error while deleting message: {e}")


    def extract_message_content(self, message, message_object):
        if isinstance(message_object.content, str):
            return message_object.content
        elif isinstance(message, str):
            return message
        print(f"Warning: Received non-string message: {type(message)}")
        return None

    def handle_scl_command(self, message_content, message_object, thread_id, thread_type, author_id):
        args = message_content.split()
        if len(args) < 2:
            self.replyMessage(
                Message(text="• 𝑼𝒔𝒆 ?𝒔𝒄𝒍 𝑵𝒂𝒎𝒆 𝑺𝒐𝒏𝒈"),
                message_object, thread_id, thread_type)
            return

        keyword = message_content[4:].strip()
        concac = self.music_downloader.find_with_keyword(keyword)
        if not concac:
            self.replyMessage(
                Message(text="• 𝑵𝒐 𝑹𝒆𝒔𝒖𝒍𝒕𝒔 𝑭𝒐𝒖𝒏𝒅"),
                message_object, thread_id, thread_type)
            return

        self.process_music_collection(concac, author_id, message_object, thread_id, thread_type)

    def process_music_collection(self, concac, author_id, message_object, thread_id, thread_type):
        collection = concac['collection']
        collection = [x for x in collection if list(x.keys())[0] != 'avatar_url']
        response_text = ''
        styles = []
        n = 0
        styles.append(MessageStyle(offset=0, length=1000, style='font', size='13', auto_format=False))
        styles.append(MessageStyle(offset=0, length=1000, style='color', color='ced6f0', auto_format=False))
        self.user_data[author_id] = []
        for data in collection:
            z = data.get('media', {}).get('transcodings', [])
            if not z:
                continue
            n += 1
            title = data['title']
            duration = data['duration']
            link = next((khoi['url'] for khoi in z if khoi['format']['protocol'] == 'progressive'), None)
            response_text += f'{n} • {title} || {self.music_downloader.convertMillis(duration)}\n'
            self.user_data[author_id].append({'link': link, 'duration': duration, 'title': title})
            styles.append(MessageStyle(offset=self.get_count(response_text, '•')[n-1], length=1, style='color', color='b3d9b0', auto_format=False))

        self.replyMessage(Message(text=response_text), message_object, thread_id, thread_type,ttl=30000)
        self.replyMessage(Message(text='• 𝑹𝒆𝒑𝒍𝒚 𝑻𝒐 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝑨𝒏𝒅 𝑪𝒉𝒐𝒔𝒆 𝑪𝒐𝒖𝒏𝒕 - 𝑫𝒆𝒍𝒆𝒕𝒆𝑴𝒔𝒈 𝑻𝒂𝒈 @𝑼𝒔𝒆𝒓'), message_object, thread_id, thread_type, ttl=30000)
        self.next_step[author_id] = 'wait_select'

    def handle_selection(self, message_content, message_object, thread_id, thread_type, author_id):
        if not message_object.quote:
            self.replyMessage(
                Message(text="• 𝑹𝒆𝒑𝒍𝒚 𝑻𝒐 𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝑨𝒏𝒅 𝑪𝒉𝒐𝒔𝒆 𝑪𝒐𝒖𝒏𝒕 - 𝑫𝒆𝒍𝒆𝒕𝒆𝑴𝒔𝒈 𝑻𝒂𝒈 @𝑼𝒔𝒆𝒓"),
                message_object, thread_id, thread_type,ttl=30000)
            return

        try:
            selection = int(message_content.strip()) - 1
            selected_song = self.user_data[author_id][selection]
            url_down = selected_song['link']
            duration = selected_song['duration']
            title = selected_song['title']

            if (int(duration) // (1000 * 90 * 90)) > 1 or (int(duration) // (1000 * 90)) % 90 > 80:
                self.replyMessage(
                    Message(text="• 𝑷𝒍𝒆𝒂𝒔𝒆 𝑪𝒉𝒐𝒐𝒔𝒆 𝒂 𝑺𝒐𝒏𝒈 𝑼𝒏𝒅𝒆𝒓 𝟖𝟎 𝑴𝒊𝒏𝒖𝒕𝒆𝒔 𝒊𝒏 𝑳𝒆𝒏𝒈𝒕𝒉"),
                    message_object, thread_id, thread_type)
                return

            self.replyMessage(Message(text='• 𝑾𝒂𝒊𝒕 𝑭𝒐𝒓 𝑫𝒐𝒘𝒏𝒍𝒐𝒂𝒅 𝑨𝒏𝒅 𝑺𝒆𝒏𝒕 𝑴𝒖𝒔𝒊𝒄'),
                              message_object, thread_id, thread_type,ttl=30000)
            
            url = self.music_downloader.get_url_down(url_down)
            if url:
                voice_url = self.music_downloader.catbox(url)
                if voice_url:
                    self.sendRemoteVoice(voice_url, thread_id, thread_type)
                    self.replyMessage(Message(text=f"""
• 𝑵𝒂𝒎𝒆 𝑴𝒖𝒔𝒊𝒄: {title}
• 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏: {self.music_downloader.convertMillis(duration)}
• 𝑩𝒐𝒕 𝑺𝒐𝒖𝒏𝒅 𝑶𝒏 𝑪𝒍𝒐𝒖𝒅 
• 𝑩𝒐𝒕 𝑶𝒇     ⃝ 𝑴𝒂𝒑ဗီူဗီူ - 𝑫𝒖𝒐𝒏𝒈 𝑵𝒈𝒐𝒄
• 𝑴𝒂𝒑 𝑩𝒆𝒐 𝑳𝒐𝒗𝒆 𝑺𝒂𝒓𝒊𝒆𝒍 𝑫𝒂𝒓𝒍𝒊𝒈𝒉𝒕
•    ⃝ 𝑴𝒂𝒑ဗီူဗီူ 𝑳𝒐𝒗𝒆   ⃝ 𝑫𝒍ဗီူဗီူ"""), message_object, thread_id, thread_type)


        except Exception as e:
            print(e)
        finally:
            self.next_step.pop(author_id, None)
            self.user_data.pop(author_id, None)


    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        threading.Thread(target=self.handle_message, args=(mid, author_id, message, message_object, thread_id, thread_type)).start()

if __name__ == "__main__":
    client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, BOT_ID)
    client.listen(thread=True)
