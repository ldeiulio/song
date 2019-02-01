from create_app import app
from flask import request, render_template, jsonify, redirect, Response, flash, send_file
from models import create_all, session, Song, File
from werkzeug.utils import secure_filename
from uploads.utils import upload_path
import os


@app.route('/api/songs', methods=('GET', 'POST', 'PUT', 'DELETE'))
def get_songs_list():
    if request.method == "POST":
        song_json = request.get_json()
        file_id = song_json["file"]["id"]
        file = session.query(File).filter(File.id == file_id).first()
        if file is None:
            flash("error, no file for song")
            return redirect('/')
        song = Song(file_id=file_id)
        session.add(song)
        session.commit()

        jdump = jsonify(song.as_dictionary())
        return jdump, 200
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        song_json = request.get_json()
        song_id = song_json["id"]
        file_id = song_json["file"]["id"]
        if song_id is None:
            flash("cannot delete song, no id supplied")
            return redirect('/')
        song = session.query(Song).filter(Song.id == song_id).first()
        if song is None:
            flash("cannot delete song, no song exists")
            return redirect('/')
        if song.file_id is not file_id:
            flash("song and file don't match")
            return redirect('/')
        file = session.query(File).filter(File.id == song.file_id).first()
        path = file.path
        session.delete(song)
        session.delete(file)
        session.commit()
        if session.query(File).filter(File.path == path).first() is None:
            if os.path.exists(path):
                os.remove(path)
        return redirect('/')
    songs = session.query(Song).all()
    for song in range(len(songs)):
        songs[song] = songs[song].as_dictionary()
    jdump = jsonify(songs)
    return jdump


@app.route('/api/delete', methods=('GET', 'POST'))
def delete_song():
    pass


@app.route('/uploads/<string:file>')
def getSongFile(file):
    path = upload_path(file)
    return send_file(path)


@app.route('/uploads_text/<string:file>')
def file_display(file):
    path = upload_path(file)
    with open(path, 'r') as f:
        content = f.read()
        return Response(content, mimetype='text/plain')


# @decorators.require("multipart/form-data")
# @decorators.accept("application/json")
@app.route("/api/files", methods=["POST"])
def file_post():
    print(request.files)
    if 'file' not in request.files:
        flash('no file part')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        flash('not selected file')
        return redirect('/')
    filename = secure_filename(file.filename)
    file_path = upload_path(filename)
    file.save(file_path)
    file_sql = File(file_name=filename, path=file_path)
    session.add(file_sql)
    session.commit()
    jdump = jsonify(file_sql.as_dictionary())
    return jdump, 201

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    create_all()
    app.run()
