import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect   # ← 新增

# -------------------------------------------------
# 1️⃣ 建立 Flask app
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# 2️⃣ 必要設定
# -------------------------------------------------
# 2‑1️⃣ 讀取自 `config.Config`（如果那裡已有 SECRET_KEY 也可以保留）
app.config.from_object('config.Config')

# 2‑2️⃣ 若 `config.Config` 沒設定 SECRET_KEY，這裡補上
# ＊請自行替換成長度 ≥ 32、隨機且保密的字串＊
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = '4f9c2d1a9b7e6a3d5c8f0e1b2a7d9c6e'  # <‑‑ 範例，請改成自己的

# 2‑3️⃣ 啟用 CSRF（開發階段關閉逾時限制，避免頁面停留較久或時鐘跳動導致過期）
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # None 代表永不過期（與 session 生命週期一致）

# -------------------------------------------------
# 3️⃣ 初始化擴充套件
# -------------------------------------------------
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------------------------------------
# 4️⃣ 啟用全域 CSRF 防護
# -------------------------------------------------
csrf = CSRFProtect(app)   # 必須在 `app` 建立之後呼叫

# -------------------------------------------------
# 5️⃣ 匯入 models、routes（在 extensions 初始化之後，避免循環匯入）
# -------------------------------------------------
from models import User, Manuscript   # noqa: F401
from routes import *                  # noqa: F401,F403

# -------------------------------------------------
# 6️⃣ 執行入口
# -------------------------------------------------
if __name__ == '__main__':
    # 若使用 SQLite，確保資料庫檔案存在
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()

    # 開發模式下啟動（debug=True 會自動顯示 reloader + debugger）
    app.run(debug=True)
