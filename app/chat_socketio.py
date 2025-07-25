# app/chat_socketio.py

from flask_socketio import emit, join_room
from . import socketio

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'username': 'System', 'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=data['room'])
