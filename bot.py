import os
from pyrogram import Client , filters
import os
import aioftp
import asyncio

start_text = '''
Hello, this is an FTP management bot
To start, send your file to the robot
this robot maded by : Redx
'''
file_name_error = '''
⚠️ Unfortunately, an error occurred while processing the file name.
this robot maded by : Redx
'''
dl_text = '📥 Downloading from Telegram servers...'
upload_text = '📤 Uploading to host...'
upload_error_text = 'Error while uploading to host❌'
save_error_text = 'Error while saving file on server❌'
dl_error_text = 'Error when downloading a file from Telegram❌'
dl_url_text = '''
The upload to the host was done successfully✅
🔅 File download link: 
🔗 {}{}
.
this robot maded by : Redx
'''
#API ID & API Hash -----> my.telegram.org
api_id = 9565562
api_hash = 'c585bbedfc6fef61f57034e46d8812f3'
#Bot Token -----> @BotFather
token = '5425942334:AAEDiezxCRvsUd2BCI0EKBZ9Y5vN8JB0mnc'
#Session Name -----> optional
session_name = 'FTP_Manager'
#The robot admin (the person who can give orders to the robot.) -----> @myidbot
admins = [1117638015,1117638015,1117638015,2033814123]
# Chat id to send technical logs
dev = 2033814123
# When a file is sent to the bot, first that file is downloaded from the Telegram repository and stored in the bot's server.
# Here you need to specify its temporary storage path
# For example, I set the bot to save the downloaded file in the current path (the path where config.py file is located).
dl_path = os.path.abspath(os.getcwd()) + '/Files/all'
# The upload path where we give FTP access to the bot.
ftp_path = '/Files/all'
# The files are temporarily downloaded after they are on the bot server. They are uploaded to another host through FTP.
# Here we have to give FTP access to the bot.
ftp_ip = '109.70.148.48'
ftp_username = 'android@golexor.com'
ftp_password = 'Iman@0911'
ftp_domain = 'https://ftp.golexor.com'

app = Client(session_name,api_id=api_id,api_hash=api_hash,bot_token=token)
async def manager_text_handler(chat_id,msg):
    pass
async def user_text_handler(chat_id,msg):
    pass

async def check_file_name(file_name,file_date=None,mim_type=None):
    new_file_name = file_name
    new_file_date = 'video_' + str(file_date)
    try :
        if not file_name :
            if ' ' in new_file_date :
                new_file_date = new_file_date.replace(' ','ـ')
            return new_file_date+'.'+mim_type
        else :
            if ' ' in file_name :
                new_file_name = new_file_name.replace(' ','ـ')
            elif '💥' in file_name :
                new_file_name = new_file_name.replace('💥','ـ')
            if '"' in file_name :
                new_file_name = new_file_name.replace('"','ـ')
            else :
                return new_file_name
            return new_file_name
    except Exception as e :
        await app.send_message(dev, f'Error in check_file_name : {str(e)}')
        return False

async def get_file_name(message):
    chat_id = message.chat.id
    file_name = 'None'
    try:
        if message.video:
            if str(message.video.file_name) == 'None':
                file_name = await check_file_name(False,message.video.file_unique_id,message.video.mime_type.split('/')[1])
            else  :
                file_name = await check_file_name(message.video.file_name,message.video.file_unique_id)
        elif message.audio:
            file_name = await check_file_name(message.audio.file_name)
        elif message.document:
            file_name = await check_file_name(message.document.file_name)
        return file_name
    except Exception as e :
        await app.send_message(dev,f'Error in get_file_name : {str(e)}')
        return False

        
async def media_handler(chat_id , msgid , message):
    status = await app.send_message(
        chat_id,
        '⏳ Processing file...',
        reply_to_message_id = msgid
    )

    file_name = await get_file_name(message)
    if not file_name :
        await app.edit_message_text(
            chat_id,
            status.id,
            file_name_error
        )
        return
    
    try:
        await app.edit_message_text(chat_id, status.id, dl_text)
        await app.download_media(message,dl_path + file_name)
        if os.path.exists(dl_path+file_name):
            try:
                await app.edit_message_text(chat_id, status.id, upload_text)
                async with aioftp.Client.context(ftp_ip, user=ftp_username, password=ftp_password) as client:
                    await client.upload(dl_path+file_name,ftp_path)
            except Exception as e :
                await app.edit_message_text(chat_id, status.id, upload_error_text)
                await app.send_message(dev,f'Error transferring to FTP host {str(e)}')
                return
            
            await app.send_message(chat_id,dl_url_text.format(ftp_domain,file_name))
            await app.delete_messages(chat_id,status.id)
            #os.remove(dl_path+file_name)
        else:
            await app.edit_message_text(chat_id, status.id, save_error_text)
            await app.send_message(dev,f'Error saving file {str(e)}')
    except Exception as e :
        await app.edit_message_text(chat_id, status.id, dl_error_text)
        await app.send_message(dev,f'Telegram download error {str(e)}')



@app.on_message(filters.private & filters.incoming)
async def message_handler(_, message):
    chat_id = message.chat.id
    msgid = message.id
    if message.text:
        msg = message.text
        if message.text == '/start':
            await app.send_message(
                chat_id,
                start_text,
                reply_to_message_id = msgid
            )
            return
        if chat_id in admins:
            await manager_text_handler(chat_id,msg)
        else:
            await user_text_handler(chat_id,msg)


    elif message.video or message.document or message.audio :
        if chat_id in admins:
            await media_handler(chat_id , msgid , message)
        else:
            await app.send_mesage(
                chat_id,
                'Only administrators can upload.',
                reply_to_message_id = msgid
            )



app.run()
