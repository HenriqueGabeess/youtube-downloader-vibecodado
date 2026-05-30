# YouTube Downloader em Python

Este projeto baixa videos ou audios do YouTube usando Python e `yt-dlp`.

Use somente para conteudos que voce tem direito de baixar, como seus proprios videos, conteudos com permissao do autor ou materiais liberados para download.

## Como instalar

Abra um terminal nesta pasta e rode:

```powershell
python -m pip install -r requirements.txt
```

Se `python` nao funcionar, tente:

```powershell
py -m pip install -r requirements.txt
```

No Windows, voce tambem pode dar duplo clique em `instalar.bat`.

Para converter audio para MP3/WAV/Opus ou juntar video em alta qualidade, tambem instale o FFmpeg:

```powershell
winget install Gyan.FFmpeg
```

Depois feche e abra o terminal novamente.

Importante: muitos videos do YouTube em 720p, 1080p ou maior vêm com video e audio separados. O FFmpeg e o programa que junta essas partes. Sem FFmpeg, o downloader tenta baixar apenas formatos que ja venham com som, mas a qualidade disponivel pode ser menor.

## Como usar no modo facil

Use a interface grafica:

```powershell
python sahur_downloader_gui.py
```

No Windows, voce tambem pode dar duplo clique em `abrir_interface.bat` ou `abrir_downloader.bat`.

Na janela, o nome **Sahur Downloader** aparece em destaque no topo.

Se preferir usar o modo terminal, rode:

```powershell
python youtube_downloader.py
```

O programa vai perguntar:

- a URL;
- se voce quer audio ou video;
- a qualidade ou formato;
- a pasta onde salvar.

## Exemplos rapidos

Baixar video na melhor qualidade:

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

Baixar video em ate 720p:

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --type video --quality 720
```

Baixar audio em MP3:

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --type audio --audio-format mp3
```

Baixar usando cookies do navegador, util quando aparece erro 429 ou "Sign in to confirm you're not a bot":

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --cookies-from-browser chrome
```

Se voce usa Microsoft Edge:

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --cookies-from-browser edge
```

Se voce usa Firefox:

```powershell
python youtube_downloader.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --cookies-from-browser firefox
```

Baixar playlist inteira:

```powershell
python youtube_downloader.py "URL_DA_PLAYLIST" --playlist
```

Escolher pasta de destino:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --output "C:\Users\SeuUsuario\Downloads"
```

## Corrigindo erro 429 ou pedido de login

Esse erro normalmente quer dizer que o YouTube desconfiou de automacao ou recebeu muitas requisicoes do mesmo IP. Nao e um erro do arquivo baixado; e uma barreira do proprio YouTube.

Tente nesta ordem:

1. Atualize o `yt-dlp`:

```powershell
python -m pip install -U "yt-dlp[default]"
```

Ou de duplo clique em `instalar.bat`, que agora tambem atualiza as dependencias.

2. Entre no YouTube pelo seu navegador normal.

3. Rode o downloader usando os cookies desse navegador:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --cookies-from-browser chrome
```

4. Se aparecer aviso sobre JavaScript runtime, instale Deno ou Node.js:

```powershell
winget install DenoLand.Deno
```

ou:

```powershell
winget install OpenJS.NodeJS.LTS
```

Depois feche e abra o terminal novamente.

5. Se voce instalou Node e ainda aparecer aviso de runtime, force o uso dele:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --cookies-from-browser chrome --js-runtime node
```

Se voce continuar recebendo 429, espere um tempo antes de tentar de novo. Muitas tentativas seguidas podem fazer o YouTube manter o bloqueio por mais tempo.

## Corrigindo "Signature solving failed" ou "Only images are available"

Esse erro quer dizer que o `yt-dlp` nao conseguiu resolver o desafio JavaScript do YouTube. Quando isso acontece, o YouTube mostra apenas formatos de imagem/thumbnail, e o video/audio nao aparece como formato baixavel.

Tente nesta ordem:

1. Atualize as dependencias:

```powershell
python -m pip install -U "yt-dlp[default]"
```

2. Instale o Deno, que e o runtime recomendado pelo guia EJS do `yt-dlp`:

```powershell
winget install DenoLand.Deno
```

3. Feche e abra o terminal.

4. Tente novamente com cookies e EJS automatico:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --cookies-from-browser chrome --js-runtime deno --remote-components npm
```

Se voce nao quiser usar Deno, instale Node.js e rode:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --cookies-from-browser chrome --js-runtime node --remote-components github
```

O downloader agora usa `--remote-components auto` por padrao. Com Deno instalado, ele tenta `ejs:npm`; sem Deno, tenta `ejs:github`.

## Corrigindo video sem som

Instale o FFmpeg e depois feche e abra o terminal:

```powershell
winget install Gyan.FFmpeg
```

Depois tente de novo:

```powershell
python youtube_downloader.py "URL_DO_VIDEO" --type video --quality best --cookies-from-browser chrome
```

Se voce nao instalar FFmpeg, o downloader agora evita formatos de video sem audio. Isso resolve o arquivo mudo, mas pode limitar a qualidade maxima disponivel.

## O que eu fiz

- Criei um programa Python com modo interativo e modo por comandos.
- Usei `yt-dlp`, uma ferramenta bem mantida para downloads de audio/video.
- Adicionei suporte para video, audio, qualidade maxima, playlists e pasta de destino.
- Adicionei suporte para cookies do navegador e arquivo `cookies.txt`.
- Adicionei suporte para runtime JavaScript, como Deno ou Node.
- Adicionei suporte para componentes EJS remotos, usados para resolver desafios JavaScript do YouTube.
- Coloquei tratamento de erro para biblioteca ausente, cancelamento e falhas de download.
- Fiz o app detectar FFmpeg: se ele existir, converte audio e junta video em alta qualidade; se nao existir, baixa no melhor formato disponivel sem conversao.
