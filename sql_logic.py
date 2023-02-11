import sqlite3
from datetime import datetime


# проверяем есть ли бд, таблицы и тп
def sql_check_and_create_bd():
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        # таблица для видео
        cursor.execute("""CREATE TABLE IF NOT EXISTS video(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    full_name TEXT,
                    date_create TEXT);
                    """)
        # таблица для нюков
        cursor.execute("""CREATE TABLE IF NOT EXISTS nuke(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    ip TEXT NOT NULL UNIQUE,
                    comment TEXT,
                    ping TEXT,
                    date_create TEXT);
                    """)
        # таблица для ассоциации видео на нюках
        cursor.execute("""CREATE TABLE IF NOT EXISTS linking(
                    id INTEGER PRIMARY KEY,
                    id_nuke  INTEGER REFERENCES nuke (id) ON DELETE CASCADE,
                    id_video INTEGER REFERENCES video (id) ON DELETE CASCADE,
                    date_create TEXT);
                    """)
        conn.commit()
        cursor.close()
        return True
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
        #f = open(log_path,'w')
        #f.write(str(error_text))
        return False


# добавить новый нюк в бд
def sql_add_nuke(nuke_name, nuke_ip, comment):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO nuke(name, ip, comment, date_create) VALUES("{nuke_name}", "{nuke_ip}", '
                       f'"{comment}", "{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# добавляем новое видео в бд
def sql_add_video(name, full_name):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO video(name, full_name, date_create) VALUES("{name}", "{full_name}", '
                       f'"{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
    except sqlite3.Error as error:
        print(error)
    cursor.close()


# создание ассоциации видео и нюка
def sql_create_link_video_and_nuke(id_nuke, id_video):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO linking(id_nuke, id_video, date_create) VALUES("{id_nuke}", "{id_video}", '
                       f'"{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получение имени нюка по айди
def sql_get_name_nuke(id):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        name = cursor.execute(f'SELECT name FROM nuke where id="{id}"').fetchall()[0]
        return name[0]
    except sqlite3.Error as error:
        print(error)
    cursor.close()


# удаление ассоциации нюка и видео
def sql_delete_link_video_and_nuke(id_nuke, id_video):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM linking WHERE id_nuke="{id_nuke}" AND id_video="{id_video}"')
        conn.commit()
        # ip_nuke = cursor.execute(f'SELECT ip FROM nuke where id="{id_nuke}"').fetchall()[0]
        # print(ip_nuke)
        # video_name = cursor.execute(f'SELECT name FROM video where id="{id_video}"').fetchall()[0]
        # print(video_name)
        # full_name = cursor.execute(f'SELECT full_name FROM video where id="{id_video}"').fetchall()[0]
        # print(full_name)
        # return ip_nuke[0], video_name[0], full_name[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# удаление ассоциации нюка и видео
def sql_get_ip_nuke_and_video(id_nuke, full_name):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        id_video = cursor.execute(f'SELECT id FROM video WHERE full_name="{full_name}"').fetchall()[0]

        ip_nuke = cursor.execute(f'SELECT ip FROM nuke where id="{id_nuke}"').fetchall()[0]
        video_name = cursor.execute(f'SELECT name FROM video where id="{id_video}"').fetchall()[0]
        full_name = cursor.execute(f'SELECT full_name FROM video where id="{id_video}"').fetchall()[0]
        return ip_nuke[0], video_name[0], full_name[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получение всех видео в ассоциациях с нюком (стр about, edit)
def sql_get_all_video_name_on_nuke(id_nuke):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_videos_on_nuke = cursor.execute(f"""SELECT video.full_name FROM linking, nuke, video
        where linking.id_nuke=nuke.id and linking.id_video=video.id and linking.id_nuke='{id_nuke}'""").fetchall()
        video_on_nuke = []
        for video in all_videos_on_nuke:
            # print(video)
            video_on_nuke.append(video[0])
        # print(video_on_nuke)
        return video_on_nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получение всех нюков
def sql_get_all_nukes():
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        nukes = cursor.execute(f'SELECT id, name, ip, comment, ping from nuke').fetchall()
        nuke = {}
        for item in nukes:
            id_nuke = item[0]
            name = item[1]
            ip = item[2]
            comment = item[3]
            ping = item[4]
            nuke[name] = {'ip_nuke': ip, 'name': name, 'id_nuke': id_nuke, 'comment': comment, 'ping': ping}
        return nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получение всех видео
def sql_get_all_videos():
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        videos = cursor.execute(f'SELECT id, name, full_name from video').fetchall()
        return videos
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)


# получение всех id видео из ассоциаций для нюка (стр. edit)
def sql_all_video_on_nuke(id_nuke):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_videos_on_nuke = cursor.execute(f"""SELECT video.id FROM linking, nuke, video
        where linking.id_nuke=nuke.id and linking.id_video=video.id and linking.id_nuke='{id_nuke}'""").fetchall()
        video_on_nuke = []
        for video in all_videos_on_nuke:
            video_on_nuke.append(str(video[0]))
        return video_on_nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получение ip нюка
def sql_ip_nuke(id):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        ip_nuke = cursor.execute(f'SELECT ip FROM nuke WHERE id="{id}"').fetchall()
        return ip_nuke[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# # получение айди видео по имени
def sql_id_from_name_video(full_name):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    id_video = cursor.execute(f'SELECT id FROM video WHERE full_name="{full_name}"').fetchall()[0]
    return id_video[0]


# запрос для кнопки синхронизации видео
def sql_sync_video(name_video):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO video(name, full_name) VALUES("{name_video}", "{name_video}")')
    conn.commit()
    cursor.close()


# список всех видео для нюка. в формате id_video, video_name, full_name
def sql_get_all_video_on_nuke(id_nuke):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    all_videos = cursor.execute(f"""SELECT video.id, video.name, video.full_name FROM linking, video
    WHERE video.id = linking.id_video AND linking.id_nuke={id_nuke}""").fetchall()
    return all_videos


# получаение всей информации о видео по айди
def sql_get_info_video_from_id(video_id):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    info_video = cursor.execute(f"""SELECT id, name, full_name FROM video WHERE id={video_id}""").fetchall()
    return info_video[0]


# удалить нюк по айди
def sql_delete_nuke(id):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM nuke WHERE id="{id}"')
    conn.commit()
    cursor.close()


# удалить видео по имени видео
def sql_delete_video(video_name):
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM video WHERE full_name="{video_name}"')
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print(error)


def sql_get_name_fullname_video(id_video):
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        video_name = cursor.execute(f'SELECT name FROM video where id="{id_video}"').fetchall()[0][0]
        full_name = cursor.execute(f'SELECT full_name FROM video where id="{id_video}"').fetchall()[0][0]
        return video_name, full_name
    except sqlite3.Error as error:
        print(error)


# переименование видео
def sql_rename_video(id_video, new_name):
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE video SET name="{new_name}" WHERE id="{id_video}"')
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print(error)


# редактирование нюка
def sql_edit_nuke(id_nuke, new_name, new_ip, new_comment):
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE nuke SET name="{new_name}", ip="{new_ip}", comment="{new_comment}" WHERE id="{id_nuke}"')
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print(error)


# изменение статуса нюка по пингу
def sql_exchange_ping(id_nuke, ping_status):
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    # print(f'INSERT INTO nuke(ping) VALUES("{ping_status}") WHERE id="{id_nuke}"')
    try:
        cursor.execute(f'UPDATE nuke SET ping="{ping_status}" WHERE id="{id_nuke}"')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        print(error_text)
    cursor.close()


# получить статус нюка
def sql_get_ping_status(id_nuke):
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        status_ping = cursor.execute(f'SELECT ping FROM nuke WHERE id="{id_nuke}"').fetchall()[0]
        return status_ping
    except sqlite3.Error as error:
        print(error)
