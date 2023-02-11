from flask import Flask, render_template, url_for, request, redirect
from logic import *
""" переменные """
path_all_video = "/mnt/videos"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = path_all_video


# главная страничка
@app.route('/', methods=['POST', 'GET'])
def index():
    # проверка доступности бд
    sql_check_and_create_bd()
    try:
        all_nukes = get_all_nukes()
    except:
        pass

    if request.method == 'POST':
        response_marks = request.values.lists()
        # проверка не пустой ли список видео
        if len(response_marks) == 2:
            for row in response_marks:
                if row[0] == 'check_box':
                    markers = row[1]
                else:
                    nuke_id = row[1]
        else:
            nuke_id = response_marks[0][1]
            markers = []

        nuke_response_id = nuke_id[0]
        # синхронизация видео в принятом списке с бд на нюке
        for nuke in all_nukes:
            all_video_on_nuke = []
            video_for_delete = []
            # если видео не помечено, но есть в бд
            for video in nuke.videos:
                all_video_on_nuke.append(video[0])
                if str(nuke_response_id) == str(nuke.id):
                    if str(video[0]) not in markers:
                        video_for_delete.append(video[0])
            # удаляем не нужные видео
            for vid in video_for_delete:
                nuke.delete_video(vid)
            # если видео помечено, но нет в бд
            if str(nuke_response_id) == str(nuke.id):
                for video in markers:
                    if int(video) not in all_video_on_nuke:
                        nuke.add_video(int(video))
            # обновление плейлиста
            if str(nuke.id) == str(nuke_response_id):
                nuke.stop_video()
                nuke.play_video()

        return "response_marks"
    else:
        all_video = sql_get_all_videos()
        return render_template("index.html", all_videos=all_video, all_nukes=all_nukes)


# отлов некоторых событий
@app.route('/handler/<id>', methods=['POST'])
def handler(id):
    all_nukes = get_all_nukes()
    for nuke_cache in all_nukes:
        if str(nuke_cache.id) == id:
            nuke = nuke_cache
    response_data = request.form['index']
    # if response_data == f'Ping_{nuke.id}':
    #     if ping_nuke(nuke.ip):
    #         return render_template("about.html", ping=True, id=nuke.id, name=nuke.name)
    #     else:
    #         return render_template("about.html", ping=False, id=nuke.id, name=nuke.name)
    # button play video
    if response_data == f'PlayVideo_{nuke.id}':
        nuke.play_video()
        return "Видео запущено"
    # button pause video
    elif response_data == f'PauseVideo_{nuke.id}':
        nuke.stop_video()
        return "Видео остановлено"
    # button restart video
    # elif response_data == f'Restart_{nuke.id}':
    #     print(f'Restart_{nuke.id}')
    #     return render_template("about.html", pause="pause", id=nuke.id, name=nuke.name)
    # button check playlist
    elif response_data == f'CheckPlaylist_{nuke.id}':
        check_playlist_sql_physic(nuke.ip, nuke.id)
        nuke.stop_video()
        nuke.play_video()
        logging(f'Синхронизация видео {nuke.ip}')
        return "Синхронизация видео"
    else:
        return redirect('/')


# страничка добавления нюка
@app.route('/nukes', methods=['POST', 'GET'])
def all_nuke():
    if request.method == 'POST':
        # удаление нюка из бд
        if request.form['name'].split('_')[0] == 'delete':
            id_nuke = request.form['name'].split('_')[1]
            sql_delete_nuke(id_nuke)
            return redirect('/nukes')
        # редактирование нюка
        elif request.form['name'].split('_____')[0] == 'edit':
            id_nuke = request.form['name'].split('_____')[1]
            new_name = request.form['nuke_name']
            new_ip = request.form['ip']
            new_comment = request.form['comment']
            sql_edit_nuke(id_nuke, new_name, new_ip, new_comment)
            return redirect('/nukes')
        # синхронизация видео
        elif request.form['name'].split('_')[0] == 'sync':
            id_nuke = request.form['name'].split('_')[1]
            ip_nuke = sql_ip_nuke(id_nuke)[0]
            check_playlist_sql_physic(ip_nuke, id_nuke)
            return 'ok'
        # проверка запущен ли сервер на нюке
        elif request.form['name'].split('_')[0] == 'check':
            id_nuke = request.form['name'].split('_')[1]
            ip_nuke = sql_ip_nuke(id_nuke)[0]
            value = send_data(ip_nuke, 'CheckConnections_____')
            if value is True:
                return 'vse ok'
            else:
                return 'ne ok'
        else:
            # добавление нового нюка
            name = request.form['name']
            ip = request.form['ip']
            comment = request.form['comment']
            if comment == '':
                comment = 'Нет описания'
            sql_add_nuke(name, ip, comment)
            return redirect('/nukes')
    else:
        all_nukes = sql_get_all_nukes()
        return render_template('nukes.html', all_nukes=all_nukes)


# страничка добавления видео и синхронизация видео между фтп и скулем
@app.route('/videos', methods=['POST', 'GET'])
def all_videos():
    if request.method == 'POST':
        # добавление видео
        if request.form['send'] == "Отправить":
            name = request.form['name']
            file = request.files['file']
            full_name = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], full_name))
            sql_add_video(name, full_name)
            feedback_status = f"Видео {full_name} успешно загружено!"
            all_video = sql_get_all_videos()
            return render_template('videos.html', all_video=all_video, status_download_video=feedback_status)
        # переменование видео
        elif request.form['send'].split('_____')[0] == 'rename':
            new_name = request.form['name']
            id_video = request.form['send'].split('_____')[1]
            sql_rename_video(id_video, new_name)
            all_video = sql_get_all_videos()
            return render_template('videos.html', all_video=all_video)
        # удаление видео
        elif request.form['send'].split('_____')[0] == 'delete':
            video_name = request.form['send'].split('_____')[1]
            delete_video_from_host(video_name)
            all_video = sql_get_all_videos()
            return render_template('videos.html', all_video=all_video)
        # синхронизация видосов
        else:
            all_video = sql_get_all_videos()
            videos_sql = []
            for row in all_video:
                videos_sql.append(row[2])
            videos_on_ftp = []
            for filename in os.listdir(path=path_all_video):
                videos_on_ftp.append(filename)

            for video in videos_on_ftp:
                if video not in videos_sql:
                    print(video)
                    sql_sync_video(video)

            for video in videos_sql:
                if video not in videos_on_ftp:
                    print(video)
                    sql_delete_video(video)

            return render_template('videos.html', all_video=all_video, status=True)
    else:
        all_video = sql_get_all_videos()
        return render_template('videos.html', all_video=all_video)


@app.route('/faq')
def faq():
    return render_template('faq.html')
