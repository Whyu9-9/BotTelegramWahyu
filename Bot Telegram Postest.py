import json
import requests
import time
import urllib
import mysql.connector

#konektor database
db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Dragoncit1234",
            db="db_postest",
            auth_plugin="mysql_native_password")

#token dari bot setelah daftar di @botfather
TOKEN = "token disini"
#url dari bot
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


#fungsi untuk mendapatkan url lalu ditaruh di variabel content
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

#fungsi untuk mendapatkan file json dari url lalu ditaruh di variabel js
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


#fungsi untuk mendapatkan chat id dan text terbaru lalu ditaruh di variabel text dan chat_id
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


#fungsi untuk mendapatkan update json
def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

#fungsi untuk mendapatkan id update terbaru
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#fungsi untuk mengirim pesan, data pesan akan di parse ke url
def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def sendImage(path, chat_id):
    url = "https://api.telegram.org/bot"+ TOKEN +"/sendPhoto";
    files = {'photo': open(path, 'rb')}
    data = {'chat_id' : chat_id}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

#fungsi untuk mengambil data dari database lalu dikirim ke fungsi send_message
#untuk selanjutnya nnti bakal dikirim ke user
def carifoto(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            cursor = db.cursor()
            sql = "SELECT lokasi_gambar FROM tb_response WHERE label='%s'" %(text)
            cursor.execute(sql, text)
            result = cursor.fetchall()
            if (len(result) > 0):
                for row in result:
                    lokasi_gambar = row[0]
                    print("Gambar " + text + " Berhasil Dikirim")
                    sendImage(lokasi_gambar, chat)
            else:
                send_message("Maaf Label " + text +" Tidak Tersedia", chat)
        except Exception as e:
            print(e)

#fungsi main yang digunakan untuk looping tidak terbatas dengan wile true
#fungsi main disini memanggil fungsi ngerjain_sendiri dan looping koneksi ke database

def main():
    last_update_id = None
    while True:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Dragoncit1234",
            db="db_postest",
            auth_plugin="mysql_native_password")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            carifoto(updates)
        db.close()
        time.sleep(0.5)

#fungsi yang memanggil fungsi main
if __name__ == '__main__':
    main()
