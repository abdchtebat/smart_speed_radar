# # app.py
# # ==================== Imports ====================
# import os, uuid, sqlite3
# from pathlib import Path
# from datetime import datetime

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from werkzeug.security import generate_password_hash, check_password_hash

# # محاولة استيراد المعالج الحقيقي؛ وإلا كنستعمل دالة بديلة بسيطة
# try:
#     from processors import run_analytics_with_speed  # يفترض دالة كتولّد فيديو+CSV وترجع summary
# except Exception:
#     def run_analytics_with_speed(input_path, output_video_path, csv_path,
#                                  weights="yolov8s.pt", conf=0.25, iou=0.45, imgsz=960,
#                                  speed_limit_kmh=60, pixels_per_meter=30.0):
#         """
#         بديل بسيط للاختبار فقط:
#         - كيكتب CSV صغير وهمي
#         - كينسخ الفيديو كما هو باش يبان فـواجهة Streamlit
#         """
#         import shutil
#         pd.DataFrame([
#             {"frame": 1, "plate": "TEST-001", "speed_kmh": speed_limit_kmh - 5, "over": 0},
#             {"frame": 120, "plate": "TEST-002", "speed_kmh": speed_limit_kmh + 12, "over": 1},
#         ]).to_csv(csv_path, index=False)
#         shutil.copyfile(input_path, output_video_path)
#         return {
#             "total_cars": 2,
#             "violations": 1,
#             "limit_kmh": speed_limit_kmh
#         }

# # ==================== Paths & Folders ====================
# BASE = Path.cwd()
# OUT_DIR = BASE / "outputs"
# OUT_DIR.mkdir(parents=True, exist_ok=True)

# DB_PATH = BASE / "users.db"

# # ==================== Streamlit Config & Style ====================
# st.set_page_config(page_title="Smart Speed Radar", page_icon="🚦", layout="centered")

# st.markdown("""
# <style>
# body { background: radial-gradient(circle at center, #001f1f 0%, #000c0c 70%); color:#E0FFFF; }
# .stButton>button { background:#00FF88; color:#000; border-radius:10px; padding:0.6rem 1.5rem; border:none; font-weight:700; transition:all .2s; }
# .stButton>button:hover { background:#00cc66; transform:scale(1.03); }
# h1,h2,h3 { color:#00FFCC; text-align:center; }
# .block { background:#002b25; padding:10px 14px; border-radius:10px; margin:8px 0; }
# </style>
# """, unsafe_allow_html=True)

# # ==================== SQLite helpers ====================
# def get_db():
#     conn = sqlite3.connect(DB_PATH.as_posix())
#     conn.row_factory = sqlite3.Row
#     return conn

# def init_db():
#     conn = get_db()
#     c = conn.cursor()
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL
#         )
#     """)
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS user_data (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             video_name TEXT,
#             speed_limit INTEGER,
#             result_summary TEXT,
#             created_at TEXT,
#             FOREIGN KEY(user_id) REFERENCES users(id)
#         )
#     """)
#     conn.commit()
#     conn.close()

# init_db()

# def register_user(username: str, password: str) -> bool:
#     username = username.strip()
#     if len(username) < 3 or len(password) < 4:
#         return False
#     conn = get_db()
#     try:
#         conn.execute(
#             "INSERT INTO users (username, password) VALUES (?, ?)",
#             (username, generate_password_hash(password))
#         )
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()

# def get_user(username: str):
#     conn = get_db()
#     row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
#     conn.close()
#     return row

# def save_user_analysis(user_id: int, video_name: str, speed_limit: int, summary):
#     conn = get_db()
#     conn.execute("""
#         INSERT INTO user_data (user_id, video_name, speed_limit, result_summary, created_at)
#         VALUES (?, ?, ?, ?, ?)
#     """, (user_id, video_name, speed_limit, str(summary), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
#     conn.commit()
#     conn.close()

# def get_user_analyses(user_id: int):
#     conn = get_db()
#     rows = conn.execute("""
#         SELECT video_name, speed_limit, result_summary, created_at
#         FROM user_data
#         WHERE user_id=?
#         ORDER BY created_at DESC
#     """, (user_id,)).fetchall()
#     conn.close()
#     return rows

# # ==================== Auth Pages ====================
# def login_page():
#     st.markdown("<h1>🛡️ SMART SPEED RADAR</h1>", unsafe_allow_html=True)
#     st.markdown("<h4 style='text-align:center;color:#00FF88;'>Système de détection intelligent</h4>", unsafe_allow_html=True)
#     st.markdown("---")

#     tab_login, tab_register = st.tabs(["🔑 Connexion", "🆕 Créer un compte"])

#     with tab_login:
#         username = st.text_input("👤 Nom d'utilisateur")
#         password = st.text_input("🔒 Mot de passe", type="password")
#         if st.button("Se connecter"):
#             user = get_user(username)
#             if user and check_password_hash(user["password"], password):
#                 st.session_state["user"] = user["username"]
#                 st.session_state["user_id"] = user["id"]
#                 st.rerun()
#             else:
#                 st.error("❌ Nom d’utilisateur ou mot de passe incorrect")

#     with tab_register:
#         new_user = st.text_input("🆕 Nom d'utilisateur")
#         new_pass = st.text_input("🔑 Mot de passe", type="password")
#         confirm_pass = st.text_input("🔁 Confirmer le mot de passe", type="password")
#         if st.button("Créer un compte"):
#             if new_pass != confirm_pass:
#                 st.error("❌ Les mots de passe ne correspondent pas.")
#             elif not register_user(new_user, new_pass):
#                 st.error("⚠️ Ce nom d’utilisateur existe déjà ou données غير صالحة.")
#             else:
#                 st.success("✅ Compte créé. تقدر دابا تسجّل الدخول.")

# # ==================== Dashboard ====================
# def radar_dashboard():
#     st.markdown(f"<h2>👋 Bienvenue, {st.session_state['user']}</h2>", unsafe_allow_html=True)
#     if st.button("🚪 Déconnexion"):
#         st.session_state.clear()
#         st.rerun()

#     st.markdown("---")
#     page = st.radio("🧭 Menu", ["📡 Nouvelle analyse", "📂 Mes analyses", "📊 Visualisation & Analyse"])

#     # ----------- Nouvelle analyse -----------
#     if page == "📡 Nouvelle analyse":
#         st.markdown("## 🎯 Module de détection de vitesse")
#         speed_limit = st.slider("🎛️ Limite de vitesse (km/h)", 10, 200, 60, 5)
#         uploaded = st.file_uploader("📂 Charger une vidéo", type=["mp4","mov","avi","mkv","webm"])

#         if uploaded and st.button("🚀 Lancer l’analyse"):
#             vid_id = uuid.uuid4().hex
#             in_path  = OUT_DIR / f"in_{vid_id}.mp4"
#             out_path = OUT_DIR / f"out_{vid_id}.mp4"
#             csv_path = OUT_DIR / f"stats_{vid_id}.csv"

#             with open(in_path, "wb") as f:
#                 f.write(uploaded.getbuffer())

#             with st.spinner("📡 Analyse radar en cours..."):
#                 try:
#                     summary = run_analytics_with_speed(
#                         input_path=str(in_path),
#                         output_video_path=str(out_path),
#                         csv_path=str(csv_path),
#                         weights="yolov8s.pt",
#                         conf=0.25,
#                         iou=0.45,
#                         imgsz=960,
#                         speed_limit_kmh=int(speed_limit),
#                         pixels_per_meter=30.0
#                     )
#                     save_user_analysis(
#                         st.session_state["user_id"],
#                         uploaded.name,
#                         int(speed_limit),
#                         summary
#                     )
#                     st.success("✅ Analyse terminée et enregistrée")

#                     st.video(str(out_path))
#                     with open(out_path, "rb") as vf:
#                         st.download_button("⬇️ Télécharger la vidéo", vf, file_name=out_path.name)
#                     if csv_path.exists():
#                         df_tmp = pd.read_csv(csv_path)
#                         st.dataframe(df_tmp.head())
#                         with open(csv_path, "rb") as cf:
#                             st.download_button("⬇️ Télécharger CSV", cf, file_name=csv_path.name)

#                 except Exception as e:
#                     st.error(f"❌ Erreur : {e}")

#     # ----------- Mes analyses -----------
#     elif page == "📂 Mes analyses":
#         st.markdown("## 🗂️ Historique de mes analyses")
#         rows = get_user_analyses(st.session_state["user_id"])
#         if not rows:
#             st.info("Aucune analyse enregistrée.")
#         else:
#             for a in rows:
#                 st.markdown(
#                     f"<div class='block'><b>📽️ Vidéo :</b> {a['video_name']}<br>"
#                     f"<b>🚦 Limite :</b> {a['speed_limit']} km/h<br>"
#                     f"<b>🕒 Date :</b> {a['created_at']}<br>"
#                     f"<b>🧩 Résumé :</b> {a['result_summary']}</div>",
#                     unsafe_allow_html=True
#                 )

#     # ----------- Visualisation & Analyse -----------
#     elif page == "📊 Visualisation & Analyse":
#         st.markdown("## 📊 Statistiques et Visualisation Radar")
#         user_id = st.session_state.get("user_id")
#         if not user_id:
#             st.warning("⚠️ سجّل الدخول أولاً.")
#             st.stop()

#         analyses = get_user_analyses(user_id)
#         if not analyses:
#             st.info("⚠️ ما كايناش تحليلات باش نعرضوها دابا.")
#             st.stop()

#         # Raw preview (اختياري)
#         st.subheader("🧩 Données brutes (أول عناصر)")
#         st.write(analyses[:2])

#         # تحويل النتائج إلى DataFrame
#         df = pd.DataFrame(analyses)
#         st.write("🧱 Colonnes détectées:", list(df.columns))

#         if "created_at" not in df.columns:
#             st.error("⚠️ 'created_at' ما كايناش فالداتا.")
#             st.dataframe(df)
#             st.stop()

#         df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
#         df["Jour"] = df["created_at"].dt.date

#         # ====== Statistiques générales ======
#         st.markdown("### 📈 Statistiques générales")
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Nombre d'analyses", len(df))
#         c2.metric("Vitesse moyenne définie", f"{df['speed_limit'].mean():.1f} km/h")
#         last = df["created_at"].dropna().max()
#         c3.metric("Dernière analyse", last.strftime("%Y-%m-%d %H:%M") if pd.notna(last) else "-")

#         # ====== Graphique 1 : Nombre d’analyses par jour ======
#         st.markdown("### 📊 Nombre d’analyses par jour")
#         counts = df.groupby("Jour").size()
#         fig, ax = plt.subplots()
#         counts.plot(kind="bar", ax=ax, color="#33FF99")
#         ax.set_xlabel("Date")
#         ax.set_ylabel("Nombre d'analyses")
#         ax.set_title("Analyses par jour")
#         st.pyplot(fig)

#         # ====== Graphique 2 : Distribution des limites de vitesse ======
#         st.markdown("### 🚦 Distribution des limites de vitesse choisies")
#         fig2, ax2 = plt.subplots()
#         df["speed_limit"].plot(kind="hist", bins=8, edgecolor="black", ax=ax2)
#         ax2.set_xlabel("Limite de vitesse (km/h)")
#         ax2.set_ylabel("Fréquence")
#         ax2.set_title("Distribution des limites de vitesse")
#         st.pyplot(fig2)

#         # ====== Résumé brut ======
#         st.markdown("### 🧩 Détails des analyses enregistrées")
#         st.dataframe(df[["video_name", "speed_limit", "created_at", "result_summary"]])

# # ==================== App Flow ====================
# if "user" not in st.session_state:
#     login_page()
# else:
#     radar_dashboard()









































# ==================== Imports ====================
import os, uuid, sqlite3, random
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

try:
    from processors import run_analytics_with_speed
except Exception:
    def run_analytics_with_speed(input_path, output_video_path, csv_path,
                                 weights="yolov8s.pt", conf=0.25, iou=0.45, imgsz=960,
                                 speed_limit_kmh=60, pixels_per_meter=30.0):
        import shutil
        pd.DataFrame([
            {"frame": 1, "plate": "TEST-001", "speed_kmh": speed_limit_kmh - 5, "over": 0},
            {"frame": 120, "plate": "TEST-002", "speed_kmh": speed_limit_kmh + 12, "over": 1},
        ]).to_csv(csv_path, index=False)
        shutil.copyfile(input_path, output_video_path)
        return {"total_cars": 2, "violations": 1, "limit_kmh": speed_limit_kmh}

# ==================== Paths & Folders ====================
BASE = Path.cwd()
OUT_DIR = BASE / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE / "users.db"

# ==================== Streamlit Config & Style ====================
st.set_page_config(page_title="Smart Speed Radar", page_icon="🚦", layout="centered")
st.markdown("""
<style>
body { background: radial-gradient(circle at center, #001f1f 0%, #000c0c 70%); color:#E0FFFF; }
.stButton>button { background:#00FF88; color:#000; border-radius:10px; padding:0.6rem 1.5rem; border:none; font-weight:700; transition:all .2s; }
.stButton>button:hover { background:#00cc66; transform:scale(1.03); }
h1,h2,h3 { color:#00FFCC; text-align:center; }
.block { background:#002b25; padding:10px 14px; border-radius:10px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)

# ==================== SQLite helpers ====================
def get_db():
    conn = sqlite3.connect(DB_PATH.as_posix())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            video_name TEXT,
            speed_limit INTEGER,
            result_summary TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

def register_user(username, password):
    username = username.strip()
    if len(username) < 3 or len(password) < 4:
        return False
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, generate_password_hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row

def save_user_analysis(user_id, video_name, speed_limit, summary):
    conn = get_db()
    conn.execute("""
        INSERT INTO user_data (user_id, video_name, speed_limit, result_summary, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, video_name, speed_limit, str(summary), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_analyses(user_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT video_name, speed_limit, result_summary, created_at
        FROM user_data WHERE user_id=? ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows

# ==================== Auth Pages ====================
def login_page():
    st.markdown("<h1>🛡️ SMART SPEED RADAR</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:#00FF88;'>Système de détection intelligent</h4>", unsafe_allow_html=True)
    st.markdown("---")

    tab_login, tab_register = st.tabs(["🔑 Connexion", "🆕 Créer un compte"])

    with tab_login:
        username = st.text_input("👤 Nom d'utilisateur")
        password = st.text_input("🔒 Mot de passe", type="password")
        if st.button("Se connecter"):
            user = get_user(username)
            if user and check_password_hash(user["password"], password):
                st.session_state["user"] = user["username"]
                st.session_state["user_id"] = user["id"]
                st.rerun()
            else:
                st.error("❌ Nom d’utilisateur ou mot de passe incorrect")

    with tab_register:
        new_user = st.text_input("🆕 Nom d'utilisateur")
        new_pass = st.text_input("🔑 Mot de passe", type="password")
        confirm_pass = st.text_input("🔁 Confirmer le mot de passe", type="password")
        if st.button("Créer un compte"):
            if new_pass != confirm_pass:
                st.error("❌ Les mots de passe ne correspondent pas.")
            elif not register_user(new_user, new_pass):
                st.error("⚠️ Ce nom d’utilisateur existe déjà ou données غير صالحة.")
            else:
                st.success("✅ Compte créé. تقدر دابا تسجّل الدخول.")

# ==================== Dashboard ====================
def radar_dashboard():
    st.markdown(f"<h2>👋 Bienvenue, {st.session_state['user']}</h2>", unsafe_allow_html=True)
    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    page = st.radio("🧭 Menu", ["📡 Nouvelle analyse", "📂 Mes analyses", "🖼️ Visualisation du dataset"])

    # ----------- Nouvelle analyse -----------
    if page == "📡 Nouvelle analyse":
        st.markdown("## 🎯 Module de détection de vitesse")
        speed_limit = st.slider("🎛️ Limite de vitesse (km/h)", 10, 200, 60, 5)
        uploaded = st.file_uploader("📂 Charger une vidéo", type=["mp4","mov","avi","mkv","webm"])

        if uploaded and st.button("🚀 Lancer l’analyse"):
            vid_id = uuid.uuid4().hex
            in_path  = OUT_DIR / f"in_{vid_id}.mp4"
            out_path = OUT_DIR / f"out_{vid_id}.mp4"
            csv_path = OUT_DIR / f"stats_{vid_id}.csv"
            with open(in_path, "wb") as f: f.write(uploaded.getbuffer())

            with st.spinner("📡 Analyse radar en cours..."):
                try:
                    summary = run_analytics_with_speed(
                        input_path=str(in_path), output_video_path=str(out_path),
                        csv_path=str(csv_path), speed_limit_kmh=int(speed_limit)
                    )
                    save_user_analysis(st.session_state["user_id"], uploaded.name, int(speed_limit), summary)
                    st.success("✅ Analyse terminée et enregistrée")
                    st.video(str(out_path))
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

    # ----------- Mes analyses -----------
    elif page == "📂 Mes analyses":
        st.markdown("## 🗂️ Historique de mes analyses")
        rows = get_user_analyses(st.session_state["user_id"])
        if not rows:
            st.info("Aucune analyse enregistrée.")
        else:
            for a in rows:
                st.markdown(
                    f"<div class='block'><b>📽️ Vidéo :</b> {a['video_name']}<br>"
                    f"<b>🚦 Limite :</b> {a['speed_limit']} km/h<br>"
                    f"<b>🕒 Date :</b> {a['created_at']}<br>"
                    f"<b>🧩 Résumé :</b> {a['result_summary']}</div>",
                    unsafe_allow_html=True
                )

    # ----------- Visualisation avancée du dataset -----------
    elif page == "🖼️ Visualisation du dataset":
        st.markdown("## 🖼️ Analyse visuelle du dataset d'images")
        data_dir = Path("data")
        if not data_dir.exists():
            st.error("⚠️ Le dossier 'data' est introuvable.")
            st.stop()

        categories = ["bus", "car", "truck", "motorcycle"]
        stats, img_data = [], []

        for c in categories:
            folder = data_dir / c
            imgs = list(folder.glob("*.*"))
            stats.append({"Classe": c, "Nombre d'images": len(imgs)})
            for img_path in imgs[:30]:
                try:
                    img = Image.open(img_path)
                    img_data.append({"Classe": c, "Width": img.width, "Height": img.height,
                                     "AspectRatio": round(img.width / img.height, 2)})
                except Exception:
                    continue

        df_stats, df_img = pd.DataFrame(stats), pd.DataFrame(img_data)
        st.dataframe(df_stats)

        # 1️⃣ Histogramme
        fig, ax = plt.subplots()
        ax.bar(df_stats["Classe"], df_stats["Nombre d'images"], color="#00FF99")
        ax.set_title("Histogramme : Nombre d'images par classe")
        st.pyplot(fig)

        # 2️⃣ Diagramme circulaire
        fig, ax = plt.subplots()
        ax.pie(df_stats["Nombre d'images"], labels=df_stats["Classe"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Diagramme circulaire des classes")
        st.pyplot(fig)

        # 3️⃣ Graphique en ligne
        fig, ax = plt.subplots()
        ax.plot(df_stats["Classe"], df_stats["Nombre d'images"], marker="o", color="#00CC99")
        ax.set_title("Graphique en ligne (évolution des classes)")
        st.pyplot(fig)

        # 4️⃣ Scatter Plot des dimensions
        if not df_img.empty:
            fig, ax = plt.subplots()
            ax.scatter(df_img["Width"], df_img["Height"], alpha=0.6, color="#33FF99")
            ax.set_title("Scatter Plot : Largeur vs Hauteur des images")
            ax.set_xlabel("Largeur (px)")
            ax.set_ylabel("Hauteur (px)")
            st.pyplot(fig)

        # 5️⃣ Boxplot
        if not df_img.empty:
            fig, ax = plt.subplots()
            df_img.boxplot(column=["Width","Height"], ax=ax)
            ax.set_title("Boxplot des dimensions")
            st.pyplot(fig)

        # 6️⃣ Heatmap
        if not df_img.empty:
            fig, ax = plt.subplots()
            sns.kdeplot(data=df_img, x="Width", y="Height", fill=True, cmap="Greens", ax=ax)
            ax.set_title("Heatmap des résolutions les plus fréquentes")
            st.pyplot(fig)

        # 7️⃣ Détection images petites
        df_outliers = df_img[(df_img["Width"] < 200) | (df_img["Height"] < 200)]
        if not df_outliers.empty:
            st.warning(f"⚠️ {len(df_outliers)} images très petites détectées.")
            st.dataframe(df_outliers.head())

        # 8️⃣ Galerie aléatoire
        st.markdown("### 🎨 Exemples aléatoires d'images")
        n_samples = st.slider("Nombre d'images par classe", 1, 5, 3)
        for c in categories:
            st.markdown(f"#### {c.capitalize()}")
            imgs = random.sample(list((data_dir / c).glob("*.*")), min(n_samples, len(list((data_dir / c).glob('*.*')))))
            cols = st.columns(len(imgs))
            for col, img_path in zip(cols, imgs):
                col.image(Image.open(img_path), caption=img_path.name, use_container_width=True)

# ==================== App Flow ====================
if "user" not in st.session_state:
    login_page()
else:
    radar_dashboard()
