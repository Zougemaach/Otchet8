import tkinter as tk
from tkinter import ttk, messagebox
import smtplib
from email.mime.text import MIMEText
import requests

# ─── НАСТРОЙКИ (ВСТАВЬТЕ СВОИ ДАННЫЕ) ───────────────────────────
# Email (SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASS = "your_app_password"  # Пароль приложения, не обычный пароль!

# SMS (Twilio)
TWILIO_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_TOKEN = "your_auth_token"
TWILIO_FROM = "+15017122661"  # Ваш номер от Twilio

# Telegram
TG_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TG_CHAT_ID = "123456789"  # ID чата, куда отправлять

# WhatsApp (через WSApi или аналог)
WA_API_KEY = "your_wa_api_key"
WA_INSTANCE_ID = "your_instance_id"
# ────────────────────────────────────────────────────────────────


class UniversalMessengerApp:
    def __init__(self, root):
        self.root = root
        root.title("Универсальный отправитель сообщений")
        root.geometry("700x600")
        root.configure(bg="#f0f0f0")

        self._build_ui()

    def _build_ui(self):
        # Заголовок
        tk.Label(self.root, text="Отправка сообщений",
                 font=("Segoe UI", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Выбор канала
        frame_channel = tk.LabelFrame(self.root, text="Канал связи", bg="#f0f0f0")
        frame_channel.pack(fill="x", padx=20, pady=5)

        self.channel_var = tk.StringVar(value="email")
        channels = [
            ("📧 Email", "email"),
            ("📱 SMS (Twilio)", "sms"),
            ("✈️ Telegram", "telegram"),
            ("💬 WhatsApp", "whatsapp"),
        ]

        for text, val in channels:
            ttk.Radiobutton(frame_channel, text=text, variable=self.channel_var,
                            value=val, command=self._on_channel_change).pack(anchor="w", padx=10, pady=2)

        # Параметры
        frame_params = tk.LabelFrame(self.root, text="Параметры", bg="#f0f0f0")
        frame_params.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_params, text="Получатель:", bg="#f0f0f0").pack(anchor="w", padx=10)
        self.recipient_entry = tk.Entry(frame_params, width=50)
        self.recipient_entry.pack(padx=10, pady=(0, 10))
        self.recipient_entry.insert(0, "test@example.com")

        # Сообщение
        frame_msg = tk.LabelFrame(self.root, text="Сообщение", bg="#f0f0f0")
        frame_msg.pack(fill="both", expand=True, padx=20, pady=5)

        self.msg_text = tk.Text(frame_msg, height=8, font=("Segoe UI", 10))
        self.msg_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.msg_text.insert("1.0", "Привет! Это тестовое сообщение из приложения.")

        # Кнопка отправки
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🚀 Отправить", command=self.send_message).pack()

        # Статус
        self.status = tk.Label(self.root, text="Готов", bd=1, relief="sunken", anchor="w", bg="white")
        self.status.pack(side="bottom", fill="x")

    def _on_channel_change(self):
        channel = self.channel_var.get()
        if channel == "email":
            self.recipient_entry.delete(0, tk.END)
            self.recipient_entry.insert(0, "test@example.com")
        elif channel == "sms":
            self.recipient_entry.delete(0, tk.END)
            self.recipient_entry.insert(0, "+15558675310")
        elif channel == "telegram":
            self.recipient_entry.delete(0, tk.END)
            self.recipient_entry.insert(0, "123456789") # Chat ID
        elif channel == "whatsapp":
            self.recipient_entry.delete(0, tk.END)
            self.recipient_entry.insert(0, "1234567890")

    def send_message(self):
        channel = self.channel_var.get()
        recipient = self.recipient_entry.get().strip()
        text = self.msg_text.get("1.0", "end-1c").strip()

        if not recipient or not text:
            messagebox.showwarning("Внимание", "Заполните получателя и текст!")
            return

        self.status.config(text=f"Отправка через {channel}...")
        self.root.update()

        try:
            if channel == "email":
                self._send_email(recipient, text)
            elif channel == "sms":
                self._send_sms(recipient, text)
            elif channel == "telegram":
                self._send_telegram(recipient, text)
            elif channel == "whatsapp":
                self._send_whatsapp(recipient, text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить: {e}")
            self.status.config(text="Ошибка отправки")

    def _send_email(self, to, text):
        msg = MIMEText(text)
        msg['Subject'] = "Сообщение из приложения"
        msg['From'] = SMTP_USER
        msg['To'] = to

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        self.status.config(text="✅ Email отправлен!")
        messagebox.showinfo("Успех", "Письмо отправлено.")

    def _send_sms(self, to, text):
        # Twilio API
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
        data = {"From": TWILIO_FROM, "To": to, "Body": text}
        response = requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_TOKEN))

        if response.status_code == 201:
            self.status.config(text="✅ SMS отправлено!")
            messagebox.showinfo("Успех", "SMS отправлено.")
        else:
            raise Exception(f"Twilio Error: {response.text}")

    def _send_telegram(self, chat_id, text):
        # Telegram Bot API
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            self.status.config(text="✅ Telegram отправлен!")
            messagebox.showinfo("Успех", "Сообщение в Telegram отправлено.")
        else:
            raise Exception(f"Telegram Error: {response.text}")

    def _send_whatsapp(self, to, text):
        # Пример через WSApi (логика зависит от вашего провайдера)
        # Здесь просто заглушка, так как нужен реальный API
        messagebox.showinfo("Внимание", "Для WhatsApp нужен рабочий API-ключ (например, WSApi).")
        self.status.config(text="WhatsApp: требуется настройка API")


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalMessengerApp(root)
    root.mainloop()
