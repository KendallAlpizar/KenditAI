import customtkinter as ctk
import pyodbc
import ollama
import threading
import speech_recognition as sr
import os
import pickle
import datetime
from PIL import Image
from tkinter import Menu
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class KenditAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. CONFIGURACIÓN DE LA VENTANA ---
        self.title("🧠 KenditAI - Ultimate Edition")
        self.geometry("1300x950")
        ctk.set_appearance_mode("dark")

        # --- 2. ESTADOS Y VARIABLES DE CONTROL ---
        self.chat_id_actual = None
        self.esta_pensando = False
        self.escuchando = False 
        self.abortar_ia = False
        self.google_user = None
        self.db_string = 'Driver={SQL Server};Server=KENDALLPC;Database=AcademiaDB;Trusted_Connection=yes;'
        self.cache_guest = [] 
        self.guest_id_counter = 0

        # --- 3. CARGA DINÁMICA DE ICONOS (Desde /icons) ---
        ruta_base = os.path.dirname(__file__)
        carpeta_icons = os.path.join(ruta_base, "icons")

        try:
            self.icon_mic = ctk.CTkImage(
                light_image=Image.open(os.path.join(carpeta_icons, "microfono.png")),
                dark_image=Image.open(os.path.join(carpeta_icons, "microfono.png")),
                size=(24, 24))
            
            self.icon_send = ctk.CTkImage(
                light_image=Image.open(os.path.join(carpeta_icons, "enviar-mensaje.png")),
                dark_image=Image.open(os.path.join(carpeta_icons, "enviar-mensaje.png")),
                size=(24, 24))
            
            self.icon_stop = ctk.CTkImage(
                light_image=Image.open(os.path.join(carpeta_icons, "boton-detener.png")),
                dark_image=Image.open(os.path.join(carpeta_icons, "boton-detener.png")),
                size=(24, 24))
            print("✅ Iconos cargados correctamente.")
        except Exception as e:
            print(f"⚠️ Error al cargar iconos: {e}")
            self.icon_mic = self.icon_send = self.icon_stop = None

        # --- 4. DISEÑO DE LA INTERFAZ (UI LAYOUT) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR (Panel Izquierdo)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#121212")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkButton(self.sidebar, text="+ Nuevo Chat", font=("Segoe UI Bold", 14),
                     fg_color="#343541", command=self.reset_ui).pack(pady=20, padx=15, fill="x")
        
        self.frame_lista_chats = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.frame_lista_chats.pack(fill="both", expand=True, padx=5, pady=5)

        self.btn_session = ctk.CTkButton(self.sidebar, text="Iniciar Sesión", font=("Segoe UI", 12), 
                                        fg_color="#1f538d", height=32, command=self.toggle_session)
        self.btn_session.pack(side="bottom", pady=20, padx=20, fill="x")

        self.label_usuario = ctk.CTkLabel(self.sidebar, text="Perfil: Guest", font=("Segoe UI", 12), text_color="gray")
        self.label_usuario.pack(side="bottom", pady=(0, 5))

        # ÁREA CENTRAL (Chat)
        self.main_container = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Configuración de filas para el contenedor principal (Chat, Input, Footer)
        self.main_container.grid_rowconfigure(0, weight=1) 
        self.main_container.grid_rowconfigure(1, weight=0)
        self.main_container.grid_rowconfigure(2, weight=0) 
        self.main_container.grid_columnconfigure(0, weight=1)

        self.chat_view = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.chat_view.grid(row=0, column=0, sticky="nsew")

        # --- 5. BARRA DE ENTRADA (Input Bar) ---
        self.input_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_container.grid(row=1, column=0, pady=(10, 15), padx=40, sticky="ew")
        
        self.input_wrapper = ctk.CTkFrame(self.input_container, corner_radius=25, fg_color="#303135")
        self.input_wrapper.pack(fill="x", expand=True)
        self.input_wrapper.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkTextbox(self.input_wrapper, fg_color="transparent", font=("Segoe UI", 16), wrap="word", height=50)
        self.user_input.grid(row=0, column=0, padx=(20, 5), pady=10, sticky="ew")
        
        self.btn_mic = ctk.CTkButton(
            self.input_wrapper, 
            image=self.icon_mic, 
            text="" if self.icon_mic else "🎙️",
            width=45, height=45, 
            fg_color="transparent", 
            hover_color="#40414f",
            command=self.toggle_dictado
        )
        self.btn_mic.grid(row=0, column=1, padx=2)

        self.btn_action = ctk.CTkButton(
            self.input_wrapper, 
            image=self.icon_send, 
            text="" if self.icon_send else "➤",
            width=45, height=45, 
            fg_color="transparent", 
            hover_color="#40414f",
            command=self.click_boton_accion
        )
        self.btn_action.grid(row=0, column=2, padx=(2, 15))

        # --- 6. BRANDING & COPYRIGHT FOOTER ---
        self.brand_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=30)
        self.brand_frame.grid(row=2, column=0, pady=(0, 10), sticky="ew")
        
        anio_actual = datetime.datetime.now().year
        
        self.label_copyright = ctk.CTkLabel(
            self.brand_frame, 
            text=f"© {anio_actual} KenditAI | Ultimate Edition",
            font=("Segoe UI", 11),
            text_color="#555555"
        )
        self.label_copyright.pack(side="left", padx=45)

        self.label_author = ctk.CTkLabel(
            self.brand_frame, 
            text="Developed by Kendall Jesus Alpizar Rodriguez",
            font=("Segoe UI Bold", 11),
            text_color="#1f538d"
        )
        self.label_author.pack(side="right", padx=45)

        # --- 7. MENÚS Y EVENTOS FINAL ---
        self.menu_contextual = Menu(self, tearoff=0, bg="#202123", fg="white")
        self.menu_contextual.add_command(label="🗑️ Eliminar Chat", command=self.confirmar_eliminacion)
        self.user_input.bind("<Return>", self.manejar_teclado)
        self.verificar_sesion_inicial()

    # --- LÓGICA DE VOZ ---
    def toggle_dictado(self):
        if not self.escuchando:
            self.escuchando = True
            self.btn_mic.configure(fg_color="#e74c3c")
            threading.Thread(target=self._hilo_dictado, daemon=True).start()
        else:
            self.escuchando = False
            self.btn_mic.configure(fg_color="transparent")

    def _hilo_dictado(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while self.escuchando:
                try:
                    audio = r.listen(source, phrase_time_limit=8)
                    texto = r.recognize_google(audio, language='es-CR')
                    self.after(0, lambda t=texto: self.user_input.insert("end", f" {t}"))
                except: continue

    # --- LÓGICA DE CHAT & STOP ---
    def enviar_mensaje(self):
        txt = self.user_input.get("1.0", "end-1c").strip()
        if not txt or self.esta_pensando: return
        self.user_input.delete("1.0", "end")
        self.crear_mensaje("Usuario", txt)
        
        self.esta_pensando = True
        self.btn_action.configure(image=self.icon_stop, text="" if self.icon_stop else "⏹️", fg_color="#b23b3b")
        
        self.current_ia_res = self.crear_mensaje("IA", "...")
        threading.Thread(target=self._proceso_fondo, args=(txt,), daemon=True).start()

    def _proceso_fondo(self, pregunta):
        self.abortar_ia = False
        if self.google_user:
            if self.chat_id_actual is None:
                res = self.ejecutar_db("INSERT INTO Chats (Nombre, GoogleEmail) OUTPUT INSERTED.ChatID VALUES (?, ?)", (pregunta[:25], self.google_user['email']), fetchone=True)
                self.chat_id_actual = res[0]
                self.after(0, self.actualizar_lista_historial)
            self.ejecutar_db("INSERT INTO Mensajes (ChatID, Emisor, Mensaje) VALUES (?, 'Usuario', ?)", (self.chat_id_actual, pregunta))
        else:
            if self.chat_id_actual is None:
                self.guest_id_counter += 1
                self.chat_id_actual = self.guest_id_counter
                self.cache_guest.append({'id': self.chat_id_actual, 'nombre': pregunta[:25], 'mensajes': []})
                self.after(0, self.actualizar_lista_historial)

        res_completa = ""
        try:
            for chunk in ollama.chat(model='phi3', messages=[{'role': 'user', 'content': pregunta}], stream=True):
                if self.abortar_ia: break
                cont = chunk['message']['content']
                if cont:
                    res_completa += cont
                    self.after(10, lambda t=res_completa: self.current_ia_res.configure(text=t))
            
            if not self.abortar_ia:
                if self.google_user: self.ejecutar_db("INSERT INTO Mensajes (ChatID, Emisor, Mensaje) VALUES (?, 'IA', ?)", (self.chat_id_actual, res_completa))
                else:
                    chat = next(c for c in self.cache_guest if c['id'] == self.chat_id_actual)
                    chat['mensajes'].append({'emisor': 'IA', 'texto': res_completa})
        finally:
            self.esta_pensando = False
            self.after(0, lambda: self.btn_action.configure(image=self.icon_send, text="" if self.icon_send else "➤", fg_color="transparent"))

    def click_boton_accion(self):
        if self.esta_pensando:
            self.abortar_ia = True 
        else:
            self.enviar_mensaje()

    # --- HELPERS UI & DB ---
    def ejecutar_db(self, query, params=(), fetch=False, fetchone=False):
        try:
            with pyodbc.connect(self.db_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if not fetch and not fetchone: conn.commit(); return True
                    return cursor.fetchone() if fetchone else cursor.fetchall()
        except: return None

    def crear_mensaje(self, emisor, texto):
        es_user = (emisor == "Usuario")
        contenedor = ctk.CTkFrame(self.chat_view, fg_color="#1f538d" if es_user else "transparent", corner_radius=15)
        contenedor.pack(padx=20, pady=10, anchor="e" if es_user else "w")
        if not es_user: ctk.CTkLabel(contenedor, text="🧠 KenditAI", font=("Segoe UI Bold", 12), text_color="#3498db").pack(anchor="w", padx=10)
        lbl = ctk.CTkLabel(contenedor, text=texto, font=("Segoe UI", 15), wraplength=700, justify="left", padx=15, pady=10)
        lbl.pack()
        self.chat_view._parent_canvas.yview_moveto(1.0)
        return lbl

    def reset_ui(self):
        self.chat_id_actual = None
        for child in self.chat_view.winfo_children(): child.destroy()
        self.actualizar_lista_historial()

    def actualizar_lista_historial(self):
        for w in self.frame_lista_chats.winfo_children(): w.destroy()
        if self.google_user:
            res = self.ejecutar_db("SELECT ChatID, Nombre FROM Chats WHERE GoogleEmail = ? ORDER BY FechaCreacion DESC", (self.google_user['email'],), fetch=True)
            if res:
                for c_id, nombre in res:
                    btn = ctk.CTkButton(self.frame_lista_chats, text=f"💬 {nombre}", anchor="w", fg_color="transparent", command=lambda cid=c_id: self.cargar_chat(cid))
                    btn.pack(fill="x", pady=2)
                    btn.bind("<Button-3>", lambda e, cid=c_id: self.mostrar_menu(e, cid))
        else:
            for c in self.cache_guest:
                btn = ctk.CTkButton(self.frame_lista_chats, text=f"💬 {c['nombre']}", anchor="w", fg_color="transparent", command=lambda cid=c['id']: self.cargar_chat(cid))
                btn.pack(fill="x", pady=2)

    def cargar_chat(self, chat_id):
        self.abortar_ia = True
        self.chat_id_actual = chat_id
        for child in self.chat_view.winfo_children(): child.destroy()
        if self.google_user:
            msjs = self.ejecutar_db("SELECT Emisor, Mensaje FROM Mensajes WHERE ChatID = ? ORDER BY Fecha ASC", (chat_id,), fetch=True)
            if msjs: 
                for e, m in msjs: self.crear_mensaje(e, m)
        else:
            chat = next((c for c in self.cache_guest if c['id'] == chat_id), None)
            if chat:
                for m in chat['mensajes']: self.crear_mensaje(m['emisor'], m['texto'])

    # --- SESIÓN GOOGLE ---
    def toggle_session(self):
        if self.google_user:
            if os.path.exists('token.pickle'): os.remove('token.pickle')
            self.cache_guest = []
            self.reset_ui()
            self.entrar_modo_guest()
        else:
            self.login_win = ctk.CTkToplevel(self)
            self.login_win.title("Acceso")
            self.login_win.geometry("300x120")
            self.login_win.attributes("-topmost", True)
            ctk.CTkLabel(self.login_win, text="🔑 Iniciando sesión en el navegador...").pack(pady=20)
            threading.Thread(target=self.autenticar_google, args=(True,), daemon=True).start()

    def autenticar_google(self, forzar=False):
        SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token: creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0, prompt='select_account' if forzar else None)
            with open('token.pickle', 'wb') as token: pickle.dump(creds, token)
        try:
            service = build('oauth2', 'v2', credentials=creds)
            self.google_user = service.userinfo().get().execute()
            if hasattr(self, 'login_win'): self.after(0, self.login_win.destroy)
            self.after(0, self.reset_ui)
            self.after(0, lambda: self.label_usuario.configure(text=f"Cuenta:\n{self.google_user['email']}", text_color="#3498db"))
            self.after(0, lambda: self.btn_session.configure(text="Cerrar Sesión", fg_color="#444"))
            self.after(0, self.actualizar_lista_historial)
        except: self.entrar_modo_guest()

    def entrar_modo_guest(self):
        self.google_user = None
        self.label_usuario.configure(text="Perfil: Guest", text_color="gray")
        self.btn_session.configure(text="Iniciar Sesión", fg_color="#1f538d")
        self.actualizar_lista_historial()

    def verificar_sesion_inicial(self):
        if os.path.exists('token.pickle'):
            threading.Thread(target=self.autenticar_google, args=(False,), daemon=True).start()
        else: self.entrar_modo_guest()

    def mostrar_menu(self, event, chat_id):
        self.chat_para_eliminar = chat_id
        self.menu_contextual.post(event.x_root, event.y_root)

    def confirmar_eliminacion(self):
        if self.google_user:
            self.ejecutar_db("DELETE FROM Mensajes WHERE ChatID = ?", (self.chat_para_eliminar,))
            self.ejecutar_db("DELETE FROM Chats WHERE ChatID = ?", (self.chat_para_eliminar,))
        else: self.cache_guest = [c for c in self.cache_guest if c['id'] != self.chat_para_eliminar]
        self.reset_ui()

    def manejar_teclado(self, event):
        self.enviar_mensaje()
        return "break"

if __name__ == "__main__":
    app = KenditAIApp()
    app.mainloop()