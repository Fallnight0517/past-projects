import pyodbc
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime


def init_database():
    print("開始初始化 SQL Server 資料庫")

    try:
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=localhost;'
            r'UID=XXXX;'
            r'PWD=XXXX;',
            autocommit=True
        )
        print("資料庫連線成功")
        cursor = conn.cursor()

        db_name = "ExhibitionTicketSystem"
        cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{db_name}')
            BEGIN
                CREATE DATABASE {db_name};
            END
        """)
        cursor.execute(f"USE {db_name};")

        print("正在重置資料表")
        tables = ['Tickets', 'Payments', 'Orders', 'TicketTypes', 'Sessions', 'Exhibitions', 'Members', 'Organizers']
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")

        print("正在建立新架構")
        queries = [
            """CREATE TABLE Organizers (
                organizer_id INT PRIMARY KEY IDENTITY(1,1),
                name NVARCHAR(100) NOT NULL,
                contact_person NVARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100)
            )""",
            """CREATE TABLE Members (
                member_id INT PRIMARY KEY IDENTITY(1,1),
                name NVARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                role VARCHAR(20) DEFAULT 'user',
                created_at DATETIME DEFAULT GETDATE()
            )""",
            """CREATE TABLE Exhibitions (
                exhibition_id INT PRIMARY KEY IDENTITY(1,1),
                organizer_id INT,
                title NVARCHAR(200) NOT NULL,
                location NVARCHAR(200),
                description NVARCHAR(MAX),
                start_date DATE,
                end_date DATE,
                status VARCHAR(20) DEFAULT 'Draft',
                validation_pin VARCHAR(20) DEFAULT '1234',
                image_path NVARCHAR(500),
                FOREIGN KEY (organizer_id) REFERENCES Organizers(organizer_id)
            )""",
            """CREATE TABLE Sessions (
                session_id INT PRIMARY KEY IDENTITY(1,1),
                exhibition_id INT NOT NULL,
                session_time DATETIME NOT NULL,
                capacity INT NOT NULL,
                FOREIGN KEY (exhibition_id) REFERENCES Exhibitions(exhibition_id)
            )""",
            """CREATE TABLE TicketTypes (
                ticket_type_id INT PRIMARY KEY IDENTITY(1,1),
                exhibition_id INT NOT NULL,
                name NVARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (exhibition_id) REFERENCES Exhibitions(exhibition_id)
            )""",
            """CREATE TABLE Orders (
                order_id INT PRIMARY KEY IDENTITY(1,1),
                member_id INT NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                order_date DATETIME DEFAULT GETDATE(),
                status VARCHAR(20) DEFAULT 'Pending',
                FOREIGN KEY (member_id) REFERENCES Members(member_id)
            )""",
            """CREATE TABLE Tickets (
                ticket_uuid VARCHAR(36) PRIMARY KEY,
                order_id INT NOT NULL,
                ticket_type_id INT NOT NULL,
                session_id INT,
                status VARCHAR(20) DEFAULT 'Unused',
                used_at DATETIME,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                FOREIGN KEY (ticket_type_id) REFERENCES TicketTypes(ticket_type_id),
                FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
            )"""
        ]
        for query in queries:
            cursor.execute(query)

        print("新增會員")
        members_data = [
            ('系統管理員', 'admin@example.com', 'scrypt:32768:8:1$d2wQswpB4NV4DquF$5aa45807a5b032b3623b2e1e10d8588e6bf28bc050ad8ebe435ee7fd9ce6692273134564e48a28cfd0d891427dc62c2316eb2b44e6f29cbdcd7de6edb802815b', '0900000000', 'admin'),
            ('王小明', 'ming.wang@gmail.com', 'scrypt:32768:8:1$aXoNIQEhR44iUA1X$efdc789b618a0e2ebb489c670a75872a0ebb4f8ed436dd93167db49e3eac0a86b758b3c7ced6fe28a62fea24f8aa6a4d794a124d01996d07f9ddfeeec9ca8945', '0912345678', 'user'),
            ('李美華', 'meihua.lee@yahoo.com.tw', 'scrypt:32768:8:1$sZ3c3LpXjmYfWB2y$f18f80e21005a468740d4de3c57874bb71ce75ea0afaf74436d844aa27998c4c7ae99465dfc9c76e7adfd61d03ea7d8b768e2af537aaeb0a49977d16400f1114', '0923456789', 'user'),
            ('張志豪', 'zhihao.chang@hotmail.com', 'scrypt:32768:8:1$r1oliOowaZNCT0dj$f3bfa18119de7aea82ad7accf5f54946118e45325a9571de85432be8512cafffd6148aa30e7bb041ac6aaf50755d2a44e528666b9ea32dad0ceadf759d42b3e1', '0934567890', 'user'),
            ('陳雅婷', 'yating.chen@gmail.com', 'scrypt:32768:8:1$OrhqMQaLDh1ainWg$306dd675ff513ae6c4a17e25d93335afe9f9ccb029111c9eba0a6106d6e8809385caee5e4e1534dc9b846fbb6b3eadb909b3656fe6e92caa67aeae3f5af3154e', '0945678901', 'user'),
            ('林建宏', 'jianhong.lin@outlook.com', 'scrypt:32768:8:1$Lr6aVnAxu6T7C8Y5$83527e1b40d5e74ca37d1955624a51c4518d421b4094a86e161976c016a356144d350be4e9f76faf0e51a2d2caac8c2470cc6230ada9119a9078e54186b14785', '0956789012', 'user'),
            ('黃淑芬', 'shufen.huang@gmail.com', 'scrypt:32768:8:1$5KzbLgsQq9Lqh80w$5fd3b0da1b12fed3e3401be2571094afeafc0417d14733d3c860ca2976790e91b940bddb4e0b3eec7a1c973ae094dd1fe3023167cad14b030e31dc397aa03c8e', '0967890123', 'user'),
            ('劉家銘', 'jiaming.liu@yahoo.com.tw', 'scrypt:32768:8:1$ZIEKa6tF3EtwvxCP$d12c3aa37d2064dfb6e43452c9177e675a12249295a768255d67353cc92c6b66e65b68cfccf0e16e157913418508b8abfb2ec35a8a62698c4bf7e984b2f9a304', '0978901234', 'user'),
            ('吳佩珊', 'peishan.wu@gmail.com', 'scrypt:32768:8:1$uSNvvHuD9qoyJPZZ$aa900494cad2a7067264a59d801b507ec8c6b33dba1c1eafe0abc5b8d125e4471815e63b6a12be2e8034023b47311b3afbc5e6d0b2f967cd098758c0138967c7', '0989012345', 'user'),
            ('蔡宗翰', 'zonghan.tsai@hotmail.com', 'scrypt:32768:8:1$yWIQyKvycesq93ad$571d1bed645499a3b224c4b3a6cf9bb2e07c6b3d74b90d9bc27030f4f48117595651ae9ebe811327f4d2f16cacf124693052cb62b9966913d18abf2776ba5d9c', '0990123456', 'user')
        ]
        for member in members_data:
            cursor.execute("""
                INSERT INTO Members (name, email, password_hash, phone, role)
                VALUES (?, ?, ?, ?, ?)""", member)

        print("新增主辦單位")
        organizers_data = [
            ('國立故宮博物院', '王館長', '02-28812021', 'service@npm.gov.tw'),
            ('台北市立美術館', '陳副館長', '02-25957656', 'info@tfam.museum'),
            ('國立台灣美術館', '林主任', '04-23723552', 'service@ntmofa.gov.tw'),
            ('高雄市立美術館', '張館長', '07-5550331', 'service@kmfa.gov.tw'),
            ('奇美博物館', '許執行長', '06-2660808', 'info@chimeimuseum.org'),
            ('聯合數位文創', '李經理', '02-77210772', 'service@udnfunlife.com'),
            ('寬宏藝術', '黃總監', '07-7809900', 'service@kharts.com.tw'),
            ('時藝多媒體', '周專員', '02-66169928', 'info@mediasphere.com.tw'),
            ('華山1914文創園區', '吳園長', '02-23581914', 'service@huashan1914.com'),
            ('松山文創園區', '蔡主任', '02-27651388', 'info@songshanculturalpark.org'),
            ('國立歷史博物館', '鄭館長', '02-23610270', 'service@nmh.gov.tw'),
            ('台北當代藝術館', '劉策展人', '02-25523721', 'info@mocataipei.org.tw'),
            ('朱銘美術館', '朱執行長', '02-24989940', 'service@juming.org.tw'),
            ('野獸國', '王企劃', '02-87719900', 'info@beastcommunity.com'),
            ('異想創造', '陳創意長', '02-27001234', 'service@imagination.com.tw'),
            ('閣林文創', '林總編', '02-23456789', 'info@greenlin.com.tw'),
            ('新光三越文教基金會', '李主任', '02-23891234', 'culture@skm.com.tw'),
            ('中正紀念堂管理處', '張處長', '02-23431100', 'service@cksmh.gov.tw'),
            ('台灣創意設計中心', '吳總監', '02-27458199', 'info@tdc.org.tw'),
            ('國立科學工藝博物館', '蘇館長', '07-3800089', 'service@nstm.gov.tw'),
        ]
        for org in organizers_data:
            cursor.execute("""
                INSERT INTO Organizers (name, contact_person, phone, email)
                VALUES (?, ?, ?, ?)""", org)

        print("新增展覽")
        exhibitions_data = [
            (1, '翠玉白菜：國寶的故事', '國立故宮博物院 正館', '深入探索故宮最具代表性的國寶翠玉白菜，透過科技互動了解其雕刻工藝與文化意涵。', '2024-06-01', '2024-12-31', 'Ended', '1234', '/static/uploads/exhibitions/exhibition_1_71a79a12.jpg'),  # id=1
            (6, '草間彌生：圓點宇宙', '華山1914文創園區 東2館', '日本當代藝術大師草間彌生的沉浸式體驗展，走進無限圓點的奇幻世界。', '2024-09-15', '2025-01-15', 'Ended', '1234', '/static/uploads/exhibitions/exhibition_2_c5b6383a.jpg'),  # id=2
            (8, '哆啦A夢50週年紀念展', '松山文創園區 二號倉庫', '慶祝哆啦A夢誕生50週年，重現經典場景，展出珍貴手稿與道具。', '2024-07-01', '2024-11-30', 'Ended', '1234', '/static/uploads/exhibitions/exhibition_3_134ae523.jpg'),  # id=3
            (7, '航海王：海賊王的寶藏', '高雄駁二藝術特區 P2倉庫', '航海王25週年特展，重現偉大航道經典場景，與草帽海賊團一同冒險！', '2024-08-10', '2024-12-15', 'Ended', '1234', '/static/uploads/exhibitions/exhibition_4_7ae34bc5.jpg'),  # id=4
            (2, '畢卡索：藍色時期特展', '台北市立美術館 地下樓', '聚焦畢卡索創作生涯中最動人的藍色時期，展出30幅珍貴原作。', '2024-05-20', '2024-10-20', 'Ended', '1234', '/static/uploads/exhibitions/exhibition_5_214be35f.jpg'),  # id=5
            (6, '莫內：光影印象派大展', '中正紀念堂 一展廳', '全球獨家沉浸式體驗，以360度環繞投影重現莫內花園，漫步在睡蓮池畔。', '2025-10-01', '2026-05-01', 'Published', '1234', '/static/uploads/exhibitions/exhibition_6_365db389.jpg'),  # id=6
            (8, '梵谷：星空夜色沉浸展', '華山1914文創園區 東3館', '穿越時空走進梵谷的畫作，體驗星夜的璀璨與向日葵的熱情。', '2025-11-15', '2026-05-31', 'Published', '1234', '/static/uploads/exhibitions/exhibition_7_39cde768.jpg'),  # id=7
            (3, '會動的文藝復興', '國立台灣美術館 大廳', '運用AI動態技術讓文藝復興名作「動」起來，達文西、米開朗基羅作品全新詮釋。', '2025-09-20', '2026-06-30', 'Published', '1234', '/static/uploads/exhibitions/exhibition_8_ddafc79a.png'),  # id=8
            (12, '奈良美智：夢遊娃娃世界', '台北當代藝術館', '日本人氣藝術家奈良美智台灣首展，展出經典大眼娃娃系列與全新創作。', '2025-12-01', '2026-05-31', 'Published', '1234', '/static/uploads/exhibitions/exhibition_9_df0fc5e0.jpg'),  # id=9
            (14, '蠟筆小新30週年特展', '松山文創園區 一號倉庫', '跟著小新一家展開爆笑冒險，重現春日部場景，限定周邊商品獨家販售。', '2025-11-01', '2026-05-28', 'Published', '1234', '/static/uploads/exhibitions/exhibition_10_84723ec4.jpg'),  # id=10
            (15, '角落小夥伴的夢幻假期', '新光三越信義新天地 A11 6F', '超療癒角落小夥伴主題展，打造夢幻度假場景，與白熊、炸蝦尾一起放鬆。', '2025-12-15', '2026-05-15', 'Published', '1234', '/static/uploads/exhibitions/exhibition_11_516fe2fe.jpg'),  # id=11
            (14, '吉卜力動畫世界特展', '華山1914文創園區 中4館', '走進宮崎駿的動畫世界，龍貓森林、神隱少女湯屋等經典場景1:1重現。', '2025-10-20', '2026-06-20', 'Published', '1234', '/static/uploads/exhibitions/exhibition_12_2b78540e.jpg'),  # id=12
            (6, '迪士尼百年經典展', '中正紀念堂 二展廳', '慶祝迪士尼100週年，從米奇到冰雪奇緣，回顧百年動畫魔法。', '2025-11-20', '2026-05-20', 'Published', '1234', '/static/uploads/exhibitions/exhibition_13_f74cb8b7.jpg'),  # id=13
            (7, '冰雪奇緣夢幻特展', '高雄市立美術館 特展區', '艾莎與安娜帶你走進艾倫戴爾王國，體驗冰雪魔法的奇幻世界。', '2025-12-01', '2026-06-01', 'Published', '1234', '/static/uploads/exhibitions/exhibition_14_a146924d.jpg'),  # id=14
            (15, '名偵探柯南科學搜查展', '國立科學工藝博物館', '化身小小偵探，運用科學辦案！體驗指紋採集、彈道分析等鑑識技術。', '2025-10-15', '2026-05-15', 'Published', '1234', '/static/uploads/exhibitions/exhibition_15_dd207b75.jpeg'),  # id=15
            (14, '寶可夢訓練家大集結', '南港展覽館 一館', '超大型寶可夢主題樂園，與皮卡丘互動、挑戰道館，捕捉專屬回憶！', '2025-12-20', '2026-05-30', 'Published', '1234', '/static/uploads/exhibitions/exhibition_16_693440e6.jpg'),  # id=16
            (6, '米奇與好朋友主題特展', '台北101 4F', '米奇95週年慶典，經典卡通場景重現，米妮、唐老鴨、高飛齊聚一堂。', '2025-11-25', '2026-05-25', 'Published', '1234', '/static/uploads/exhibitions/exhibition_17_b16c064e.jpg'),  # id=17
            (8, '達文西：曠世奇才展', '奇美博物館 特展廳', '文藝復興巨匠達文西的科學與藝術，展出手稿複製品與機械模型。', '2025-09-01', '2026-05-31', 'Published', '1234', '/static/uploads/exhibitions/exhibition_18_eda93322.jpg'),  # id=18
            (19, '安藤忠雄：建築的詩學', '台北市立美術館 二樓', '日本建築大師安藤忠雄回顧展，光與影的詩意空間，1:1清水模體驗區。', '2025-10-10', '2026-05-10', 'Published', '1234', '/static/uploads/exhibitions/exhibition_19_27944aa8.jpg'),  # id=19
            (9, 'teamLab：未來遊樂園', '華山1914文創園區 中5館', '日本超人氣數位藝術團隊teamLab互動體驗展，打造光影交織的奇幻世界。', '2025-12-01', '2026-06-30', 'Published', '1234', '/static/uploads/exhibitions/exhibition_20_e13b8443.jpg'),  # id=20
        ]
        for ex in exhibitions_data:
            cursor.execute("""
                INSERT INTO Exhibitions (organizer_id, title, location, description, start_date, end_date, status, validation_pin, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", ex)

        print("新增場次")
        sessions_data = [
            (1, '2024-08-15 10:00:00', 200),  # session_id=1
            (1, '2024-08-15 14:00:00', 200),  # session_id=2
            (2, '2024-11-20 10:00:00', 150),  # session_id=3
            (2, '2024-11-20 14:00:00', 150),  # session_id=4
            (2, '2024-11-20 18:00:00', 150),  # session_id=5
            (3, '2024-10-01 10:00:00', 300),  # session_id=6
            (3, '2024-10-01 14:00:00', 300),  # session_id=7
            (4, '2024-10-20 10:00:00', 250),  # session_id=8
            (4, '2024-10-20 14:00:00', 250),  # session_id=9
            (4, '2024-10-20 18:00:00', 250),  # session_id=10
            (5, '2024-09-15 10:00:00', 100),  # session_id=11
            (5, '2024-09-15 14:00:00', 100),  # session_id=12
            (6, '2026-04-25 10:00:00', 200),  # session_id=13
            (6, '2026-04-25 14:00:00', 200),  # session_id=14
            (6, '2026-04-25 18:00:00', 200),  # session_id=15
            (7, '2026-05-28 10:00:00', 180),  # session_id=16
            (7, '2026-05-28 14:00:00', 180),  # session_id=17
            (8, '2026-05-30 10:00:00', 250),  # session_id=18
            (8, '2026-05-30 14:00:00', 250),  # session_id=19
            (8, '2026-05-30 18:00:00', 250),  # session_id=20
            (9, '2026-04-05 10:00:00', 120),  # session_id=21
            (9, '2026-04-05 14:00:00', 120),  # session_id=22
            (10, '2026-05-27 10:00:00', 300),  # session_id=23
            (10, '2026-05-27 14:00:00', 300),  # session_id=24
            (10, '2026-05-27 18:00:00', 300),  # session_id=25
            (11, '2026-04-10 10:00:00', 200),  # session_id=26
            (11, '2026-04-10 14:00:00', 200),  # session_id=27
            (12, '2026-06-15 10:00:00', 250),  # session_id=28
            (12, '2026-06-15 14:00:00', 250),  # session_id=29
            (12, '2026-06-15 18:00:00', 250),  # session_id=30
            (13, '2026-04-20 10:00:00', 300),  # session_id=31
            (13, '2026-04-20 14:00:00', 300),  # session_id=32
            (14, '2026-05-25 10:00:00', 200),  # session_id=33
            (14, '2026-05-25 14:00:00', 200),  # session_id=34
            (14, '2026-05-25 18:00:00', 200),  # session_id=35
            (15, '2026-04-08 10:00:00', 220),  # session_id=36
            (15, '2026-04-08 14:00:00', 220),  # session_id=37
            (16, '2026-04-30 10:00:00', 500),  # session_id=38
            (16, '2026-04-30 14:00:00', 500),  # session_id=39
            (16, '2026-04-30 18:00:00', 500),  # session_id=40
            (17, '2026-04-01 10:00:00', 200),  # session_id=41
            (17, '2026-04-01 14:00:00', 200),  # session_id=42
            (18, '2026-04-12 10:00:00', 180),  # session_id=43
            (18, '2026-04-12 14:00:00', 180),  # session_id=44
            (18, '2026-04-12 18:00:00', 180),  # session_id=45
            (19, '2026-04-05 10:00:00', 150),  # session_id=46
            (19, '2026-04-05 14:00:00', 150),  # session_id=47
            (20, '2026-05-10 10:00:00', 243),  # session_id=48
            (20, '2026-05-10 14:00:00', 250),  # session_id=49
            (20, '2026-05-10 18:00:00', 250),  # session_id=50
        ]
        for s in sessions_data:
            cursor.execute("""
                INSERT INTO Sessions (exhibition_id, session_time, capacity)
                VALUES (?, ?, ?)""", s)

        print("新增票種")
        ticket_types_data = [
        ]
        for tt in ticket_types_data:
            cursor.execute("""
                INSERT INTO TicketTypes (exhibition_id, name, price)
                VALUES (?, ?, ?)""", tt)

        print("新增訂單")
        orders_data = [
        ]
        for order in orders_data:
            cursor.execute("""
                INSERT INTO Orders (member_id, total_amount, order_date, status)
                VALUES (?, ?, ?, ?)""", order)

        print("新增票券")
        tickets_data = [
        ]
        for ticket in tickets_data:
            cursor.execute("""
                INSERT INTO Tickets (ticket_uuid, order_id, ticket_type_id, session_id, status, used_at)
                VALUES (?, ?, ?, ?, ?, ?)""", ticket)

        conn.commit()
        print("資料庫初始化完成")

    except Exception as e:
        print(f"初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == '__main__':
    init_database()
