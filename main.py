# from app import create_app
# from flask_socketio import SocketIO

# app = create_app()
# socketio = SocketIO(app)

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


from app import create_app, socketio
import app.chat_socketio  # 👈 This registers events

app = create_app()

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)
