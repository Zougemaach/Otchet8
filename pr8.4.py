import tkinter as tk
from tkinter import ttk, messagebox
import pyaudio
import numpy as np
import threading
import time
import wave
import math

# Попытка импорта BASS для радио (если библиотека установлена)
try:
    from pybass3 import Song
    HAS_BASS = True
except ImportError:
    HAS_BASS = False

class AudioStudioApp:
    def __init__(self, root):
        self.root = root
        root.title("Аудио Студия: Генератор, Запись, Радио")
        root.geometry("900x700")
        
        # Аудио параметры
        self.RATE = 44100
        self.CHUNK = 1024
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.is_recording = False
        self.radio_song = None
        
        self._build_ui()
        
    def _build_ui(self):
        # --- Вкладки ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Генератор
        self.tab_gen = ttk.Frame(notebook)
        notebook.add(self.tab_gen, text='Генератор сигналов')
        self._build_generator(self.tab_gen)
        
        # Вкладка 2: Радио
        self.tab_radio = ttk.Frame(notebook)
        notebook.add(self.tab_radio, text='Онлайн-Радио')
        self._build_radio(self.tab_radio)
        
        # Вкладка 3: Визуализация (упрощенная)
        self.tab_vis = ttk.Frame(notebook)
        notebook.add(self.tab_vis, text='Визуализация')
        self._build_visualizer(self.tab_vis)
        
        # Статус бар
        self.status = tk.Label(self.root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ================= ГЕНЕРАТОР =================
    def _build_generator(self, parent):
        frame = ttk.LabelFrame(parent, text="Параметры сигнала")
        frame.pack(fill='x', padx=10, pady=10)
        
        # Частота
        ttk.Label(frame, text="Частота (Гц):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.freq_var = tk.DoubleVar(value=440.0)
        ttk.Scale(frame, from_=50, to=2000, variable=self.freq_var, orient='horizontal').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Entry(frame, textvariable=self.freq_var, width=10).grid(row=0, column=2, padx=5)
        
        # Амплитуда
        ttk.Label(frame, text="Амплитуда:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.amp_var = tk.DoubleVar(value=0.5)
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.amp_var, orient='horizontal').grid(row=1, column=1, sticky='ew', padx=5)
        
        # Форма волны
        ttk.Label(frame, text="Форма:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.wave_var = tk.StringVar(value="sine")
        wave_combo = ttk.Combobox(frame, textvariable=self.wave_var, values=["sine", "square", "sawtooth"])
        wave_combo.grid(row=2, column=1, sticky='w', padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        self.btn_gen = ttk.Button(btn_frame, text="▶ Старт", command=self.toggle_generator)
        self.btn_gen.pack(side='left', padx=5)
        
        self.btn_record = ttk.Button(btn_frame, text="🔴 Запись (5 сек)", command=self.record_audio)
        self.btn_record.pack(side='left', padx=5)

    def get_waveform(self, t, freq, amp, shape):
        # Генерация волны с защитой от клиппинга
        if shape == "sine":
            sig = np.sin(2 * np.pi * freq * t)
        elif shape == "square":
            sig = np.sign(np.sin(2 * np.pi * freq * t))
        elif shape == "sawtooth":
            sig = 2 * (t * freq - np.floor(t * freq + 0.5))
        else:
            sig = np.sin(2 * np.pi * freq * t)
        return (sig * amp).astype(np.float32)

    def toggle_generator(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_gen.config(text="▶ Старт")
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
        else:
            self.is_playing = True
            self.btn_gen.config(text="⏹ Стоп")
            threading.Thread(target=self._play_loop, daemon=True).start()

    def _play_loop(self):
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.RATE, output=True)
        t = 0.0
        while self.is_playing:
            freq = self.freq_var.get()
            amp = self.amp_var.get()
            shape = self.wave_var.get()
            
            # Генерируем буфер
            t_arr = np.arange(self.CHUNK) / self.RATE + t
            data = self.get_waveform(t_arr, freq, amp, shape)
            
            # Если запись активна, пишем в файл
            if self.is_recording:
                self.frames.append((data * 32767).astype(np.int16).tobytes())
            
            self.stream.write(data.tobytes())
            t += self.CHUNK / self.RATE
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def record_audio(self):
        if self.is_recording:
            return
        self.frames = []
        self.is_recording = True
        self.status.config(text="Запись... (5 сек)")
        
        def stop_record():
            time.sleep(5)
            self.is_recording = False
            self._save_wav()
            self.status.config(text="Запись завершена")
            
        threading.Thread(target=stop_record, daemon=True).start()

    def _save_wav(self):
        if not self.frames:
            return
        wf = wave.open("recorded.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        messagebox.showinfo("Готово", "Файл recorded.wav сохранен")

    # ================= РАДИО =================
    def _build_radio(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="URL радиостанции:").pack()
        self.radio_url = ttk.Entry(frame, width=50)
        self.radio_url.insert(0, "http://stream.radioparadise.com/aac-320")
        self.radio_url.pack(pady=5)
        
        self.btn_radio = ttk.Button(frame, text="▶ Играть", command=self.toggle_radio)
        self.btn_radio.pack(pady=10)
        
        if not HAS_BASS:
            ttk.Label(frame, text="⚠️ Для радио установите pybass3 и bass.dll", foreground="red").pack(pady=10)

    def toggle_radio(self):
        if not HAS_BASS:
            messagebox.showerror("Ошибка", "Библиотека BASS не установлена. pip install pybass3")
            return
            
        if self.radio_song:
            self.radio_song.stop()
            self.radio_song = None
            self.btn_radio.config(text="▶ Играть")
            self.status.config(text="Радио остановлено")
        else:
            try:
                url = self.radio_url.get()
                self.radio_song = Song(url)
                self.radio_song.play()
                self.btn_radio.config(text="⏹ Стоп")
                self.status.config(text=f"Играет: {url}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось запустить: {e}")

    # ================= ВИЗУАЛИЗАЦИЯ =================
    def _build_visualizer(self, parent):
        # Простой Canvas для осциллограммы
        self.canvas = tk.Canvas(parent, bg='black', height=200)
        self.canvas.pack(fill='x', padx=10, pady=10)
        self.canvas.bind("<Configure>", self.draw_visual)
        
        # Кнопка для обновления (чтобы не нагружать систему постоянными вызовами)
        ttk.Button(parent, text="Обновить визуализацию", command=self.draw_visual).pack(pady=5)

    def draw_visual(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Рисуем сетку
        for i in range(0, w, 50):
            self.canvas.create_line(i, 0, i, h, fill="#222")
        self.canvas.create_line(0, h//2, w, h//2, fill="#444")
        
        # Генерируем тестовую волну для отображения (от текущих настроек)
        freq = self.freq_var.get()
        amp = self.amp_var.get()
        shape = self.wave_var.get()
        
        points = []
        for x in range(w):
            t = (x / w) * (2 / freq) # Показываем 2 периода
            val = self.get_waveform(np.array([t]), freq, amp, shape)[0]
            y = h//2 - val * (h//2 - 10)
            points.append((x, y))
            
        if points:
            self.canvas.create_line(points, fill="#00ff00", width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioStudioApp(root)
    root.mainloop()
