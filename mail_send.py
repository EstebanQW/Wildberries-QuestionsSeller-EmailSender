import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

# ==========================================================#
API_KEY = ""  # апи ключ вб для обработки вопросов
FROM_ADDR = "example1@mail.ru"  # почта, с которой будет уходить письмо
MAIL_PASSWORD = "password"  # пароль от почты для внешних приложений
TO_ADDR = "example2@mail.ru"  # почта, на которую отправлять письмо
QUESTIONS_SUM = (
    10  # количество кейсов, которые необходимо отправить (1 кейс = 1 вопрос)
)
# ==========================================================#


def get_answers(value):
    url = "https://feedbacks-api.wildberries.ru/api/v1/questions"
    headers = {
        "Authorization": API_KEY,
    }
    params = {
        "isAnswered": False,
        "take": value,
        "skip": 0,
    }
    print("Отправляю запрос на сервер для получения вопросов WB")

    max_retries = 2  # количество попыток отправки запроса
    retry_delay = 2  # задержка между попытками в секундах

    for _ in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Получил статус-код: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                return data["data"]["questions"]
            elif response.status_code == 429:
                print(
                    f"Ошибка запроса: {response.status_code}. Слишком много запросов за последнее время."
                )
                return None
            else:
                print(f"Ошибка запроса: {response.status_code}. Повторяю запрос...")
                time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}. Повторяю запрос...")
            time.sleep(retry_delay)

    print("Все попытки отправки запроса не увенчались успехом. Ошибка.")
    return None


def send_mail(value):
    cases = get_answers(value)
    for case in cases:
        tema = case["id"]
        body = f"""<p><b>Текст вопроса:</b> {case['text']}</p>
<br>
<p><b>Ссылка на товар WB:</b> <a href="firefox:https://www.wildberries.ru/catalog/{case['productDetails']['nmId']}/detail.aspx">https://www.wildberries.ru/catalog/{case['productDetails']['nmId']}/detail.aspx</a></p>
<br>
<p>Название бренда: {case['productDetails']['brandName']}</p>
<p>ID вопроса: {case['id']}</p>
<p>Дата поступления вопроса: {case['createdDate']}</p>
<p>Артикул на WB: {case['productDetails']['nmId']}</p>
<p>Название товара: {case['productDetails']['productName']}</p>
<p>Артикул продавца: {case['productDetails']['supplierArticle']}</p>
<br>
"""
        print(f"Начинаю отправку сообщения(кейса) на email {TO_ADDR}.")

        msg = MIMEMultipart()
        msg["From"] = FROM_ADDR
        msg["To"] = TO_ADDR
        msg["Subject"] = tema
        msg.attach(MIMEText(body, "html"))

        max_retries = 2  # количество попыток отправки email
        retry_delay = 2  # задержка между попытками в секундах

        for _ in range(max_retries):
            try:
                server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
                server.login(FROM_ADDR, MAIL_PASSWORD)
                text = msg.as_string()
                server.sendmail(FROM_ADDR, TO_ADDR, text)
                server.quit()
                current_index = cases.index(case)
                print(
                    f"Сообщение отправлено. Осталось отправить сообщений(кейсов): {len(cases[current_index:])-1}шт."
                )
                break
            except smtplib.SMTPException as e:
                print(f"Ошибка при отправке письма: {e}. Повторяю отправку...")
                time.sleep(retry_delay)
        else:
            print("Все попытки отправки письма не увенчались успехом. Ошибка.")
        time.sleep(1)
    print("Все сообщения(кейсы) отправлены.")


if __name__ == "__main__":
    send_mail(QUESTIONS_SUM)
