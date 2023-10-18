from pybit.unified_trading import HTTP
import requests
import time
import json
import datetime

"""
    Функция проверки попадания текущего времени в заданных в часах промежуток

    :param start_time: Начало временного периода 
    :type  start_time: int.
    :param   end_time: Начало временного периода
    :type    end_time: int.
    
    :returns: True или False
"""
def time_in_range(start_time, end_time):

    start   = datetime.time(start_time, 0, 0)
    end     = datetime.time(end_time, 0, 0)
    hours   = (int(time.strftime("%H", time.gmtime(time.time()))) + 3) % 24
    minutes = int(time.strftime("%M", time.gmtime(time.time())))
    x       = datetime.time(hours, minutes, 0)
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


"""
    Функция отправки сообщения в телеграм 

    :param     text: Отправляемый текст сообщения
    :type      text: str.
    :param tg_token: Токен телеграм-бота из BotFather
    :type  tg_token: str.
    :param  user_id: ID пользователя бота
    :type   user_id: int.

"""
def send_msg(text, tg_token, user_id):
    url_req = (
        "https://api.telegram.org/bot"
        + tg_token
        + "/sendMessage"
        + "?chat_id="
        + str(user_id)
        + "&text="
        + text
    )
    requests.get(url_req)

"""
    Функция чтения json-файла

    :param     filename: Название файла
    :type      filename: str.
    
    :returns: dict или list
"""
def json_load(filename):
    with open(filename, "r", encoding="utf8") as read_file:
        result = json.load(read_file)
    return result

"""
    Функция записи в json-файл

    :param     filename: Название файла
    :type      filename: str.
    :param     data: Записываемые данные
    :type      data: list or dict.
  
"""
def json_dump(filename, data):
    with open(filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False)






try:
    config         = json_load(r"./json/config.json")
except:
    print('Заполните корректно файл с настройками')

token          = config['tg_token']
user_id        = config['user_id']
api_key        = config['api_key']
api_secret     = config['api_secret']
day_stop_loss  = config['day_stop_loss']
start_time     = config['balance_update_time_start']
end_time       = config['balance_update_time_end']


session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret,
)

# Блок првоерки наличия сведений о последней записи дневного баланса
try:
    day_start_balance = json_load("balance.json")[0]
except:
    day_start_balance = float(
        session.get_wallet_balance(accountType="UNIFIED", coin="USDT",)["result"][
            "list"
        ][0]["totalEquity"]
    )

    json_dump("balance.json", [day_start_balance])


update_flag = True
while True:

    try:
        balance = float(
            session.get_wallet_balance(accountType="UNIFIED", coin="USDT",)["result"][
                "list"
            ][0]["totalEquity"]
        )

        # Обновление дневного баланса в заданный промежуток времени
        if time_in_range(start_time, end_time) and update_flag:
            day_start_balance = balance
            update_flag       = False
            json_dump("balance.json", [day_start_balance])
            send_msg("Дневной баланс обновлен", token, user_id)
            
        if not time_in_range(start_time, end_time):
            update_flag = True


        # если прeвышен дневной стоп-лосс, то уже открытые и вновь открытые позиции закрываютсяс уведомлением в телеграм
        if (100 - balance / day_start_balance * 100) > day_stop_loss:
            
            current_orders = session.get_positions(
                category="linear", settleCoin="USDT"
            )["result"]["list"]

            if len(current_orders) > 0:
                
                send_msg(
                    "Торговля на сегодня заблокирована, достигнут дневной лимит стоп-лосса", token, user_id
                )
                for position in current_orders:
                    coeff = 0
                    price = float(
                        session.get_tickers(
                            category="linear",
                            symbol=position["symbol"],
                        )["result"]["list"][0]["lastPrice"]
                    )

                    side        = position["side"]
                    entry_price = float(position["avgPrice"])

                    session.place_order(
                        category="linear",
                        symbol=position["symbol"],
                        side="Buy" if side == "Sell" else "Sell",
                        orderType="Market",
                        qty=position["size"],
                    )

    except Exception as e:
        send_msg("Ошибка в дневном риск-менеджере: {}".format(str(e)), token, user_id)
