from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any


DEFAULT_DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
VIDEO_QUALITIES = ("best", "1080", "720", "480", "360")
AUDIO_FORMATS = ("mp3", "m4a", "wav", "opus", "best")
BROWSERS = ("chrome", "edge", "firefox", "brave", "opera", "vivaldi")
JS_RUNTIMES = ("auto", "deno", "node", "quickjs", "bun", "none")
REMOTE_COMPONENTS = ("auto", "github", "npm", "none")


def import_yt_dlp():
    try:
        import yt_dlp
    except ImportError:
        print(
            "A biblioteca yt-dlp nao esta instalada.\n"
            "Instale com: pip install -r requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return yt_dlp


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def build_js_runtime_options(runtime: str) -> dict[str, Any]:
    if runtime == "none":
        return {"js_runtimes": []}

    if runtime != "auto":
        return {"js_runtimes": {runtime: {}}}

    if shutil.which("deno"):
        return {}

    for detected_runtime in ("node", "quickjs", "bun"):
        if shutil.which(detected_runtime):
            return {"js_runtimes": {detected_runtime: {}}}

    return {}


def build_remote_component_options(remote_components: str) -> dict[str, Any]:
    if remote_components == "none":
        return {"remote_components": set()}

    if remote_components == "npm":
        return {"remote_components": {"ejs:npm"}}

    if remote_components == "github":
        return {"remote_components": {"ejs:github"}}

    if shutil.which("deno"):
        return {"remote_components": {"ejs:npm"}}

    return {"remote_components": {"ejs:github"}}


def build_video_format(quality: str, ffmpeg_available: bool) -> str:
    if quality == "best":
        if ffmpeg_available:
            return "bv*+ba/best"
        return (
            "best[ext=mp4][vcodec!=none][acodec!=none]/"
            "best[vcodec!=none][acodec!=none]"
        )

    max_height = int(quality)
    if ffmpeg_available:
        return f"bv*[height<={max_height}]+ba/best[height<={max_height}]/best"
    return (
        f"best[height<={max_height}][ext=mp4][vcodec!=none][acodec!=none]/"
        f"best[height<={max_height}][vcodec!=none][acodec!=none]"
    )


def build_audio_options(audio_format: str, ffmpeg_available: bool) -> dict[str, Any]:
    options: dict[str, Any] = {"format": "bestaudio/best"}

    if audio_format == "best":
        return options

    if not ffmpeg_available:
        print(
            "Aviso: ffmpeg nao foi encontrado. Vou baixar o melhor audio disponivel "
            "sem converter o formato.",
            file=sys.stderr,
        )
        return options

    options["postprocessors"] = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": "192",
        }
    ]
    return options


def progress_hook(status: dict[str, Any]) -> None:
    if status.get("status") == "downloading":
        percent = status.get("_percent_str", "").strip()
        speed = status.get("_speed_str", "").strip()
        eta = status.get("_eta_str", "").strip()
        parts = [part for part in (percent, speed, f"ETA {eta}" if eta else "") if part]
        if parts:
            print("\rBaixando: " + " | ".join(parts), end="", flush=True)
    elif status.get("status") == "finished":
        print("\nDownload concluido. Finalizando arquivo...")


def print_progress(status: dict[str, Any]) -> None:
    progress_hook(status)


def download(
    url: str,
    media_type: str,
    output_dir: Path,
    quality: str,
    audio_format: str,
    playlist: bool,
    cookies_from_browser: str | None,
    cookies_file: Path | None,
    js_runtime: str,
    remote_components: str,
    progress_callback=None,
) -> None:
    yt_dlp = import_yt_dlp()
    ffmpeg_available = has_ffmpeg()
    output_dir.mkdir(parents=True, exist_ok=True)

    base_options: dict[str, Any] = {
        "outtmpl": str(output_dir / "%(title).180s [%(id)s].%(ext)s"),
        "ignoreerrors": False,
        "noplaylist": not playlist,
        "progress_hooks": [progress_callback or print_progress],
        "windowsfilenames": True,
    }
    base_options.update(build_js_runtime_options(js_runtime))
    base_options.update(build_remote_component_options(remote_components))

    if cookies_from_browser:
        base_options["cookiesfrombrowser"] = (cookies_from_browser, None, None, None)

    if cookies_file:
        base_options["cookiefile"] = str(cookies_file)

    if media_type == "video":
        if not ffmpeg_available:
            print(
                "Aviso: ffmpeg nao foi encontrado. Vou baixar apenas formatos de "
                "video que ja venham com audio. Para melhor qualidade com som, "
                "instale o FFmpeg.",
                file=sys.stderr,
            )
        base_options.update(
            {
                "format": build_video_format(quality, ffmpeg_available),
            }
        )
        if ffmpeg_available:
            base_options["merge_output_format"] = "mp4"
    else:
        base_options.update(build_audio_options(audio_format, ffmpeg_available))

    with yt_dlp.YoutubeDL(base_options) as downloader:
        downloader.download([url])


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def interactive_args() -> argparse.Namespace:
    print("YouTube Downloader")
    print("Use apenas com conteudo que voce tem permissao para baixar.\n")

    url = ask("Cole a URL do video ou playlist")
    while not url:
        url = ask("A URL e obrigatoria")

    media_type = ask("Baixar audio ou video?", "video").lower()
    while media_type not in {"audio", "video"}:
        media_type = ask("Digite audio ou video", "video").lower()

    quality = "best"
    audio_format = "mp3"

    if media_type == "video":
        quality = ask("Qualidade do video (best, 1080, 720, 480, 360)", "best").lower()
        while quality not in VIDEO_QUALITIES:
            quality = ask("Escolha: best, 1080, 720, 480 ou 360", "best").lower()
    else:
        audio_format = ask("Formato do audio (mp3, m4a, wav, opus, best)", "mp3").lower()
        while audio_format not in AUDIO_FORMATS:
            audio_format = ask("Escolha: mp3, m4a, wav, opus ou best", "mp3").lower()

    output = ask("Pasta de destino", str(DEFAULT_DOWNLOAD_DIR))
    playlist_answer = ask("Baixar playlist inteira? (s/n)", "n").lower()
    cookies_answer = ask(
        "Usar cookies do navegador para evitar bloqueio? (chrome, edge, firefox, n)",
        "n",
    ).lower()
    if cookies_answer in {"n", "nao", "no"}:
        cookies_answer = ""
    while cookies_answer and cookies_answer not in BROWSERS:
        cookies_answer = ask(
            "Escolha chrome, edge, firefox, brave, opera, vivaldi ou n",
            "n",
        ).lower()
        if cookies_answer in {"n", "nao", "no"}:
            cookies_answer = ""

    js_runtime = ask("Runtime JavaScript (auto, deno, node, quickjs, bun, none)", "auto").lower()
    while js_runtime not in JS_RUNTIMES:
        js_runtime = ask("Escolha auto, deno, node, quickjs, bun ou none", "auto").lower()
    remote_components = ask(
        "Baixar scripts EJS quando necessario? (auto, github, npm, none)",
        "auto",
    ).lower()
    while remote_components not in REMOTE_COMPONENTS:
        remote_components = ask("Escolha auto, github, npm ou none", "auto").lower()

    return argparse.Namespace(
        url=url,
        type=media_type,
        output=Path(output),
        quality=quality,
        audio_format=audio_format,
        playlist=playlist_answer in {"s", "sim", "y", "yes"},
        cookies_from_browser=cookies_answer or None,
        cookies_file=None,
        js_runtime=js_runtime,
        remote_components=remote_components,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa videos ou audios do YouTube com yt-dlp."
    )
    parser.add_argument("url", nargs="?", help="URL do video ou playlist.")
    parser.add_argument(
        "-t",
        "--type",
        choices=("video", "audio"),
        default="video",
        help="Tipo de download. Padrao: video.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DOWNLOAD_DIR,
        help="Pasta onde os arquivos serao salvos.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=VIDEO_QUALITIES,
        default="best",
        help="Qualidade maxima do video. Padrao: best.",
    )
    parser.add_argument(
        "-f",
        "--audio-format",
        choices=AUDIO_FORMATS,
        default="mp3",
        help="Formato do audio. Padrao: mp3.",
    )
    parser.add_argument(
        "--playlist",
        action="store_true",
        help="Baixa a playlist inteira quando a URL for de playlist.",
    )
    parser.add_argument(
        "--cookies-from-browser",
        choices=BROWSERS,
        help="Usa cookies de um navegador onde voce ja esta logado no YouTube.",
    )
    parser.add_argument(
        "--cookies",
        dest="cookies_file",
        type=Path,
        help="Usa um arquivo cookies.txt no formato Netscape/Mozilla.",
    )
    parser.add_argument(
        "--js-runtime",
        choices=JS_RUNTIMES,
        default="auto",
        help="Runtime JavaScript para o yt-dlp. Padrao: auto.",
    )
    parser.add_argument(
        "--remote-components",
        choices=REMOTE_COMPONENTS,
        default="auto",
        help="Fonte dos scripts EJS para desafios do YouTube. Padrao: auto.",
    )

    args = parser.parse_args()
    if not args.url:
        return interactive_args()
    return args


def main() -> int:
    args = parse_args()
    try:
        download(
            url=args.url,
            media_type=args.type,
            output_dir=args.output,
            quality=args.quality,
            audio_format=args.audio_format,
            playlist=args.playlist,
            cookies_from_browser=args.cookies_from_browser,
            cookies_file=args.cookies_file,
            js_runtime=args.js_runtime,
            remote_components=args.remote_components,
        )
    except KeyboardInterrupt:
        print("\nDownload cancelado pelo usuario.")
        return 130
    except Exception as exc:
        print(f"\nNao consegui concluir o download: {exc}", file=sys.stderr)
        return 1

    print(f"Arquivo salvo em: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
