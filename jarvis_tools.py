# JARVIS PC — TË GJITHA komandat direkte (një vend).
# Këto vegla i thërret drejtpërdrejt agjenti Gemini Realtime,
# pa LangChain në mes (më shpejt, më i besueshëm).
import asyncio
import subprocess
import urllib.parse
from datetime import datetime

from livekit.agents import function_tool


# ── Programet ──────────────────────────────────────────────

_APP_MAP = {
    "notepad": "notepad", "calculator": "calc", "chrome": "chrome",
    "edge": "msedge", "firefox": "firefox", "vlc": "vlc",
    "paint": "mspaint", "settings": "start ms-settings:",
    "control panel": "control", "task manager": "taskmgr",
    "command prompt": "cmd", "spotify": "spotify",
    "telegram": "telegram", "whatsapp": "whatsapp", "vs code": "code",
}


@function_tool(
    name="hap_programin",
    description=(
        "Hap një program në kompjuter. Përdore kur përdoruesi thotë 'hap ...'. "
        "Emrat: notepad, calculator, chrome, edge, firefox, vlc, paint, "
        "settings, control panel, task manager, command prompt, spotify, "
        "telegram, whatsapp, vs code."
    ),
)
async def hap_programin(emri: str) -> str:
    """Hap një program desktop në Windows."""
    cmd = _APP_MAP.get(emri.lower().strip(), emri.strip())

    def _launch():
        subprocess.Popen(f'start "" "{cmd}"', shell=True)

    try:
        await asyncio.to_thread(_launch)
        return f"U hap programi: {emri}."
    except Exception as e:
        return f"S'u hap dot {emri}: {e}"


@function_tool(
    name="mbyll_programin",
    description=(
        "Mbyll një program në kompjuter. Përdore kur përdoruesi thotë "
        "'mbyll ...' (p.sh. 'mbyll notepad', 'mbyll chrome')."
    ),
)
async def mbyll_programin(emri: str) -> str:
    """Mbyll një program me taskkill."""
    _kill = {
        "notepad": "notepad.exe", "calculator": "Calculator.exe",
        "chrome": "chrome.exe", "edge": "msedge.exe",
        "firefox": "firefox.exe", "vlc": "vlc.exe", "paint": "mspaint.exe",
        "spotify": "spotify.exe", "telegram": "telegram.exe",
        "whatsapp": "whatsapp.exe",
    }
    exe = _kill.get(emri.lower().strip(), emri.strip())

    def _kill_proc():
        subprocess.run(f'taskkill /IM "{exe}" /F',
                       shell=True, capture_output=True)

    try:
        await asyncio.to_thread(_kill_proc)
        return f"U mbyll programi: {emri}."
    except Exception as e:
        return f"S'u mbyll dot {emri}: {e}"


# ── Tastiera ───────────────────────────────────────────────

@function_tool(
    name="shkruaj_tekst",
    description=(
        "Shkruan tekst me tastierë në dritaren aktive (mbështet ë, ç). "
        "Përdore kur përdoruesi thotë 'shkruaj ...'. "
        "Sigurohu që dritarja ku do shkruhet është e hapur."
    ),
)
async def shkruaj_tekst(teksti: str) -> str:
    """Shkruan tekst me tastierë."""
    try:
        from pynput.keyboard import Controller
        kb = Controller()
        await asyncio.to_thread(kb.type, teksti)
        return f"U shkrua: {teksti}"
    except Exception as e:
        return f"Shkrimi dështoi: {e}"


@function_tool(
    name="shtyp_tastin",
    description=(
        "Shtyp një tast special: enter, escape, tab, backspace, delete, "
        "space, up, down, left, right. Përdore kur duhet konfirmim "
        "ose navigim (p.sh. pas shkrimit, shtyp enter)."
    ),
)
async def shtyp_tastin(tasti: str) -> str:
    """Shtyp një tast special."""
    try:
        from pynput.keyboard import Key, Controller
        kb = Controller()
        _keys = {
            "enter": Key.enter, "escape": Key.esc, "tab": Key.tab,
            "backspace": Key.backspace, "delete": Key.delete,
            "space": Key.space, "up": Key.up, "down": Key.down,
            "left": Key.left, "right": Key.right,
        }
        k = _keys.get(tasti.lower().strip())
        if not k:
            return f"Tasti '{tasti}' s'njihet."
        await asyncio.to_thread(kb.press, k)
        await asyncio.to_thread(kb.release, k)
        return f"U shtyp tasti: {tasti}."
    except Exception as e:
        return f"Shtypja dështoi: {e}"


# ── Web ────────────────────────────────────────────────────

@function_tool(
    name="kerko_ne_google",
    description=(
        "Kërkon në Google dhe hap shfletuesin me rezultatet. "
        "Përdore kur përdoruesi thotë 'kërko në google për ...'."
    ),
)
async def kerko_ne_google(kerkimi: str) -> str:
    """Hap Google me rezultatet e kërkimit."""
    try:
        url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(kerkimi)

        def _launch():
            subprocess.Popen(f'start "" "{url}"', shell=True)

        await asyncio.to_thread(_launch)
        return f"Po kërkoj në Google për: {kerkimi}."
    except Exception as e:
        return f"Kërkimi dështoi: {e}"


# ── Moti & Ora ─────────────────────────────────────────────

@function_tool(
    name="moti",
    description=(
        "Tregon motin aktual për një qytet (temperatura, gjendja, lagështia, era). "
        "Përdore kur përdoruesi pyet për motin. Nëse s'thotë qytet, përdor Tiranën."
    ),
)
async def moti(qyteti: str = "Tirana") -> str:
    """Merr motin aktual nga OpenWeather."""
    try:
        from jarvis_get_whether import get_weather
        # get_weather është LangChain @tool — e thërrasim direkt
        result = await get_weather.ainvoke({"city": qyteti} if qyteti else {})
        return str(result)
    except Exception as e:
        return f"Moti s'u mor dot: {e}"


@function_tool(
    name="ora_data",
    description="Tregon orën dhe datën aktuale.",
)
async def ora_data() -> str:
    """Kthen orën dhe datën."""
    tani = datetime.now()
    ditet = ["e hënë", "e martë", "e mërkurë", "e enjte",
             "e premte", "e shtunë", "e diel"]
    return (f"Ora është {tani.strftime('%H:%M')}, "
            f"{ditet[tani.weekday()]} {tani.strftime('%d.%m.%Y')}.")


# ── Volumi ─────────────────────────────────────────────────

@function_tool(
    name="volumi",
    description=(
        "Kontrollon volumin e sistemit: 'ngre' (më lart), 'ul' (më ulët), "
        "'hesht' (mute/unmute). Përdore kur përdoruesi thotë "
        "'ngre volumin', 'ul zërin', 'hesht'."
    ),
)
async def volumi(veprimi: str) -> str:
    """Ndryshon volumin e sistemit."""
    try:
        from pynput.keyboard import Key, Controller
        kb = Controller()
        v = veprimi.lower().strip()
        if v in ("ngre", "rrit", "lart"):
            key, n = Key.media_volume_up, 5
        elif v in ("ul", "zbrit", "poshtë", "poshte"):
            key, n = Key.media_volume_down, 5
        elif v in ("hesht", "mute", "qetëso"):
            key, n = Key.media_volume_mute, 1
        else:
            return f"Veprimi '{veprimi}' s'njihet (ngre/ul/hesht)."

        def _do():
            for _ in range(n):
                kb.press(key)
                kb.release(key)

        await asyncio.to_thread(_do)
        return f"Volumi: {veprimi}."
    except Exception as e:
        return f"Kontrolli i volumit dështoi: {e}"


# ── Regjistrimi i ekranit ──────────────────────────────────

@function_tool(
    name="regjistro_ekranin",
    description=(
        "Regjistron video të ekranit (mp4 në Desktop). Përdore kur përdoruesi "
        "thotë 'bëj video record' ose 'regjistro ekranin'. "
        "Mund të japësh sekonda (p.sh. 30); default 10."
    ),
)
async def regjistro_ekranin(sekonda: int = 10) -> str:
    """Regjistron ekranin me ffmpeg (gdigrab)."""
    try:
        import os
        from datetime import datetime as _dt
        sekonda = max(3, min(int(sekonda), 300))
        out = os.path.join(
            os.path.expanduser("~"), "Desktop",
            f"jarvis-record-{_dt.now().strftime('%Y%m%d-%H%M%S')}.mp4")

        def _rec():
            subprocess.run(
                f'ffmpeg -y -f gdigrab -framerate 15 -i desktop '
                f'-t {sekonda} -pix_fmt yuv420p "{out}"',
                shell=True, capture_output=True, timeout=sekonda + 20)

        await asyncio.to_thread(_rec)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return f"Video u regjistrua: {out} ({sekonda} sekonda)."
        return ("Regjistrimi dështoi — duhet ffmpeg i instaluar. "
                "Shkarko nga ffmpeg.org dhe shtoje në PATH.")
    except Exception as e:
        return f"Regjistrimi dështoi: {e}"


# Lista e plotë — importohet në agent.py
ALL_TOOLS = [
    hap_programin,
    mbyll_programin,
    shkruaj_tekst,
    shtyp_tastin,
    kerko_ne_google,
    moti,
    ora_data,
    volumi,
    regjistro_ekranin,
]
