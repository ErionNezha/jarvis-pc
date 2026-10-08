<!-- Created by Erion Nezha — © 2026 All rights reserved -->
# JARVIS PC — Asistenti Personal me Zë 🎙️

Asistent zëri në **shqip** për Windows PC. Flet, dëgjon, hap programe, shkruan tekst, tregon motin/orën, kërkon në Google — të gjitha me komandë zanore.

**Krijuar nga Mr.Erionxx**

## ✨ Funksionet

| Komanda zanore | Çfarë bën |
|---|---|
| *"hap notepad"* | Hap Notepad (ose chrome, calculator, vlc...) |
| *"mbyll chrome"* | Mbyll programin |
| *"shkruaj: përshëndetje me ë dhe ç"* | Shkruan tekst (mbështet ë, ç) |
| *"kërko në google për motin"* | Hap browser-in me rezultatet |
| *"si është moti?"* | Moti aktual (OpenWeather) |
| *"sa është ora?"* | Ora dhe data |
| *"ngre volumin" / "hesht"* | Kontrollon zërin e sistemit |
| *"bëj video record"* | Regjistron ekranin (mp4) |

## 🛠️ Teknologjitë

- **Python 3.12** — logjika kryesore
- **LiveKit** — transmetimi realtime i zërit (WebRTC)
- **Google Gemini 2.5** — modeli realtime `gemini-2.5-flash-native-audio` (zëri Charon)
- **LangChain** — agjent ReAct për arsyetim kompleks
- **pynput** — kontrolli i tastierës/miusit

## 🚀 Instalimi

1. Instalo **Python 3.12** (jo 3.14!)
2. Kopjo `.env.example` si `.env` dhe mbush çelësat:
   - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` — [livekit.io](https://livekit.io) (falas)
   - `GOOGLE_API_KEY` — [Google AI Studio](https://aistudio.google.com) (falas)
   - `OPENWEATHER_API_KEY` — [openweathermap.org](https://openweathermap.org) (falas)
3. Ekzekuto **`start_jarvis.bat`** — bën gjithçka vetë!

Ose manualisht:
```cmd
cd jarvis-pc
.venv\Scripts\activate
python token_server.py    :: dritarja 1
python agent.py dev       :: dritarja 2
:: hap http://localhost:8765/ → kliko FOL
```

## 🏗️ Arkitektura

```
┌─────────┐   zë   ┌─────────┐   WebRTC   ┌──────────┐   audio   ┌────────┐
│ Mikrofon├────────►│ Browser ├────────────►│ LiveKit  ├──────────►│ Worker │
└─────────┘        └─────────┘   (cloud)    └──────────┘           └───┬────┘
                                                                      │
                                                              ┌───────▼────────┐
                                                              │ Gemini 2.5     │
                                                              │ Realtime       │
                                                              └───────┬────────┘
                                                                      │ veglat
                                                              ┌───────▼────────┐
                                                              │ jarvis_tools.py│
                                                              │ (8 komanda)    │
                                                              └────────────────┘
```

- **Çdo lidhje = dhomë unike** (`jarvis-room-<timestamp>-<rand>`) — kurrë dublikatë
- **Veglat direkte** (`@function_tool`) — pa ndërmjetës, përgjigje e shpejtë
- **Zëri Charon** — i thellë, natyral në shqip

## 📁 Struktura

```
jarvis-pc/
├── agent.py              # Workeri LiveKit + Gemini
├── token_server.py       # Serveri i tokenave + klienti web
├── jarvis_tools.py       # TË GJITHA komandat (8 vegla direkte)
├── jarvis_reasoning.py   # LangChain ReAct (arsyetim kompleks)
├── client/index.html     # Ndërfaqja e zërit
├── start_jarvis.bat      # Nisje me 1 klik
└── requirements.txt
```

## 📝 Licenca

© 2026 Mr.Erionxx — Të gjitha të drejtat e rezervuara.
