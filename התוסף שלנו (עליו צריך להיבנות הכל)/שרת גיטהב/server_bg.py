"""
YoniTube Background Server v3
• תמיד פועל — ללא בדיקת Chrome (הבדיקה הקודמת גרמה לחלון שחור)
• מפעיל את Flask על port 5000
• מונע הרצה כפולה עם socket lock
• מאתחל אוטומטית אם נפל
"""
import sys, os, time, threading, importlib.util, socket, logging

# ── Suppress console (no black window) ───────────────────────────
if getattr(sys, 'frozen', False):
    try:
        _dev = open(os.devnull, 'w')
        sys.stdout = _dev
        sys.stderr = _dev
    except Exception:
        pass

# ── Paths ─────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BUNDLE_DIR = sys._MEIPASS
    _EXE_DIR    = os.path.dirname(sys.executable)
else:
    _BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    _EXE_DIR    = _BUNDLE_DIR

# ── Logging ───────────────────────────────────────────────────────
LOG_FILE = os.path.join(_EXE_DIR, 'yonitube_bg.log')
logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format='%(asctime)s %(message)s', encoding='utf-8',
)
log = logging.getLogger('yn_bg')

# ── Single-instance lock (no subprocess needed) ──────────────────
_lock_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    _lock_sock.bind(('127.0.0.1', 47321))
except OSError:
    log.info('Already running — exit')
    sys.exit(0)

log.info(f'YoniTube BG v3 | bundle={_BUNDLE_DIR} | exe={_EXE_DIR}')

def _run_flask():
    """Load server.py and run Flask. Retries forever on crash."""
    while True:
        try:
            sp   = os.path.join(_BUNDLE_DIR, 'server.py')
            if not os.path.exists(sp):
                sp = os.path.join(_EXE_DIR, 'server.py')
            spec = importlib.util.spec_from_file_location('_yn_server', sp)
            if spec is None or spec.loader is None:
                raise RuntimeError(f'Unable to load server module from {sp}')
            mod  = importlib.util.module_from_spec(spec)
            sys.modules['_yn_server'] = mod
            spec.loader.exec_module(mod)
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            log.info('Flask starting on port 5000')
            mod.app.run(host='127.0.0.1', port=5000,
                        debug=False, threaded=True, use_reloader=False)
        except SystemExit:
            pass
        except Exception as e:
            log.error(f'Flask error: {e}')
        log.info('Flask stopped — restarting in 5s')
        time.sleep(5)

if __name__ == '__main__':
    t = threading.Thread(target=_run_flask, daemon=True)
    t.start()
    # Keep process alive
    while True:
        time.sleep(60)
