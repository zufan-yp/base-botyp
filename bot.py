import tweepy
import config
from datetime import datetime
import pytz
import sys
from time import sleep
import requests
from requests_oauthlib import OAuth1

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

auth_download = OAuth1(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)
temp_img = "./tmp/img-tmp.jpg"


def debug_cuy(text):
    print(pytz.timezone("Asia/Jakarta").localize(datetime.now()).strftime("%H:%M:%S") + ' => ' + str(text))


def delete_message(message_id):
    debug_cuy("👋 menghapus pesan dengan id " + str(message_id))
    api.destroy_direct_message(message_id)


def make_tweet(text):
    try:
        debug_cuy("🚀 membuat tweet baru")
        api.update_status(text)
    except tweepy.TweepError as e:
        debug_cuy('😡 ' + e.response.text)
        pass
    except Exception as e:
        print(e)
        pass


def make_tweet_with_image(file, text):
    try:
        debug_cuy("🚀 membuat tweet baru dengan gambar")
        api.update_with_media(filename=file, status=text)
    except tweepy.TweepError as e:
        debug_cuy('😡 ' + e.response.text)
        pass
    except Exception as e:
        print(e)
        pass


def download_photo(url):
    try:
        response = requests.get(url, auth=auth_download)
        with open(temp_img, "wb") as img:
            img.write(response.content)
        debug_cuy("👌 gambar berhasil di unduh")
    except Exception as e:
        print(e)
        pass


while True:
    # * mencoba mengambil pesan
    try:
        list = api.list_direct_messages()
        list.reverse()  # * mengurutkan dari yang terlama
        # * cek isi list tidak 0
        if len(list) is not 0:
            for x in range(len(list)):
                message_id = list[x].id
                message_data = list[x].message_create['message_data']
                text = message_data['text']
                debug_cuy('💌 ada pesan "'+text+'"')
                # * cek ada kata kunci
                if config.keywords in text and len(text) <= 280:
                    debug_cuy('👍 pesan berisi kata kunci')
                    # * bersihkan kata kunci dari text
                    # debug_cuy('👋 menghapus kata kunci dari text')
                    text = text.replace(config.keywords, '')
                    # * proses jika text tidak kosong setelah di bersihkan
                    if text is not '':
                        # * mencoba cek ada attachment tidak
                        try:
                            attachment_media = message_data['attachment']['media']
                            media_type = attachment_media['type']
                            media_url = attachment_media['media_url']
                            url = attachment_media['url']
                            if media_type == 'photo':
                                debug_cuy('🏙  pesan berisi gambar')
                                download_photo(media_url)
                                # * hapus url pada text
                                text = text.replace(url, '')
                                # * bikin tweet dengan gambar
                                make_tweet_with_image(temp_img, text)
                                delete_message(message_id)
                            else:
                                debug_cuy('😓 tidak boleh video')
                                delete_message(message_id)
                        # * handle jika cuma text
                        except:
                            # * bikin tweet
                            make_tweet(text)
                            delete_message(message_id)
                    else:
                        debug_cuy('👎 text setelah kata kunci kosong')
                        delete_message(message_id)
                else:
                    debug_cuy('👎 pesan tidak sesuai kata kunci')
                    delete_message(message_id)
        # * handle jika isi list kosong
        else:
            debug_cuy('⏳ isi pesan kosong, menunggu pesan baru, cek setiap 1 menit, sisa limit ' + str(api.rate_limit_status()['resources']['direct_messages']['/direct_messages/events/list']['remaining']))
        sleep(60)
    # ! handle jika ada error
    except tweepy.RateLimitError as e:
        debug_cuy('😡 ' + e.response.text)
        sleep(60)
        pass
    except tweepy.TweepError as e:
        debug_cuy('😡 ' + e.response.text)
        pass
    except Exception as e:
        print(e)
        pass
