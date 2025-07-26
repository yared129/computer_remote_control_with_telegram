from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes, filters, ApplicationBuilder, MessageHandler
import threading
import datetime
import os
import asyncio
import subprocess
import pyautogui
import time
import zipfile

API_TOKEN = "API_TOKEN"
LOGGED_IN = []
global loop
global loop_telegram
loop_telegram = True

global IS_READING_DIRECTORY
global IS_READING_SCREEN 
global IS_DOWNLOADING
global IS_UPLOADING
global FINISHED
global SERVER_STARTED
global RETRYING

global PERMISSION_SCREENSHOT
global PERMISSION_ACCESS_DIRECTORY
global PERMISSION_DOWNLOAD
global PERMISSION_UPLOAD

IS_READING_DIRECTORY = False
IS_READING_SCREEN = False
IS_DOWNLOADING = False
IS_UPLOADING = False
FINISHED = True
SERVER_STARTED = False
RETRYING = False

PERMISSION_SCREENSHOT = True
PERMISSION_ACCESS_DIRECTORY = True
PERMISSION_DOWNLOAD = True
PERMISSION_UPLOAD = True
PERMISSION_COMMAND_PROMPT = True

date = datetime.datetime.now()
day = date.day
month = date.month
hour = date.hour

password = f"{month*24}{day*23}{hour*22}"

def run_telegram_bot():
    global loop_telegram
    global loop
    global SERVER_STARTED
    global RETRYING
    try:
        async def run_bot():
            print("Starting Bot Application....")
            tg_application = ApplicationBuilder().token(API_TOKEN).build()
            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                await update.message.reply_text("Welcome to the Simple Telegram Bot!")
                
            async def changePassword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                chat_id = update._effective_chat.id
                print("chat ID: ",chat_id)
                global FINISHED
                text = update.message.text
                current_datetime = datetime.datetime.now()
                day = current_datetime.day
                hour = current_datetime.hour
                if len(text) > 17:
                    if text[10:] == f"Something{day}{hour}":
                        LOGGED_IN.append(chat_id)
                        FINISHED = False
                        await update.message.reply_text(f"Welcome!\nCWD\n{os.getcwd()}")
                    else:
                        if chat_id in LOGGED_IN:
                            LOGGED_IN.remove(chat_id)
                        await update.message.reply_text("Wrong password.")
                else:
                    await update.message.reply_text("text recieved!")
            
            async def handle_message(update, context):
                chat_id = update._effective_chat.id
                print("chat ID: ",chat_id)
                global IS_READING_DIRECTORY
                global IS_READING_SCREEN 
                global IS_DOWNLOADING
                global IS_UPLOADING
                global FINISHED
                
                global PERMISSION_SCREENSHOT
                global PERMISSION_ACCESS_DIRECTORY
                global PERMISSION_DOWNLOAD
                global PERMISSION_UPLOAD
                
                if update.message.text:
                    print("Received:", update.message.text)
                    text:str = update.message.text
                    if chat_id in LOGGED_IN:
                        current_datetime = datetime.datetime.now()
                        current_time = current_datetime.time()
                        try:
                            if text.lower()=="ls":
                                if PERMISSION_ACCESS_DIRECTORY:
                                    IS_READING_DIRECTORY = True
                                    IS_READING_SCREEN = False
                                    IS_DOWNLOADING = False
                                    IS_UPLOADING = False
                                    FINISHED = False
                                    res = "List of Directories\n\n"
                                    for x in os.listdir():
                                        res+=x+"\n"
                                    await update.message.reply_text(res+"\n"+os.getcwd())
                                else:
                                    await update.message.reply_text("Permission Denied!")
                            elif text.lower().startswith("unzipp "):
                                if PERMISSION_ACCESS_DIRECTORY:
                                    filename = text[7:]
                                    if filename.endswith(".zip"):
                                        try:
                                            with zipfile.ZipFile(filename, 'r') as zipf:
                                                zipf.extractall('extracted_files')
                                        except FileNotFoundError:
                                            await update.message.reply_text("File not Found!")
                                        except:
                                            await update.message.reply_text("File not unzipped. Please try again...")
                                else:
                                    await update.message.reply_text("Permission Denied!")
                            elif text.lower()=="finished" or text.lower()=="logout":
                                IS_READING_DIRECTORY = False
                                IS_READING_SCREEN = False
                                IS_DOWNLOADING = False
                                IS_UPLOADING = False
                                FINISHED = True
                                LOGGED_IN.remove(chat_id)
                                await update.message.reply_text("You have Logged out successfully!\nYou can always log back in by entering your password.")
                            elif text.lower().startswith("cd "):
                                if PERMISSION_ACCESS_DIRECTORY:
                                    IS_READING_DIRECTORY = True
                                    IS_READING_SCREEN = False
                                    IS_DOWNLOADING = False
                                    IS_UPLOADING = False
                                    FINISHED = False
                                    try:
                                        os.chdir(text[3:])
                                        await update.message.reply_text(os.getcwd())
                                    except:
                                        await update.message.reply_text("Directory doesn't exist!")
                                else:
                                    await update.message.reply_text("Permission Denied!")
                            elif text.lower()=="screenshot":
                                if PERMISSION_SCREENSHOT:
                                    IS_READING_DIRECTORY = False
                                    IS_READING_SCREEN = True
                                    IS_DOWNLOADING = False
                                    IS_UPLOADING = False
                                    FINISHED = False
                                    image_name = f"Screenshot-{current_time.hour}-{current_datetime.minute}-{current_datetime.second}.png"
                                    f = open(image_name, "wb")
                                    f.close()
                                    screenshot = pyautogui.screenshot()
                                    screenshot.save(image_name)
                                    try:
                                        with open(image_name, 'rb') as photo:
                                            await update.message.reply_photo(photo, caption="Here is your screenshoted image!")
                                        await update.message.reply_text("File sent successfully!")
                                    except FileNotFoundError:
                                        await update.message.reply_text("Error: File not found.")
                                    except Exception as e:
                                        await update.message.reply_text(f"An error occurred: {e}")
                                else:
                                    await update.message.reply_text("Permission Denied!")
                            elif text.lower().startswith("download "):
                                if PERMISSION_UPLOAD:
                                    IS_READING_DIRECTORY = False
                                    IS_READING_SCREEN = False
                                    IS_DOWNLOADING = True
                                    IS_UPLOADING = False
                                    FINISHED = False
                                    file_path = text[9:]
                                    try:
                                        with open(file_path, 'rb') as file:
                                            await context.bot.send_document(chat_id=chat_id, document=file)
                                        await update.message.reply_text("File sent successfully!")
                                    except FileNotFoundError:
                                        await update.message.reply_text("Error: File not found.")
                                    except Exception as e:
                                        await update.message.reply_text(f"An error occurred: {e}")
                                else:
                                    await update.message.reply_text("Permission Denied!")
                            elif len(text)>0:
                                if PERMISSION_COMMAND_PROMPT:
                                    IS_READING_DIRECTORY = True
                                    IS_READING_SCREEN = False
                                    IS_DOWNLOADING = False
                                    IS_UPLOADING = False
                                    FINISHED = False
                                    cmd = subprocess.Popen(text,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                                    output = cmd.stdout.read() + cmd.stderr.read()
                                    output = str(output,'utf-8')
                                    output = output+os.getcwd()
                                    await update.message.reply_text(output)
                                else:
                                    await update.message.reply_text("Permission Denied!")
                        except Exception as e:
                            await update.message.reply_text("bingo not changed!"+str(e))
                    else:
                        await update.message.reply_text("Hi!Nice to meet you!")
                
                elif update.message.document:
                    if PERMISSION_DOWNLOAD:
                        document = update.message.document
                        if chat_id in LOGGED_IN:
                            file_name = document.file_name
                            mime_type = document.mime_type
                            file_size = document.file_size
                            file_id = document.file_id
                            unique_id = document.file_unique_id
                            IS_READING_DIRECTORY = False
                            IS_READING_SCREEN = False
                            IS_DOWNLOADING = False
                            IS_UPLOADING = True
                            FINISHED = False
                            file = await context.bot.get_file(file_id)
                            await file.download_to_drive(f"./{file_name}")
                            await update.message.reply_text("File uploaded sucessfully.")
                        else:
                            await update.message.reply_text("Permission denied!")
                    else:
                        await update.message.reply_text("Permission Denied!")
                elif update.message.photo:
                    if PERMISSION_DOWNLOAD:
                        photo_file = update.message.photo[-1]
                        if chat_id in LOGGED_IN:
                            file_object = await context.bot.get_file(photo_file.file_id)
                
                            await file_object.download_to_drive(f'received_image_{photo_file.file_id}.jpg')

                            await update.message.reply_text("Image uploaded sucessfully!")
                        else:
                            await update.message.reply_text("Permission denied!")
                    else:
                        await update.message.reply_text("Permission Denied!")
                elif update.message.audio:
                    if PERMISSION_DOWNLOAD:
                        audio_file = update.message.audio
                        if chat_id in LOGGED_IN:
                            file_name = audio_file.file_name
                            file_id = audio_file.file_id
                            unique_id = audio_file.file_unique_id
                            IS_READING_DIRECTORY = False
                            IS_READING_SCREEN = False
                            IS_DOWNLOADING = False
                            IS_UPLOADING = True
                            FINISHED = False
                            file = await context.bot.get_file(file_id)
                            await file.download_to_drive(f"./{file_name}")
                            await update.message.reply_text("Audio uploaded sucessfully.")
                        else:
                            await update.message.reply_text("Permission denied!")
                    else:
                        await update.message.reply_text("Permission Denied!")
                else:
                    if chat_id in LOGGED_IN:
                        await update.message.reply_text("Message not Valid. Please try again!")
                    else:
                        await update.message.reply_text("Hi! Nice to meet you.")
                        
            async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                await update.message.reply_text(
                    'I can respond to the following commands:\n/start - Start the bot\n/help - Get help information'
                )
            tg_application.add_handler(CommandHandler('start', start))
            tg_application.add_handler(CommandHandler('help', help_command))
            tg_application.add_handler(CommandHandler('password', changePassword))
            tg_application.add_handler(MessageHandler(filters.ALL, handle_message))
            
            await tg_application.initialize()
            await tg_application.start()
            print("Polling Bot Application...")
            global SERVER_STARTED
            global RETRYING
            SERVER_STARTED = True
            RETRYING = False
            # await tg_application.run_polling()
            await tg_application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            await asyncio.Future()
            # await tg_application.wait_until_closed()
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    except:
        SERVER_STARTED = False
        RETRYING = True
        if loop_telegram:
            run_telegram_bot()
    
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 500)  # Set a fixed minimum size
        self.setWindowTitle("Online Remote Controller")
        self.setWindowIcon(QIcon("installer_logo.jpg"))
        self.setObjectName("main")
        self.setStyleSheet("background-color:black; color: white;")
        label = QLabel("Online Remote Controller")
        label.setStyleSheet("font-size:28px;")
        layout = QVBoxLayout()
        layout.addWidget(label)
        
        directory_hlayout = QHBoxLayout()
        directory_label = QLabel("Access Directory...........................")
        self.directory_toggle = QPushButton("Allowed")
        self.directory_toggle.clicked.connect(self.togglo_permission_directory)
        directory_hlayout.addWidget(directory_label, Qt.AlignCenter)
        directory_hlayout.addWidget(self.directory_toggle, Qt.AlignRight)
        layout.addLayout(directory_hlayout)
        
        screenshot_hlayout = QHBoxLayout()
        screenshot_label = QLabel("Access to Screenshot........................")
        self.screenshot_toggle = QPushButton("Allowed")
        self.screenshot_toggle.clicked.connect(self.togglo_permission_screenshot)
        screenshot_hlayout.addWidget(screenshot_label, Qt.AlignCenter)
        screenshot_hlayout.addWidget(self.screenshot_toggle, Qt.AlignRight)
        layout.addLayout(screenshot_hlayout)
        
        download_hlayout = QHBoxLayout()
        download_label = QLabel("Access to Download to this computer.........")
        self.download_toggle = QPushButton("Allowed")
        self.download_toggle.clicked.connect(self.togglo_permission_download)
        download_hlayout.addWidget(download_label, Qt.AlignCenter)
        download_hlayout.addWidget(self.download_toggle, Qt.AlignRight)
        layout.addLayout(download_hlayout)
        
        upload_hlayout = QHBoxLayout()
        upload_label = QLabel("Access to Upload from this computer........")
        self.upload_toggle = QPushButton("Allowed")
        self.upload_toggle.clicked.connect(self.togglo_permission_upload)
        upload_hlayout.addWidget(upload_label, Qt.AlignCenter)
        upload_hlayout.addWidget(self.upload_toggle, Qt.AlignRight)
        layout.addLayout(upload_hlayout)
        
        cmd_hlayout = QHBoxLayout()
        cmd_label = QLabel("Access to Command Prompt...................")
        self.cmd_toggle = QPushButton("Allowed")
        self.cmd_toggle.clicked.connect(self.togglo_permission_cmd)
        cmd_hlayout.addWidget(cmd_label, Qt.AlignCenter)
        cmd_hlayout.addWidget(self.cmd_toggle, Qt.AlignRight)
        layout.addLayout(cmd_hlayout)
        
        self.label = QLabel("Please wait until the developer finishes installing applications...")
        layout.addWidget(self.label)
        layout.setAlignment(label, Qt.AlignCenter)
        layout.setAlignment(self.label, Qt.AlignCenter)
        self.setLayout(layout)
        self.t = None
        
    def togglo_permission_directory(self):
        global PERMISSION_ACCESS_DIRECTORY
        if self.directory_toggle.text()=="Allowed":
            PERMISSION_ACCESS_DIRECTORY = False
            self.directory_toggle.setText("Not Allowed")
        else:
            PERMISSION_ACCESS_DIRECTORY = True
            self.directory_toggle.setText("Allowed")
            
        
    def togglo_permission_screenshot(self):
        global PERMISSION_SCREENSHOT
        if self.screenshot_toggle.text()=="Allowed":
            PERMISSION_SCREENSHOT = False
            self.screenshot_toggle.setText("Not Allowed")
        else:
            PERMISSION_SCREENSHOT = True
            self.screenshot_toggle.setText("Allowed")
            
    def togglo_permission_download(self):
        global PERMISSION_DOWNLOAD
        if self.download_toggle.text()=="Allowed":
            PERMISSION_DOWNLOAD = False
            self.download_toggle.setText("Not Allowed")
        else:
            PERMISSION_DOWNLOAD = True
            self.download_toggle.setText("Allowed")
            
    def togglo_permission_upload(self):
        global PERMISSION_UPLOAD
        if self.upload_toggle.text()=="Allowed":
            PERMISSION_UPLOAD = False
            self.upload_toggle.setText("Not Allowed")
        else:
            PERMISSION_UPLOAD = True
            self.upload_toggle.setText("Allowed")
            
    def togglo_permission_cmd(self):
        global PERMISSION_COMMAND_PROMPT
        if self.cmd_toggle.text()=="Allowed":
            PERMISSION_COMMAND_PROMPT = False
            self.cmd_toggle.setText("Not Allowed")
        else:
            PERMISSION_COMMAND_PROMPT = True
            self.cmd_toggle.setText("Allowed")
        
    def update_label(self):
        # QTimer.singleShot(0, self.update_labels)
        while True:
            if RETRYING:
                self.label.setText("There is no connection. Retrying...")
            elif not SERVER_STARTED:
                self.label.setText("Checking for connection...")
            elif IS_READING_DIRECTORY:
                self.label.setText("Developer is accessing directories.")
            elif IS_READING_SCREEN:
                self.label.setText("Developer is taking screenshot.")
            elif IS_DOWNLOADING:
                self.label.setText("Developer is uploading files.")
            elif IS_UPLOADING:
                self.label.setText("Developer is downloading files into this computer.")
            elif FINISHED:
                self.label.setText("Developed has't signed in yet.")
            else:
                self.label.setText("Please wait until the developer finishes installing applications...")
            time.sleep(0.5)
        
    def start_telegram(self):
        self.t = threading.Thread(target=run_telegram_bot)
        self.t.start()
        
    def closeEvent(self, event):
        global loop
        global loop_telegram
        loop_telegram = False
        if self.t != None:
            loop.call_soon_threadsafe(loop.stop)
            self.t.join()
        
class PasswordChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("installer_logo.jpg"))
        self.setWindowTitle("Online Remote Controller")
        self.setStyleSheet("background-color:black; color: white;")

def run_main():
        widget.show()
        text, ok = QInputDialog.getText(widget,"Installer", "Enter Password:")
        if ok and text:
            if text==str(password):
                widget.hide()
                window.start_telegram()
                threading.Thread(target=window.update_label, daemon=True).start()
                window.show()
                sys.exit(app.exec_())
            else:
                reply = QMessageBox.question(None, "Confirm", "Wrong password!\nDo you want to try again?",
                                    QMessageBox.Yes | QMessageBox.No)
                if reply==QMessageBox.Yes:
                    run_main()
            
if __name__=="__main__":
    # This is something
    app = QApplication(sys.argv)
    window = MainWidget()
    widget = PasswordChecker()

    run_main()
    