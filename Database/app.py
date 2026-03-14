'''
io: 將 QR code 圖片存在記憶體緩衝區(BytesIO)，直接傳給瀏覽器，不放在硬碟內
os: 操作檔案路徑、建立資料夾、刪除檔案
uuid: 用於產生唯一的亂碼 ID 給票卷以及上傳圖片的檔名，避免重複
qrcode: 用於生成 QR code 圖片
pyodbc: 用於連接 Python 與 資料庫，執行 SQL 指令
datetime, timedelta: 用於判斷展覽是否過期或者場次是否開始，以及登入閒置自動登出
flask:
    Flask: 建立網頁應用程式物件 (app)
    render_template: 將資料填入 HTML 檔案並回傳給瀏覽器
    request: 接收使用者傳來的資料 (表單 form, 網址參數 args, 檔案 files)
    redirect, url_for: 讓瀏覽器跳轉到別的網址
    session: 用來記住使用者狀態，例如: 購物車內容
    flash: 在跳頁時顯示一次性的提示訊息，例如: 登入成功
    send_file: 用來傳送圖片檔案給瀏覽器
werkzeug.security:
    generate_password_hash: 用於將密碼經過雜湊，再存入資料庫
    check_password_hash: 檢查輸入的密碼與資料庫的雜湊是否相符
werkzeug.utils:
    secure_filename: 將上傳的圖片檔名過濾成安全格式
'''

import io
import os
import uuid
import qrcode
import pyodbc
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__) # 讓 flask 知道當前檔案(app.py)位置
app.secret_key = os.urandom(24)  # 設定隨機亂數，會附加在傳給瀏覽器的 Cookie 後面，用於登入、購物車要記住不同的使用者狀態
app.permanent_session_lifetime = timedelta(minutes=30)  # 設定閒置 30 分鐘自動登出

# 圖片上傳設定
# 設定上傳的圖片要被存到哪個資料夾
#               把路徑拼起來 | 只取資料夾的路徑 | 找出某檔案的絕對路徑 | __file__ 代表目前的檔案(app.py) | 要經過的各個資料夾
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'exhibitions')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'} # 設定允許的圖片格式

# 確保上傳圖片的資料夾存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app.config 是用來存放整個網站的設定值的字典
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # 紀錄上傳資料夾的路徑
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上傳檔案大小為 16MB


def allowed_file(filename):
    """檢查檔案副檔名是否允許"""
    # 檢查檔名是否有副檔名的小數點 | 從右邊r 以 . 切割1刀 | [1] 取得切割後的列表的第二個元素(也就是副檔名) | .lower() 轉換成小寫 | in ALLOWED_EXTENSIONS 檢查拿到的副檔名有沒有在前面設定的允許清單內
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_exhibition_image(file, exhibition_id=None):
    """
    儲存展覽圖片
    回傳相對路徑 (用於存入資料庫)
    """
    if file and allowed_file(file.filename):
        # 產生唯一檔名避免覆蓋
        ext = file.filename.rsplit('.', 1)[1].lower() # 分割副檔名存在 ext
        if exhibition_id: # 如果有展覽id，就將展覽id融入圖片名稱
            filename = f"exhibition_{exhibition_id}_{uuid.uuid4().hex[:8]}.{ext}" # [:8] 只取 uuid 產生的32個字元中的前8個字
        else:
            filename = f"exhibition_{uuid.uuid4().hex}.{ext}"
        
        filename = secure_filename(filename)
        # 以前面儲存的上傳圖片的資料夾檔案路徑，結合檔名，儲存圖片
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 回傳相對路徑 (給前端用)
        return f"/static/uploads/exhibitions/{filename}"
    return None


def delete_old_image(image_path):
    """刪除舊圖片檔案"""
    # 檢查圖片是否為我們自己上傳的圖片，圖片是否存在 且 是否在我們設定的路徑之下
    if image_path and image_path.startswith('/static/uploads/exhibitions/'):
        # 圖片檔案路徑中，'刪除'路徑，只保存檔名
        filename = image_path.replace('/static/uploads/exhibitions/', '')
        # 結合檔名與設定的路徑，讓os知道圖片所在的絕對路徑
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath): # 如果存在就刪掉，否則報錯
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"刪除舊圖片失敗: {e}")


def get_db_connection():
    try:
        # 嘗試連接資料庫
        return pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};' # 以 ODBC 為驅動程式
            r'SERVER=localhost;' # SQL Server 是在本地端(localhost)
            r'DATABASE=ExhibitionTicketSystem;' # 在 SQL Server 內，要使用的資料庫名稱
            r'UID=XXXX;' # 程式進入資料庫的身分與密碼，需要提前在 SQL Server 那邊設定
            r'PWD=XXXX;'
        )
        print("資料庫連線成功！")
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        return None

def to_dict(cursor, row):
    """將 SQL Server 傳回的資料從 Tuple 轉為 字典"""
    # dict轉為字典 | zip 將欄位名稱與資料連起來 | cursor.description 儲存了SQL查詢的欄位資訊 | 資料的型態 Row(Tuple) 給zip串資料與欄位
    return dict(zip([column[0] for column in cursor.description], row))

# 輔助函式：檢查是否為管理員
def is_admin():
    return session.get('role') == 'admin'


# Context Processor: 讓所有 Template 都能讀到購物車數量
@app.context_processor
def inject_cart_count():
    cart = session.get('cart', [])
    return dict(cart_count=len(cart))


# ==========================================
# 前台路由 (Front-end)
# ==========================================

# --- 首頁：展覽列表 (含搜尋 & 時間檢查) ---
@app.route('/')
def index():
    # 取得搜尋關鍵字，'q'抓取網址問號後面的參數q的值，''如果只是剛進首頁就會是空字串
    keyword = request.args.get('q', '')

    conn = get_db_connection()
    if not conn: return "DB Connection Error", 500 # 如果連接不到 SQL Server 就回傳 500 狀態碼並顯示錯誤
    try:
        with conn.cursor() as cursor: # 用於向資料庫申請一個"游標 (Cursor)"，用來執行 SQL 指令並取得結果
            if keyword: # 如果要查詢東西，也就是keyword存在的話
                # 搜尋標題或地點
                # 只抓取以上架或以結束的展覽(為了過濾草稿)，搜尋標題或地點符合關鍵字的
                sql = """
                    SELECT * FROM Exhibitions
                    WHERE status IN ('Published', 'Ended') AND (title LIKE ? OR location LIKE ?)
                    ORDER BY CASE WHEN status = 'Ended' THEN 1 ELSE 0 END, start_date DESC
                """
                search_term = f"%{keyword}%" # 加上%可以在SQL代表任意字元
                cursor.execute(sql, (search_term, search_term)) # 執行 SQL 語句
            else:
                # 顯示所有上架中與已結束的展覽 (過期的排最後)
                cursor.execute("""
                    SELECT * FROM Exhibitions 
                    WHERE status IN ('Published', 'Ended') 
                    ORDER BY CASE WHEN status = 'Ended' THEN 1 ELSE 0 END, start_date DESC
                """)

            # 一次存取SQL傳回的所有資料
            rows = cursor.fetchall()
            # 補上轉換邏輯：將 List of Tuples 轉為 List of Dicts
            exhibitions = [to_dict(cursor, row) for row in rows]

        # 傳入 now 讓前端判斷是否顯示「已結束」
        # exhibitons列出剛剛抓取的展覽列表，keyword傳回搜尋框
        return render_template('index.html', exhibitions=exhibitions, keyword=keyword, now=datetime.now())
    finally:
        conn.close()


# --- 註冊 ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')

        if not name or not email or not password:
            flash('請填寫完整資訊')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 預設 role 為 'user'
                cursor.execute(
                    "INSERT INTO Members (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, 'user')",
                    (name, email, hashed_pw, phone)
                )
            conn.commit()
            flash('註冊成功，請登入！')
            return redirect(url_for('login'))
        except Exception as e:
            flash('註冊失敗 (Email 可能已存在)')
            print(e)
        finally:
            conn.close()
    return render_template('register.html')


# --- 登入 (含權限判斷) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Members WHERE email = ?", (email,))
                user = cursor.fetchone()
                if user:  # 如果有抓到資料，就轉成字典
                    columns = [column[0] for column in cursor.description]
                    user = dict(zip(columns, user))

            if user and check_password_hash(user['password_hash'], password):
                # 登入成功，設定 Session
                session.permanent = True  # 啟用自動過期
                session['user_id'] = user['member_id']
                session['user_name'] = user['name']
                session['role'] = user['role']  # 儲存身分

                # 根據身分導向不同頁面
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('帳號或密碼錯誤')
        finally:
            conn.close()
    return render_template('login.html')


# --- 登出 ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- 展覽詳細頁 (加入購物車 - 含嚴格過期檢查) ---
@app.route('/exhibition/<int:id>', methods=['GET', 'POST'])
def detail(id):
    conn = get_db_connection()
    if not conn: return "DB Error", 500

    try:
        with conn.cursor() as cursor:
            # === POST: 加入購物車 ===
            if request.method == 'POST':
                try:
                    quantity = int(request.form.get('quantity', 1))
                except ValueError:
                    quantity = 1

                if quantity <= 0:
                    flash("購買數量必須大於 0")
                    return redirect(request.url)

                session_id = request.form.get('session_id')

                # 後端防呆：嚴格檢查過期
                # 同時查詢「場次時間」與「展覽結束日期」
                sql = """
                    SELECT S.session_time, E.end_date 
                    FROM Sessions S
                    JOIN Exhibitions E ON S.exhibition_id = E.exhibition_id
                    WHERE S.session_id = ?
                """
                cursor.execute(sql, (session_id,))
                row = cursor.fetchone()
                if row: row = to_dict(cursor, row)  # 一行搞定轉換
                else:
                    flash("錯誤：找不到場次資訊")
                    return redirect(request.url)

                # 1. 檢查展覽是否已結束
                if row['end_date'] < datetime.now().date():
                    flash("很抱歉，此展覽活動已完全結束，無法購票！")
                    return redirect(request.url)

                # 2. 檢查場次時間是否已過
                if row['session_time'] < datetime.now():
                    flash("錯誤：該場次時間已過，無法購買！")
                    return redirect(request.url)

                # 建立商品物件
                item_template = {
                    'exhibition_id': id,
                    'exhibition_title': request.form.get('exhibition_title'),
                    'session_id': session_id,
                    'session_time_str': request.form.get('session_time_str'),
                    'ticket_type_id': request.form.get('ticket_type'),
                    'ticket_name': request.form.get('ticket_name'),
                    'price': float(request.form.get('price'))
                }

                cart = session.get('cart', [])
                # 依數量重複加入
                for _ in range(quantity):
                    cart.append(item_template.copy())

                session['cart'] = cart
                flash(f'已將 {quantity} 張票加入購物車')
                return redirect(url_for('index'))

            # === GET: 顯示頁面 ===
            cursor.execute("SELECT * FROM Exhibitions WHERE exhibition_id = ?", (id,))
            exhibition = cursor.fetchone()
            if exhibition:  # 如果有抓到資料，就轉成字典
                columns = [column[0] for column in cursor.description]
                exhibition = dict(zip(columns, exhibition))


            cursor.execute("SELECT * FROM Sessions WHERE exhibition_id = ? ORDER BY session_time", (id,))
            sessions = cursor.fetchall()
            if sessions:
                columns = [column[0] for column in cursor.description]
                sessions = [dict(zip(columns, row)) for row in sessions]

            cursor.execute("SELECT * FROM TicketTypes WHERE exhibition_id = ?", (id,))
            ticket_types = cursor.fetchall()
            if ticket_types:
                columns = [column[0] for column in cursor.description]
                ticket_types = [dict(zip(columns, row)) for row in ticket_types]

            if not exhibition: return "找不到該展覽", 404

            # ★ 傳入 now 給前端做按鈕停用判斷
            return render_template('detail.html',
                                   ex=exhibition,
                                   sessions=sessions,
                                   types=ticket_types,
                                   now=datetime.now())

    finally:
        conn.close()


# --- 查看購物車 ---
@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total_price)


# --- 清空購物車 ---
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))


# --- 結帳 (交易處理 + 原子性扣庫存) ---
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('請先登入才能結帳')
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash('購物車是空的')
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            total_amount = sum(item['price'] for item in cart)

            # 1. 建立訂單
            cursor.execute("SET NOCOUNT ON; INSERT INTO Orders (member_id, total_amount, status) VALUES (?, ?, 'Paid'); SELECT SCOPE_IDENTITY()",
                           (session['user_id'], total_amount))
            result = cursor.fetchone()  # 用 fetchone() 取得剛產生的 ID
            if result:
                order_id = int(result[0])
            else:
                raise Exception("無法取得訂單 ID")
                
            # 2. 處理每一張票 (扣庫存 + 建票)
            for item in cart:
                session_id = item['session_id']
                ticket_type_id = item['ticket_type_id']

                # [關鍵] 扣除庫存，若庫存不足會影響行數為 0 (防止超賣)
                cursor.execute("""
                    UPDATE Sessions 
                    SET capacity = capacity - 1 
                    WHERE session_id = ? AND capacity > 0
                """, (session_id,))

                if cursor.rowcount == 0:
                    raise Exception(f"很抱歉，場次「{item['session_time_str']}」已額滿，無法購買。")

                ticket_uuid = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO Tickets (ticket_uuid, order_id, ticket_type_id, session_id, status)
                    VALUES (?, ?, ?, ?, 'Unused')
                """, (ticket_uuid, order_id, ticket_type_id, session_id))

        conn.commit()
        session.pop('cart', None)
        flash(f'結帳成功！共購買 {len(cart)} 張票券')
        return redirect(url_for('my_tickets'))

    except Exception as e:
        conn.rollback()
        flash(f'結帳失敗: {e}')
        return redirect(url_for('view_cart'))
    finally:
        conn.close()


# --- 我的票券 ---
@app.route('/my_tickets')
def my_tickets():
    if 'user_id' not in session: return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT T.ticket_uuid, E.title, S.session_time, TT.name, T.status
                FROM Tickets T
                JOIN Orders O ON T.order_id = O.order_id
                JOIN TicketTypes TT ON T.ticket_type_id = TT.ticket_type_id
                JOIN Sessions S ON T.session_id = S.session_id
                JOIN Exhibitions E ON TT.exhibition_id = E.exhibition_id
                WHERE O.member_id = ?
                ORDER BY O.order_date DESC
            """
            cursor.execute(sql, (session['user_id'],))
            tickets = cursor.fetchall()
            return render_template('my_tickets.html', tickets=tickets)
    finally:
        conn.close()


# --- QR Code API ---
@app.route('/qrcode/<uuid>')
def serve_qrcode(uuid):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(uuid)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


# --- 現場核銷 API (輸入 PIN 碼) ---
@app.route('/api/use_ticket', methods=['POST'])
def api_use_ticket():
    data = request.get_json()
    uuid = data.get('uuid')
    input_pin = data.get('pin')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT T.status, E.validation_pin 
                FROM Tickets T
                JOIN TicketTypes TT ON T.ticket_type_id = TT.ticket_type_id
                JOIN Exhibitions E ON TT.exhibition_id = E.exhibition_id
                WHERE T.ticket_uuid = ?
            """
            cursor.execute(sql, (uuid,))
            row = cursor.fetchone()
            if row: row = to_dict(cursor, row)
            else: return {"success": False, "message": "找不到票券"}, 404

            if row['status'] == 'Used':
                return {"success": False, "message": "此票券已經使用過了"}

            if input_pin != row['validation_pin']:
                return {"success": False, "message": "核銷碼錯誤"}

            # 用 GETDATE() 取得當前時間
            cursor.execute("UPDATE Tickets SET status = 'Used', used_at = GETDATE() WHERE ticket_uuid = ?", (uuid,))
            conn.commit()
            return {"success": True, "message": "驗證成功，歡迎入場！"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}, 500
    finally:
        conn.close()


# ==========================================
# 後台管理路由 (Admin Dashboard)
# ==========================================

@app.route('/admin')
def admin_dashboard():
    # 檢查是否為管理員
    if 'user_id' not in session or not is_admin():
        flash("權限不足，請以管理員身分登入")
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Exhibitions ORDER BY exhibition_id DESC")
            
            rows = cursor.fetchall()
            # 補上轉換邏輯
            exhibitions = [to_dict(cursor, row) for row in rows]
        return render_template('admin/dashboard.html', exhibitions=exhibitions)
    finally:
        conn.close()


# --- 新增展覽 (自動新增主辦單位 + 圖片上傳) ---
@app.route('/admin/create', methods=['GET', 'POST'])
def admin_create_exhibition():
    if not is_admin(): return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                # 1. 處理主辦單位 (輸入名稱 -> 自動判斷ID)
                org_name = request.form['organizer_name'].strip()
                cursor.execute("SELECT organizer_id FROM Organizers WHERE name = ?", (org_name,))
                existing_org = cursor.fetchone()

                if existing_org:
                    organizer_id = existing_org[0]
                else:
                    cursor.execute("SET NOCOUNT ON; INSERT INTO Organizers (name) VALUES (?); SELECT SCOPE_IDENTITY()", (org_name,))
                    organizer_id = int(cursor.fetchone()[0])  # 用 fetchone() 取 ID

                # 2. 處理圖片上傳
                image_path = None
                if 'exhibition_image' in request.files:
                    file = request.files['exhibition_image']
                    if file and file.filename != '':
                        image_path = save_exhibition_image(file)          

                # 3. 新增展覽
                cursor.execute("""
                    INSERT INTO Exhibitions (organizer_id, title, location, description, start_date, end_date, status, validation_pin, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    organizer_id,
                    request.form['title'],
                    request.form['location'],
                    request.form['description'],
                    request.form['start_date'],
                    request.form['end_date'],
                    request.form['status'],
                    request.form.get('validation_pin', '1234'),
                    image_path
                ))
                conn.commit()
                flash(f'新增成功 (主辦: {org_name})')
                return redirect(url_for('admin_dashboard'))

            cursor.execute("SELECT * FROM Organizers")
            rows = cursor.fetchall()
            organizers = [to_dict(cursor, row) for row in rows]
            return render_template('admin/create.html', organizers=organizers)
    finally:
        conn.close()


# --- 編輯展覽 (修改內容與上下架 + 圖片更新) ---
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_exhibition(id):
    if not is_admin(): return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # POST: 更新資料
            if request.method == 'POST':
                # 1. 取得目前的圖片路徑
                cursor.execute("SELECT image_path FROM Exhibitions WHERE exhibition_id = ?", (id,))
                current = cursor.fetchone()
                old_image_path = current[0] if current else None
                
                # 2. 處理圖片上傳
                new_image_path = old_image_path  # 預設保留原圖
                
                # 檢查是否要刪除現有圖片
                if request.form.get('delete_image') == '1':
                    delete_old_image(old_image_path)
                    new_image_path = None
                
                # 檢查是否有上傳新圖片
                if 'exhibition_image' in request.files:
                    file = request.files['exhibition_image']
                    if file and file.filename != '':
                        # 刪除舊圖
                        delete_old_image(old_image_path)
                        # 儲存新圖
                        new_image_path = save_exhibition_image(file, id)                     
                
                # 3. 更新資料庫
                cursor.execute("""
                    UPDATE Exhibitions 
                    SET title=?, location=?, description=?, 
                        start_date=?, end_date=?, status=?, validation_pin=?, image_path=?
                    WHERE exhibition_id=?
                """, (
                    request.form['title'], request.form['location'], request.form['description'],
                    request.form['start_date'], request.form['end_date'], request.form['status'],
                    request.form['validation_pin'], new_image_path, id
                ))
                conn.commit()
                flash('展覽修改成功！')
                return redirect(url_for('admin_dashboard'))

            # GET: 顯示資料 (JOIN 主辦單位名稱)
            sql = """
                SELECT E.*, O.name as organizer_name 
                FROM Exhibitions E
                LEFT JOIN Organizers O ON E.organizer_id = O.organizer_id
                WHERE E.exhibition_id = ?
            """
            cursor.execute(sql, (id,))
            exhibition = cursor.fetchone()
            if exhibition:  # 如果有抓到資料，就轉成字典
                columns = [column[0] for column in cursor.description]
                exhibition = dict(zip(columns, exhibition))

            if not exhibition:
                flash('找不到該展覽')
                return redirect(url_for('admin_dashboard'))

            return render_template('admin/edit.html', ex=exhibition)
    finally:
        conn.close()


# --- 刪除展覽 ---
@app.route('/admin/delete/<int:id>', methods=['POST'])
def admin_delete_exhibition(id):
    if not is_admin(): return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 先取得展覽圖片路徑，稍後刪除檔案
            cursor.execute("SELECT image_path FROM Exhibitions WHERE exhibition_id = ?", (id,))
            result = cursor.fetchone()
            image_path = result[0] if result else None

            # 2. 刪除相關聯的資料 (注意外鍵順序)
            # 2.1 先刪除票券 (Tickets 關聯 Sessions 和 TicketTypes)
            cursor.execute("""
                DELETE FROM Tickets 
                WHERE session_id IN (SELECT session_id FROM Sessions WHERE exhibition_id = ?)
                   OR ticket_type_id IN (SELECT ticket_type_id FROM TicketTypes WHERE exhibition_id = ?)
            """, (id, id))
            
            # 2.2 刪除場次
            cursor.execute("DELETE FROM Sessions WHERE exhibition_id = ?", (id,))
            
            # 2.3 刪除票種
            cursor.execute("DELETE FROM TicketTypes WHERE exhibition_id = ?", (id,))
            
            # 3. 刪除展覽本身
            cursor.execute("DELETE FROM Exhibitions WHERE exhibition_id = ?", (id,))
            
            conn.commit()
            
            # 4. 刪除圖片檔案
            if image_path:
                delete_old_image(image_path)
            
            flash('展覽已成功刪除！')
            
    except Exception as e:
        conn.rollback()
        flash(f'刪除失敗: {e}')
        print(f"刪除展覽錯誤: {e}")
    finally:
        conn.close()
    
    return redirect(url_for('admin_dashboard'))


# --- 管理展覽細項 (場次與票種) ---
@app.route('/admin/manage/<int:id>', methods=['GET', 'POST'])
def admin_manage_exhibition(id):
    if not is_admin(): return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                # 新增場次
                if 'add_session' in request.form:
                    # 將前端格式: "2025-12-31T19:30" ->改成 資料庫格式: "2025-12-31 19:30:00"
                    s_time = request.form['session_time']
                    if 'T' in s_time:
                        s_time = s_time.replace('T', ' ')
                    if len(s_time) == 16: # 如果長度只有到分鐘
                        s_time += ':00'   # 補上秒數

                    cursor.execute("INSERT INTO Sessions (exhibition_id, session_time, capacity) VALUES (?, ?, ?)",
                                   (id, s_time, request.form['capacity']))
                    flash('場次已新增')

                # 新增票種
                if 'add_ticket_type' in request.form:
                    cursor.execute("INSERT INTO TicketTypes (exhibition_id, name, price) VALUES (?, ?, ?)",
                                   (id, request.form['name'], request.form['price']))
                    flash('票種已新增')
                conn.commit()

            cursor.execute("SELECT * FROM Exhibitions WHERE exhibition_id = ?", (id,))
            exhibition = cursor.fetchone()
            if exhibition:  # 如果有抓到資料，就轉成字典
                columns = [column[0] for column in cursor.description]
                exhibition = dict(zip(columns, exhibition))

            cursor.execute("SELECT * FROM Sessions WHERE exhibition_id = ?", (id,))
            sessions = cursor.fetchall()
            if sessions:
                columns = [column[0] for column in cursor.description]
                sessions = [dict(zip(columns, row)) for row in sessions]

            cursor.execute("SELECT * FROM TicketTypes WHERE exhibition_id = ?", (id,))
            ticket_types = cursor.fetchall()
            if ticket_types:
                columns = [column[0] for column in cursor.description]
                ticket_types = [dict(zip(columns, row)) for row in ticket_types]
            
            return render_template('admin/manage.html', ex=exhibition, sessions=sessions, types=ticket_types)
    finally:
        conn.close()


if __name__ == '__main__':
    # host='0.0.0.0' 表示監聽這台機器所有的 IP (包含外網 IP)
    # port=5000 是網站運作的埠號
    app.run(host='0.0.0.0', port=5000, debug=True)
