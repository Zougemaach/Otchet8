import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
import threading
import wave
import time
import math

# Попытка импорта BASS для радио
try:
    from pybass3 import Song
    HAS_BASS = True
except ImportError:
    HAS_BASS = False


class AudioStudioApp:
    def __init__(self, root):
        self.root = root
        root.title("Аудио Студия (SoundDevice)")
        root.geometry("1000x750")
        root.configure(bg="#f0f0f0")

        # Аудио параметры
        self.RATE = 44100
        self.BLOCK_SIZE = 1024
        
        # Состояние
        self.is_playing = False
        self.is_recording = False
        self.recorded_frames = []
        self.radio_song = None
        
        # Буфер для визуализации (последние данные)
        self.last_data = np.zeros(self.BLOCK_SIZE)
        
        self._build_ui()
        self._animate()

    def _build_ui(self):
        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_gen = ttk.Frame(self.notebook)
        self.tab_radio = ttk.Frame(self.notebook)
        self.tab_vis = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_gen, text="🎛️ Генератор")
        self.notebook.add(self.tab_radio, text="📻 Радио")
        self.notebook.add(self.tab_vis, text="📊 Визуализация")

        self._build_generator()
        self._build_radio()
        self._build_vis()

        # Статус
        self.status = tk.Label(self.root, text="Готов",
                               bd=1, relief="sunken", anchor="w",
                               bg="white", font=("Segoe UI", 9))
        self.status.pack(side="bottom", fill="x")

    def _build_generator(self):
        frame = ttk.LabelFrame(self.tab_gen, text="Параметры сигнала")
        frame.pack(fill="x", padx=10, pady=10)

        # Частота
        ttk.Label(frame, text="Частота (Гц):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.freq_var = tk.DoubleVar(value=440.0)
        ttk.Scale(frame, from_=50, to=2000, variable=self.freq_var,
                  orient="horizontal", command=self._on_change).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Entry(frame, textvariable=self.freq_var, width=10).grid(row=0, column=2, padx=5)

        # Амплитуда
        ttk.Label(frame, text="Амплитуда:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amp_var = tk.DoubleVar(value=0.5)
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.amp_var,
                  orient="horizontal", command=self._on_change).grid(row=1, column=1, sticky="ew", padx=5)

        # Форма
        ttk.Label(frame, text="Форма:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.wave_var = tk.StringVar(value="sine")
        wave_combo = ttk.Combobox(frame, textvariable=self.wave_var,
                                  values=["sine", "square", "sawtooth", "triangle"],
                                  state="readonly")
        wave_combo.grid(row=2, column=1, sticky="w", padx=5)
        wave_combo.bind("<<ComboboxSelected>>", self._on_change)

        frame.columnconfigure(1, weight=1)

        # Кнопки
        btn_frame = ttk.Frame(self.tab_gen)
        btn_frame.pack(pady=10)

        self.btn_gen = ttk.Button(btn_frame, text="▶ Старт (Слушать)",
                                  command=self.toggle_generator)
        self.btn_gen.pack(side="left", padx=5)

        self.btn_rec = ttk.Button(btn_frame, text="🔴 Записать 3 сек",
                                  command=self.record_audio)
        self.btn_rec.pack(side="left", padx=5)

        self.gen_canvas = tk.Canvas(self.tab_gen, bg="black", height=150, highlightthickness=0)
        self.gen_canvas.pack(fill="x", padx=10, pady=10)

    def _build_radio(self):
        frame = ttk.Frame(self.tab_radio)
        frame.pack(pady=30)

        ttk.Label(frame, text="URL радиостанции:", font=("Segoe UI", 11)).pack()
        self.radio_url = ttk.Entry(frame, width=60)
        self.radio_url.insert(0, "http://stream.radioparadise.com/aac-320")
        self.radio_url.pack(pady=5)

        self.btn_radio = ttk.Button(frame, text="▶ Играть", command=self.toggle_radio)
        self.btn_radio.pack(pady=15)

        if not HAS_BASS:
            tk.Label(frame, text="⚠️ Для радио установите pybass3 и bass.dll", foreground="red").pack(pady=10)
        else:
            tk.Label(frame, text="✅ BASS загружен. Можно слушать.", foreground="green").pack(pady=10)

    def _build_vis(self):
        frame = ttk.Frame(self.tab_vis)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="ОСЦИЛЛОГРАММА (реальное время)", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.osc_canvas = tk.Canvas(frame, bg="black", height=200, highlightthickness=0)
        self.osc_canvas.pack(fill="x", pady=5)

        ttk.Label(frame, text="СПЕКТР (FFT)", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.spec_canvas = tk.Canvas(frame, bg="#0a0a1a", height=200, highlightthickness=0)
        self.spec_canvas.pack(fill="x", pady=5)

    # ================= АУДИО ГЕНЕРАЦИЯ (ЗВУК) =================
    def audio_callback(self, outdata, frames, time_info, status):
        if status:
            print(status)
        
        # Генерируем звук в зависимости от выбранной формы
        t = (np.arange(frames) + self.stream_time) / self.RATE
        freq = self.freq_var.get()
        amp = self.amp_var.get()
        shape = self.wave_var.get()

        if shape == "sine":
            signal = np.sin(2 * np.pi * freq * t)
        elif shape == "square":
            signal = np.sign(np.sin(2 * np.pi * freq * t))
        elif shape == "sawtooth":
            signal = 2 * (t * freq - np.floor(t * freq + 0.5))
        elif shape == "triangle":
            signal = 4 * np.abs(t * freq - np.floor(t * freq + 0.5)) - 1
        else:
            signal = np.zeros(frames)

        data = (signal * amp).astype(np.float32)
        
        # Для визуализации
        self.last_data = data.copy()
        
        # Если записываем — сохраняем
        if self.is_recording:
            self.recorded_frames.append(data.copy())

        outdata[:] = data.reshape(-1, 1)
        self.stream_time += frames / self.RATE

    def toggle_generator(self):
        if self.is_playing:
            self.is_playing = False
            self.stream.stop()
            self.stream.close()
            self.btn_gen.config(text="▶ Старт (Слушать)")
            self.status.config(text="Звук остановлен")
        else:
            self.is_playing = True
            self.stream_time = 0.0
            self.stream = sd.OutputStream(
                samplerate=self.RATE,
                blocksize=self.BLOCK_SIZE,
                channels=1,
                callback=self.audio_callback
            )
            self.stream.start()
            self.btn_gen.config(text="⏹ Стоп")
            self.status.config(text="Генератор играет...")

    # ================= ЗАПИСЬ =================
    def record_audio(self):
        if not self.is_playing:
            messagebox.showwarning("Внимание", "Сначала включите звук (Старт)!")
            return

        self.is_recording = True
        self.recorded_frames = []
        self.status.config(text="Запись 3 секунды...")
        self.btn_rec.config(state="disabled")

        def stop_record():
            time.sleep(3.0)
            self.is_recording = False
            self.root.after(0, self._save_wav)

        threading.Thread(target=stop_record, daemon=True).start()

    def _save_wav(self):
        self.btn_rec.config(state="normal")
        self.status.config(text="Запись завершена")
        
        if not self.recorded_frames:
            return

        # Склеиваем все фрагменты
        full_data = np.concatenate(self.recorded_frames)
        # Переводим в 16-битный формат
        full_data_int16 = (full_data * 32767).astype(np.int16)

        filename = "recorded.wav"
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.RATE)
            wf.writeframes(full_data_int16.tobytes())

        messagebox.showinfo("Готово", f"Файл '{filename}' сохранен.\n"
                                      f"Сэмплов: {len(full_data)}")

    # ================= РАДИО =================
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
    def _on_change(self, *args):
        pass

    def _animate(self):
        if self.is_playing:
            self.draw_visualizer()
        self.root.after(50, self._animate)

    def draw_visualizer(self):
        self._draw_oscilloscope(self.gen_canvas)
        self._draw_oscilloscope(self.osc_canvas)
        self._draw_spectrum(self.spec_canvas)

    def _draw_oscilloscope(self, canvas):
        canvas.delete("all")
        W = canvas.winfo_width()
        H = canvas.winfo_height()
        if W < 50 or H < 20:
            return

        # Сетка
        for i in range(0, W, 50):
            canvas.create_line(i, 0, i, H, fill="#222")
        for j in range(0, H, 50):
            canvas.create_line(0, j, W, j, fill="#222")
        canvas.create_line(0, H // 2, W, H // 2, fill="#444")

        if not self.is_playing:
            return

        data = self.last_data
        n = len(data)
        if n == 0:
            return

        points = []
        for i in range(0, n, 4):  # каждый 4-й сэмпл для скорости
            x = (i / n) * W
            y = H // 2 - data[i] * (H // 2 - 10)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(*points, fill="#00ff00", width=2)

    def _draw_spectrum(self, canvas):
        canvas.delete("all")
        W = canvas.winfo_width()
        H = canvas.winfo_height()
        if W < 50 or H < 20:
            return

        if not self.is_playing:
            return

        data = self.last_data
        n = len(data)
        if n < 2:
            return

        # FFT
        fft_result = np.abs(np.fft.rfft(data * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, 1 / self.RATE)

        # Ограничиваем отображение до 4000 Гц
        max_freq = 4000
        valid_idx = freqs <= max_freq
        fft_result = fft_result[valid_idx]
        freqs = freqs[valid_idx]

        if len(fft_result) == 0:
            return

        # Нормализация
        max_mag = np.max(fft_result)
        if max_mag > 0:
            fft_result = fft_result / max_mag

        # Рисуем спектр
        bar_w = W / len(fft_result)
        for k, mag in enumerate(fft_result):
            h = mag * (H - 20)
            x1 = k * bar_w
            y1 = H - h
            x2 = (k + 1) * bar_w
            y2 = H

            # Градиент
            if h > H * 0.8:
                color = "#ff3333"
            elif h > H * 0.5:
                color = "#ffaa00"
            else:
                color = "#00ff88"

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Подписи частот
        for f in [0, 500, 1000, 2000, 3000, 4000]:
            x = (f / max_freq) * W
            canvas.create_text(x, H - 5, text=f"{f}Hz", fill="#666", font=("Segoe UI", 7))

    def on_closing(self):
        if self.is_playing:
            self.stream.stop()
            self.stream.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioStudioApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
