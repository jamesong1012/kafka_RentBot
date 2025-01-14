from confluent_kafka import Consumer, KafkaError
from telegram.ext import Updater, CommandHandler
from telegram import Bot
from ksql import KSQLAPI

setting = {
        'bootstrap.servers':'localhost:29092',
        'group.id':'admin.py',
        'default.topic.config': {'auto.offset.reset': 'largest'}
}
c = Consumer(setting)
c.subscribe(['house_info'])

client = KSQLAPI('http://localhost:8088')

token = '5407630481:AAG97GSHB2l0n_0y1aCnrEkRtx32P9ML0Io'
bot = Bot(token)

updater = Updater(token=token)

dispatcher = updater.dispatcher

# 定義收到訊息後的動作(新增handler)
def start(update, context): # 新增指令/start
    message = update.message
    chat = message['chat']
    update.message.reply_text(text='HI  ' + str(chat['id']))
    print(message.text)

def delete(update, context):
    house_id = update.message.text[8:]
    if(house_id == ''):
        update.message.reply_text(text='請輸入房屋ID!')
    else:
        query_statment = 'insert into house_stream_deleted (houseid, dummy) VALUES (' +'\'' + house_id + '\'' +', cast(null as varchar))'
        client.ksql(query_statment)
        update.message.reply_text(text='房屋ID: '+ house_id + '已刪除')
        

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('delete', delete))
updater.start_polling()
updater.idle()

while True:
    msg = c.poll(0.1)
    if msg is None:
        continue
    else:
        key = msg.key().decode('utf-8')
        data = msg.value().decode('utf-8')
        print('ID      :' + key)
        temp = data.replace('{', '')
        temp = temp.replace('}', '')
        temp = temp.replace('[', '')
        temp = temp.replace(']', '')
        temp = temp.replace(',', '\n')
        temp = temp.replace('\"', '')
        temp = temp.replace('TITLE:',       '案名    :')
        temp = temp.replace('LOCATION:',    '地址    :')
        temp = temp.replace('ROOMTYPE:',    '房型    :')
        temp = temp.replace('PING:',        '坪數    :')
        temp = temp.replace('FLOOR:',       '樓層    :')
        temp = temp.replace('PRICE:',       '價格    :')
        temp = temp.replace('ROOMPATTERN:', '格局    :')
        temp = temp.replace('TAGS:',        '標籤    :')
        temp = temp.replace('GENDER:',      '性別    :')
        if(temp[-1] == '0'):
            temp = temp[:-1] + '無限制'
        elif(temp[-1] == '1'):
            temp = temp[:-1] + '限男'
        else:
            temp = temp[:-1] + '限女'
        print(temp)
        bot.send_message(1236400727,'ID        :' + key + '\n' + temp)
