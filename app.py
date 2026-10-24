from flask import Flask
from config import Config
from routes.translate import translate_bp
from routes.practice import practice_bp
from routes.situations import situations_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(translate_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(situations_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
