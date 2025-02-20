import os
import importlib
import sys
import random
import json
from zlapi.models import Message
from config import PREFIX, ADMIN

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.huang = self.load_huang()
        self.auto_huang = self.load_auto_huang()
        self.admin_id = ADMIN
        self.adminon = self.load_admin_mode()

        if PREFIX == '':
            print("Prefix hiện tại của bot là 'no prefix'")
        else:
            print(f"Prefix hiện tại của bot là '{PREFIX}'")

    def load_admin_mode(self):
        try:
            with open('modules/cache/admindata.json', 'r') as f:
                data = json.load(f)
                return data.get('adminon', False)
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False

    def save_admin_mode(self):
        with open('modules/cache/admindata.json', 'w') as f:
            json.dump({'adminon': self.adminon}, f)

    def load_huang(self):
        huang = {}
        modules_path = 'modules'
        success_count = 0
        failed_count = 0
        success_huang = []
        failed_huang = []

        for filename in os.listdir(modules_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{modules_path}.{module_name}')
                    
                    if hasattr(module, 'get_huang'):
                        if hasattr(module, 'des'):
                            des = getattr(module, 'des')
                            if all(key in des for key in ['version', 'credits', 'description']):
                                huang.update(module.get_huang())
                                success_count += 1
                                success_huang.append(module_name)
                            else:
                                raise ImportError(f"Lỗi không thể tìm thấy thông tin của lệnh: {module_name}")
                        else:
                            raise ImportError(f"Lệnh {module_name} không có thông tin")
                    else:
                        raise ImportError(f"Module {module_name} không có hàm gọi lệnh")
                except Exception as e:
                    print(f"Không thể load được module: {module_name}. Lỗi: {e}")
                    failed_count += 1
                    failed_huang.append(module_name)

        if success_count > 0:
            print(f"Đã load thành công {success_count} lệnh: {', '.join(success_huang)}")
        if failed_count > 0:
            print(f"Không thể load được {failed_count} lệnh: {', '.join(failed_huang)}")

        return huang

    def load_auto_huang(self):
        auto_huang = {}
        auto_modules_path = 'modules.auto'
        success_count = 0
        failed_count = 0
        success_auto_huang = []
        failed_auto_huang = []

        for filename in os.listdir('modules/auto'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{auto_modules_path}.{module_name}')
                    
                    if hasattr(module, 'get_huang'):
                        if hasattr(module, 'des'):
                            des = getattr(module, 'des')
                            if all(key in des for key in ['version', 'credits', 'description']):
                                auto_huang.update(module.get_huang())
                                success_count += 1
                                success_auto_huang.append(module_name)
                            else:
                                raise ImportError(f"Module {module_name} thiếu các thông tin cần thiết")
                        else:
                            raise ImportError(f"Lệnh {module_name} không có thông tin")
                    else:
                        raise ImportError(f"Module {module_name} không có hàm gọi lệnh")
                except Exception as e:
                    print(f"Không thể load được module: {module_name}. Lỗi: {e}")
                    failed_count += 1
                    failed_auto_huang.append(module_name)

        if success_count > 0:
            print(f"Đã load thành công {success_count} lệnh auto: {', '.join(success_auto_huang)}")
        if failed_count > 0:
            print(f"Không thể load được {failed_count} lệnh auto: {', '.join(failed_auto_huang)}")

        return auto_huang

    def toggle_admin_mode(self, message, message_object, thread_id, thread_type, author_id):
        if author_id == self.admin_id:
            if 'on' in message.lower():
                self.adminon = True
                self.save_admin_mode()
                self.replyMessage("𝑨𝒅𝒎𝒊𝒏 𝑻𝒓𝒖𝒆.", message_object, thread_id, thread_type)
            elif 'off' in message.lower():
                self.adminon = False
                self.save_admin_mode()
                self.replyMessage("𝑨𝒅𝒎𝒊𝒏 𝑭𝒂𝒍𝒔𝒆.", message_object, thread_id, thread_type)
            else:
                self.replyMessage("𝑷𝒍𝒆𝒂𝒔𝒆 𝑼𝒔𝒆 𝒂𝒅𝒎𝒊𝒏𝒎𝒐𝒅𝒆 𝒐𝒏/𝒐𝒇𝒇.", message_object, thread_id, thread_type)
        else:
            self.replyMessage("𝟒𝟎𝟑 𝑭𝒐𝒓𝒃𝒊𝒅𝒅𝒆𝒏:).", message_object, thread_id, thread_type)

    def handle_command(self, message, author_id, message_object, thread_id, thread_type):
        if message.startswith(PREFIX + 'adminmode'):
            self.toggle_admin_mode(message, message_object, thread_id, thread_type, author_id)
            return
        
        auto_command_handler = self.auto_huang.get(message.lower())
        if auto_command_handler:
            auto_command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
            return

        if not message.startswith(PREFIX):
            return

        if self.adminon and author_id != self.admin_id:
            error_message = "𝑨𝒅𝒎𝒊𝒏 𝑻𝒓𝒖𝒆 - 𝒀𝒐𝒖 𝑵𝒐𝒕 𝒂 𝑨𝒅𝒎𝒊𝒏."
            self.replyMessage(error_message, message_object, thread_id, thread_type)
            return

        command_name = message[len(PREFIX):].split(' ')[0].lower()
        
        if command_name == 'scl':
            return 

        command_handler = self.huang.get(command_name)

        if command_handler:
            command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
        else:
            error_message = f"𝑪𝒐𝒎𝒎𝒂𝒏𝒅 '{command_name}' 𝑵𝒐𝒕 𝑭𝒐𝒖𝒏𝒅. 𝑷𝒍𝒆𝒂𝒔𝒆 𝑼𝒔𝒆 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 {PREFIX}𝒔𝒄𝒍"
            self.replyMessage(error_message, message_object, thread_id, thread_type)

    def replyMessage(self, message, message_object, thread_id, thread_type):
        mes = Message(text=message)
        self.client.replyMessage(mes, message_object, thread_id=thread_id, thread_type=thread_type)
