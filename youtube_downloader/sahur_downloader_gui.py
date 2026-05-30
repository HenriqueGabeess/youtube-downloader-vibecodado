from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from youtube_downloader import (
    AUDIO_FORMATS,
    BROWSERS,
    DEFAULT_DOWNLOAD_DIR,
    JS_RUNTIMES,
    REMOTE_COMPONENTS,
    VIDEO_QUALITIES,
    download,
)


class SahurDownloaderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sahur Downloader")
        self.geometry("760x620")
        self.minsize(680, 560)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.download_thread: threading.Thread | None = None

        self.url_var = tk.StringVar()
        self.type_var = tk.StringVar(value="video")
        self.quality_var = tk.StringVar(value="best")
        self.audio_format_var = tk.StringVar(value="mp3")
        self.output_var = tk.StringVar(value=str(DEFAULT_DOWNLOAD_DIR))
        self.playlist_var = tk.BooleanVar(value=False)
        self.cookies_browser_var = tk.StringVar(value="chrome")
        self.use_browser_cookies_var = tk.BooleanVar(value=True)
        self.cookies_file_var = tk.StringVar()
        self.js_runtime_var = tk.StringVar(value="auto")
        self.remote_components_var = tk.StringVar(value="auto")
        self.status_var = tk.StringVar(value="Pronto para baixar.")
        self.progress_var = tk.DoubleVar(value=0)

        self.configure(bg="#f5f7fb")
        self._build_ui()
        self.after(120, self._process_events)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fb")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("Title.TLabel", background="#16213e", foreground="#ffffff", font=("Segoe UI", 28, "bold"))
        style.configure("Subtitle.TLabel", background="#16213e", foreground="#dbe7ff", font=("Segoe UI", 10))
        style.configure("TLabel", background="#ffffff", foreground="#182033", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TRadiobutton", background="#ffffff", foreground="#182033", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#ffffff", foreground="#182033", font=("Segoe UI", 10))
        style.configure("Horizontal.TProgressbar", troughcolor="#e8edf7", background="#2f80ed")

        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x")
        header_inner = tk.Frame(header, bg="#16213e", padx=24, pady=22)
        header_inner.pack(fill="x")
        ttk.Label(header_inner, text="Sahur Downloader", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_inner,
            text="Baixe videos ou audios com cookies, FFmpeg e EJS quando precisar.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
        panel.pack(fill="both", expand=True, padx=18, pady=18)
        panel.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(panel, text="URL do YouTube").grid(row=row, column=0, sticky="w", pady=(0, 6))
        url_entry = ttk.Entry(panel, textvariable=self.url_var)
        url_entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(0, 6))
        url_entry.focus()

        row += 1
        ttk.Label(panel, text="Tipo").grid(row=row, column=0, sticky="w", pady=6)
        type_frame = ttk.Frame(panel, style="Panel.TFrame")
        type_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=6)
        ttk.Radiobutton(type_frame, text="Video", variable=self.type_var, value="video", command=self._refresh_type_controls).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(type_frame, text="Audio", variable=self.type_var, value="audio", command=self._refresh_type_controls).pack(side="left")

        row += 1
        ttk.Label(panel, text="Qualidade do video").grid(row=row, column=0, sticky="w", pady=6)
        self.quality_combo = ttk.Combobox(panel, textvariable=self.quality_var, values=VIDEO_QUALITIES, state="readonly")
        self.quality_combo.grid(row=row, column=1, sticky="ew", pady=6)

        row += 1
        ttk.Label(panel, text="Formato do audio").grid(row=row, column=0, sticky="w", pady=6)
        self.audio_combo = ttk.Combobox(panel, textvariable=self.audio_format_var, values=AUDIO_FORMATS, state="readonly")
        self.audio_combo.grid(row=row, column=1, sticky="ew", pady=6)

        row += 1
        ttk.Label(panel, text="Pasta de destino").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(panel, textvariable=self.output_var).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(panel, text="Escolher", command=self._choose_output).grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=6)

        row += 1
        ttk.Checkbutton(panel, text="Baixar playlist inteira", variable=self.playlist_var).grid(row=row, column=1, sticky="w", pady=6)

        row += 1
        ttk.Checkbutton(
            panel,
            text="Usar cookies do navegador",
            variable=self.use_browser_cookies_var,
            command=self._refresh_cookie_controls,
        ).grid(row=row, column=1, sticky="w", pady=6)
        self.browser_combo = ttk.Combobox(panel, textvariable=self.cookies_browser_var, values=BROWSERS, state="readonly")
        self.browser_combo.grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=6)

        row += 1
        ttk.Label(panel, text="cookies.txt opcional").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(panel, textvariable=self.cookies_file_var).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(panel, text="Arquivo", command=self._choose_cookies_file).grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=6)

        row += 1
        ttk.Label(panel, text="JavaScript").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Combobox(panel, textvariable=self.js_runtime_var, values=JS_RUNTIMES, state="readonly").grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Combobox(panel, textvariable=self.remote_components_var, values=REMOTE_COMPONENTS, state="readonly").grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=6)

        row += 1
        ttk.Separator(panel).grid(row=row, column=0, columnspan=3, sticky="ew", pady=16)

        row += 1
        self.progress = ttk.Progressbar(panel, variable=self.progress_var, maximum=100)
        self.progress.grid(row=row, column=0, columnspan=3, sticky="ew")

        row += 1
        ttk.Label(panel, textvariable=self.status_var).grid(row=row, column=0, columnspan=3, sticky="w", pady=(8, 14))

        row += 1
        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.grid(row=row, column=0, columnspan=3, sticky="ew")
        actions.columnconfigure(0, weight=1)
        self.download_button = ttk.Button(actions, text="Baixar", style="Accent.TButton", command=self._start_download)
        self.download_button.grid(row=0, column=0, sticky="ew")

        row += 1
        note = (
            "Dica: para videos em alta qualidade com som, instale FFmpeg. "
            "Se o YouTube pedir verificacao, mantenha os cookies do navegador ativados."
        )
        ttk.Label(panel, text=note, wraplength=660).grid(row=row, column=0, columnspan=3, sticky="w", pady=(16, 0))

        self._refresh_type_controls()
        self._refresh_cookie_controls()

    def _refresh_type_controls(self) -> None:
        if self.type_var.get() == "video":
            self.quality_combo.configure(state="readonly")
            self.audio_combo.configure(state="disabled")
        else:
            self.quality_combo.configure(state="disabled")
            self.audio_combo.configure(state="readonly")

    def _refresh_cookie_controls(self) -> None:
        self.browser_combo.configure(state="readonly" if self.use_browser_cookies_var.get() else "disabled")

    def _choose_output(self) -> None:
        folder = filedialog.askdirectory(initialdir=self.output_var.get() or str(DEFAULT_DOWNLOAD_DIR))
        if folder:
            self.output_var.set(folder)

    def _choose_cookies_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Escolha o arquivo cookies.txt",
            filetypes=(("Cookies", "*.txt"), ("Todos os arquivos", "*.*")),
        )
        if filename:
            self.cookies_file_var.set(filename)

    def _start_download(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL obrigatoria", "Cole a URL do video ou playlist.")
            return

        self.download_button.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Preparando download...")

        self.download_thread = threading.Thread(target=self._run_download, args=(url,), daemon=True)
        self.download_thread.start()

    def _run_download(self, url: str) -> None:
        try:
            cookies_file = self.cookies_file_var.get().strip()
            download(
                url=url,
                media_type=self.type_var.get(),
                output_dir=Path(self.output_var.get().strip() or DEFAULT_DOWNLOAD_DIR),
                quality=self.quality_var.get(),
                audio_format=self.audio_format_var.get(),
                playlist=self.playlist_var.get(),
                cookies_from_browser=self.cookies_browser_var.get() if self.use_browser_cookies_var.get() else None,
                cookies_file=Path(cookies_file) if cookies_file else None,
                js_runtime=self.js_runtime_var.get(),
                remote_components=self.remote_components_var.get(),
                progress_callback=self._download_progress,
            )
        except Exception as exc:
            self.events.put(("error", str(exc)))
        else:
            self.events.put(("done", None))

    def _download_progress(self, status: dict[str, object]) -> None:
        if status.get("status") == "downloading":
            percent_text = str(status.get("_percent_str", "")).strip().replace("%", "")
            try:
                percent = float(percent_text)
            except ValueError:
                percent = self.progress_var.get()
            speed = str(status.get("_speed_str", "")).strip()
            eta = str(status.get("_eta_str", "")).strip()
            text = "Baixando"
            if speed:
                text += f" | {speed}"
            if eta:
                text += f" | ETA {eta}"
            self.events.put(("progress", (percent, text)))
        elif status.get("status") == "finished":
            self.events.put(("progress", (100.0, "Download concluido. Finalizando arquivo...")))

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    percent, text = payload
                    self.progress_var.set(float(percent))
                    self.status_var.set(str(text))
                elif event == "done":
                    self.progress_var.set(100)
                    self.status_var.set("Pronto. Arquivo salvo na pasta escolhida.")
                    self.download_button.configure(state="normal")
                    messagebox.showinfo("Concluido", "Download concluido.")
                elif event == "error":
                    self.status_var.set("Nao consegui concluir o download.")
                    self.download_button.configure(state="normal")
                    messagebox.showerror("Erro no download", str(payload))
        except queue.Empty:
            pass
        self.after(120, self._process_events)


if __name__ == "__main__":
    app = SahurDownloaderApp()
    app.mainloop()
