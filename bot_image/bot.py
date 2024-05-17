import logging
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import paramiko
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv('TOKEN')
emails=[]
phonenumbers=[]

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}! Для того, чтобы узнать команды, введи /help')

def helpCommand(update: Update, context):
    update.message.reply_text('find_phone_number - Поиск номера телефона\nfind_email - Поиск электронной почты\nverify_password - Проверка сложности пароля\nget_release -  Релиз\nget_uname -  Архитектура процессора, имя хоста системы и версия ядра.\nget_uptime -  Время работы\nget_df -  Состояние файловой системы\nget_free - Состояние оперативной памяти\nget_mpstat - Производительность системы\nget_w - Работающие пользователи\nget_auths - Последние 10 входов\nget_critical - Последние 5 крит. события\nget_ps - Процессы\nget_ss - Порты\nget_apt_list - Пакеты\nget_services - Сервисы\nget_emails - EMails\nget_phonenumbers- Phonenumbers\nget_repl_logs -Logs')

def db_connection(command):
        db_user=os.getenv('DB_USER')
        db_password=os.getenv('DB_PASSWORD')
        db_host=os.getenv('DB_HOST')
        db_port=os.getenv('DB_PORT')
        db_database=os.getenv('DB_DATABASE')
        connection = None
        try:
            connection = psycopg2.connect(user=db_user,
                                        password=db_password,
                                        host=db_host,
                                        port=db_port, 
                                        database=db_database)

            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            data = cursor.fetchall()
            logging.info("Команда успешно выполнена")
            return data 
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()

def connection(command):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def findReg(reg,input):
    Regex = re.compile(reg) 
    RegexList = Regex.findall(input) # Ищем совпадения с регулярным выражением
    if not RegexList: # Обрабатываем случай, когда нет вхождений
        return None# Завершаем выполнение функции
    return RegexList

def list_to_str(list):
    if not list: # Обрабатываем случай, когда нет вхождений
        return None# Завершаем выполнение функции
    regList = '' # Создаем строку, в которую будем записывать данные
    for i in range(len(list)):
        regList += f'{i+1}. {list[i]}\n' # Записываем данные по порядку
    return regList

def get_phonenumbers(update: Update, context):
    update.message.reply_text(list_to_str(db_connection('SELECT phonenumber from phonenumbers;')))
    return ConversationHandler.END

def insert_phonenumber(update: Update, context):
    user_input = update.message.text
    if user_input=='Да':
        ins=db_connection('INSERT INTO phonenumbers (phonenumber) VALUES (\''+ '\'), (\''.join(phonenumbers) +'\') RETURNING phonenumber_id;')
        if ins is None:
                print('(\''+ '), (\''.join(phonenumbers) +'\')')
                update.message.reply_text("Неудачное добавление")
                return ConversationHandler.END
        else:
                update.message.reply_text("Номер телефона успешно добавлен")
                return ConversationHandler.END
    else:
        update.message.reply_text("Всего хорошего")
        return ConversationHandler.END

def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def find_phone_number (update: Update, context):
    global phonenumbers
    phonenumbers.clear()
    user_input = update.message.text# Получаем текст, содержащий(или нет) номера телефонов
    if findReg(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',user_input) is None:
        update.message.reply_text('Не найдено номеров телефона')
        return ConversationHandler.END
    else:
        phonenumbers=(findReg(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',user_input))
        update.message.reply_text(list_to_str(phonenumbers)) # Отправляем сообщение пользователю
        update.message.reply_text('Записать данные в базу данных?')
    return 'insert_phonenumber' # Отправляем сообщение пользователю

def get_emails(update: Update, context):
    update.message.reply_text(list_to_str(db_connection('SELECT email from emails;')))
    return ConversationHandler.END

def insert_email(update: Update, context):
    user_input = update.message.text
    if user_input=='Да':
        ins=db_connection('INSERT INTO emails (email) VALUES (\''+ '\'), (\''.join(emails) +'\') RETURNING email_id;')
        if ins is None:
                print('(\''+ '), (\''.join(emails) +'\')')
                update.message.reply_text("Неудачное добавление")
                return ConversationHandler.END
        else:
                update.message.reply_text("Электронная почта успешно добавлена")
                return ConversationHandler.END
    else:
        update.message.reply_text("Всего хорошего")
        return ConversationHandler.END
    
def find_email_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронной почты: ')
    return 'find_email'

def find_email (update: Update, context):
    global emails
    emails.clear()
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    if findReg(r'(?:[A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(?:\.[A-Z|a-z]{2,})+',user_input) is None:
        update.message.reply_text('Не найдено электронной почты')
        return ConversationHandler.END
    else:
        emails=findReg(r'(?:[A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(?:\.[A-Z|a-z]{2,})+',user_input)
        update.message.reply_text(list_to_str(emails))
        update.message.reply_text('Записать данные в базу данных?')
    return 'insert_email' # Отправляем сообщение пользователю

def verify_password_Command(update: Update, context):
    update.message.reply_text('Введите пароль: ')
    return 'verify_password'

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    pattern1 = re.compile(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z!@#$%^&*()]{8,}$') 
    if re.match(pattern1, user_input) is None: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Простой пароль')
        return # Завершаем выполнение функции
    else:
        update.message.reply_text('Сложный пароль') # Отправляем сообщение пользователю
        return ConversationHandler.END # Завершаем работу обработчика диалога

def get_release (update: Update, context):
    update.message.reply_text(connection('uname -r'))
    return ConversationHandler.END

def get_uname (update: Update, context):
    print('a')
    update.message.reply_text(connection('uname -a'))
    print(connection('uname -a'))
    return ConversationHandler.END

def get_uptime (update: Update, context):
    update.message.reply_text(connection('uptime'))
    return ConversationHandler.END

def get_df (update: Update, context):
    update.message.reply_text(connection('df'))
    return ConversationHandler.END

def get_free (update: Update, context):
    update.message.reply_text(connection('free -h'))
    return ConversationHandler.END

def get_mpstat (update: Update, context):
    update.message.reply_text(connection('mpstat'))
    return ConversationHandler.END

def get_w (update: Update, context):
    update.message.reply_text(connection('who -a'))
    return ConversationHandler.END

def get_auths (update: Update, context):
    update.message.reply_text(connection('last -10'))
    return ConversationHandler.END

def get_critical (update: Update, context):
    update.message.reply_text(connection('journalctl -p crit -n 5'))
    return ConversationHandler.END

def get_ps (update: Update, context):
    update.message.reply_text(connection('ps '))
    return ConversationHandler.END

def get_ss (update: Update, context):
    update.message.reply_text(connection('ss -tulpn'))
    return ConversationHandler.END

def apt_list_Command(update: Update, context):
    update.message.reply_text('Введите пакет, который желаете найти, либо введите all для вывода всех пакетов: ')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input=='all':
        if len(connection('apt list --installed'))>4096:
            for x in range(0, len(connection('apt list --installed')),4096):
                update.message.reply_text(connection('apt list --installed')[x:x+4096])  
            else:  
                update.message.reply_text(connection('apt list --installed'))
    else:
        update.message.reply_text(connection('apt list '+user_input))
    return ConversationHandler.END

def get_services (update: Update, context):
    update.message.reply_text(connection('service --status-all | grep \'\[ + \]\''))
    return ConversationHandler.END


def get_repl_logs(update: Update, context):
    reply=''
    filename=os.listdir('//temp/db_logs/')[0]
    log=open('/temp/db_logs/'+filename,'r').readlines()
    for i in log:
    	if 'repl' in i.lower():
    	   reply += i + '\n'
    update.message.reply_text(reply)
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'insert_phonenumber':[MessageHandler(Filters.text & ~Filters.command, insert_phonenumber)]
        },
        fallbacks=[]
    )
    convHandlerFind_emails= ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_Command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'insert_email':[MessageHandler(Filters.text & ~Filters.command, insert_email)]
        },
        fallbacks=[]
    )
    convHandlerVerify_Password= ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_Command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerAptList= ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', apt_list_Command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFind_emails)
    dp.add_handler(convHandlerVerify_Password)
    dp.add_handler(convHandlerAptList)
    dp.add_handler(CommandHandler("get_release",get_release))
    dp.add_handler(CommandHandler("get_uname",get_uname))
    dp.add_handler(CommandHandler("get_uptime",get_uptime))
    dp.add_handler(CommandHandler("get_df",get_df))
    dp.add_handler(CommandHandler("get_free",get_free))
    dp.add_handler(CommandHandler("get_mpstat",get_mpstat))
    dp.add_handler(CommandHandler("get_w",get_w))
    dp.add_handler(CommandHandler("get_auths",get_auths))
    dp.add_handler(CommandHandler("get_critical",get_critical))
    dp.add_handler(CommandHandler("get_ps",get_ps))
    dp.add_handler(CommandHandler("get_ss",get_ss))
    dp.add_handler(CommandHandler("get_services",get_services))
    dp.add_handler(CommandHandler("get_repl_logs",get_repl_logs))
    dp.add_handler(CommandHandler("get_emails",get_emails))
    dp.add_handler(CommandHandler("get_phonenumbers",get_phonenumbers))

	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
