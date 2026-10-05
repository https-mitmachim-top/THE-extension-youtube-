"""
YoniTube GUI v6 — by. The_Yonatan
• שרת Flask מובנה (port 5001, נפרד מ-server_bg על 5000)
• ממשק כהה יפה עם Tkinter — כל צבע 6-ספרות בלבד
• בחירת תיקיית יעד, תצוגת התקדמות חיה
"""
import tkinter as tk
from tkinter import ttk, filedialog
import threading, os, sys, time, re, json, subprocess, importlib.util

# ── Paths ─────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BD = sys._MEIPASS
    _ED = os.path.dirname(sys.executable)
else:
    _BD = os.path.dirname(os.path.abspath(__file__))
    _ED = _BD

ICON_PATH = os.path.join(_BD, 'icon.ico')
SRV_PORT  = 5001
SRV_URL   = f'http://127.0.0.1:{SRV_PORT}'
ANSI      = re.compile(r'\x1b\[[0-9;]*m')

# ── Color palette — 6-digit hex only, NO alpha ────────────────────
C = {
    'bg':     '#0d0d10',
    'bg2':    '#13131e',
    'bg3':    '#1a1a2e',
    'bg4':    '#1e2a4a',
    'fg':     '#e8e8f0',
    'fg2':    '#8888a0',
    'acc':    '#2563eb',
    'acc2':   '#3b82f6',
    'green':  '#22c55e',
    'red':    '#ef4444',
    'yellow': '#facc15',
    'amber':  '#f59e0b',
    'grey':   '#555577',
    'bdr':    '#252535',
    'white':  '#ffffff',
    'lgreen': '#86efac',
    'lblue':  '#93c5fd',
    'pink':   '#fca5a5',
    'dkred':  '#2a0f0f',
    'dkgrn':  '#0f2a1a',
}

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('YoniTube')
        self.root.geometry('980x700')
        self.root.minsize(800, 520)
        self.root.configure(bg=C['bg'])
        self.root.protocol('WM_DELETE_WINDOW', self._quit)
        try:
            if os.path.exists(ICON_PATH):
                self.root.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.running     = True
        self.q_frames    = {}
        self.q_data      = {}
        self.log_lines   = []

        self._style()
        self._build_ui()
        self._start_server()
        self._poll()

    # ── ttk styling ───────────────────────────────────────────────
    def _style(self):
        st = ttk.Style(self.root)
        st.theme_use('default')
        st.configure('YN.TNotebook', background=C['bg'], borderwidth=0)
        st.configure('YN.TNotebook.Tab',
                     background=C['bg3'], foreground=C['fg2'],
                     padding=[18, 7], font=('Segoe UI', 10, 'bold'), borderwidth=0)
        st.map('YN.TNotebook.Tab',
               background=[('selected', C['bg4'])],
               foreground=[('selected', C['lblue'])])
        st.configure('Vertical.TScrollbar',
                     background=C['bg3'], troughcolor=C['bg'], borderwidth=0,
                     arrowcolor=C['fg2'])

    # ── Top bar ───────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        top = tk.Frame(root, bg=C['bg2'], height=58)
        top.pack(fill=tk.X); top.pack_propagate(False)

        # Logo
        logo = tk.Frame(top, bg=C['acc'], width=36, height=36)
        logo.place(x=14, y=11)
        tk.Label(logo, text='▼', bg=C['acc'], fg=C['white'],
                 font=('Segoe UI', 14, 'bold')).place(relx=.5, rely=.5, anchor='center')
        tk.Label(top, text='YoniTube', bg=C['bg2'], fg=C['lblue'],
                 font=('Segoe UI', 16, 'bold')).place(x=58, y=14)
        tk.Label(top, text='by. The_Yonatan', bg=C['bg2'], fg=C['grey'],
                 font=('Segoe UI', 9)).place(x=186, y=22)

        self.srv_lbl = tk.Label(top, text='● מחכה...', bg=C['bg2'],
                                fg=C['yellow'], font=('Segoe UI', 10, 'bold'))
        self.srv_lbl.pack(side=tk.RIGHT, padx=16)
        tk.Button(top, text='🔄', bg=C['bg3'], fg=C['fg2'], relief=tk.FLAT,
                  cursor='hand2', font=('Segoe UI', 12),
                  command=self._restart_server).pack(side=tk.RIGHT, pady=12)

        # Status stripe
        self.gline = tk.Frame(root, bg=C['acc'], height=3)
        self.gline.pack(fill=tk.X)

        # Notebook
        nb = ttk.Notebook(root, style='YN.TNotebook')
        nb.pack(fill=tk.BOTH, expand=True)
        self._tab_dl(nb)
        self._tab_queue(nb)
        self._tab_settings(nb)
        self._tab_log(nb)

        # Bottom bar
        bot = tk.Frame(root, bg=C['bg2'], height=40)
        bot.pack(fill=tk.X, side=tk.BOTTOM); bot.pack_propagate(False)
        for txt, bg, fg, cmd in [
            ('🛑 עצור הכל',   C['dkred'], C['pink'],  self._kill_all),
            ('🗑 נקה הושלמו', C['bg3'],   C['fg2'],   self._clear_done),
            ('📂 פתח תיקייה', C['bg3'],   C['lblue'], self._open_folder),
        ]:
            tk.Button(bot, text=txt, bg=bg, fg=fg, relief=tk.FLAT,
                      cursor='hand2', font=('Segoe UI', 9, 'bold'),
                      command=cmd).pack(side=tk.LEFT, padx=7, pady=7)
        self.bot_stat = tk.Label(bot, text='', bg=C['bg2'],
                                 fg=C['fg2'], font=('Segoe UI', 9))
        self.bot_stat.pack(side=tk.RIGHT, padx=12)
        tk.Label(bot, text='v6 | port 5001', bg=C['bg2'],
                 fg=C['grey'], font=('Segoe UI', 8)).pack(side=tk.RIGHT, padx=16)

    # ── Download tab ──────────────────────────────────────────────
    def _tab_dl(self, nb):
        frm = tk.Frame(nb, bg=C['bg'])
        nb.add(frm, text='⬇  הורדה')

        def section(txt):
            f = tk.Frame(frm, bg=C['bg'])
            f.pack(fill=tk.X, padx=14, pady=2)
            tk.Label(f, text=txt, bg=C['bg'], fg=C['fg2'],
                     font=('Segoe UI', 9, 'bold'), width=16, anchor='e').pack(side=tk.RIGHT)
            return f

        def sep():
            tk.Frame(frm, bg=C['bdr'], height=1).pack(fill=tk.X, padx=14, pady=3)

        # URL
        ur = section('🔗 קישור:')
        self.url_var = tk.StringVar()
        tk.Entry(ur, textvariable=self.url_var, bg=C['bg3'], fg=C['fg'],
                 insertbackground=C['white'], relief=tk.FLAT,
                 font=('Segoe UI', 11)).pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=5, padx=4)
        tk.Button(ur, text='✕', bg=C['bg3'], fg=C['grey'], relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.url_var.set('')
                  ).pack(side=tk.LEFT, padx=4)
        sep()

        # Format
        fr = section('🎬 פורמט:')
        self.fmt_var = tk.StringVar(value='mp3')
        ttk.Combobox(fr, textvariable=self.fmt_var, state='readonly', width=13,
                     values=['mp3','m4a','flac','wav','aac','ogg','opus','wma','aiff',
                             'mp4','mkv','webm','mov','avi','flv','mpg','3gp','ts','thumbnail'],
                     font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=4)

        # Quality
        qr = section('📐 איכות:')
        self.qual_var = tk.StringVar(value='מקסימום')
        ttk.Combobox(qr, textvariable=self.qual_var, state='readonly', width=15,
                     values=['מקסימום','4K (2160p)','1080p','720p','480p','360p','240p'],
                     font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=4)

        # Speed
        sr = section('⚡ מהירות:')
        self.spd_var = tk.StringVar(value='medium')
        ttk.Combobox(sr, textvariable=self.spd_var, state='readonly', width=15,
                     values=['slow — 4 חיבורים','medium — 8 חיבורים','fast — 16 חיבורים'],
                     font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=4)

        # Subtitles
        sub_r = section('💬 כתוביות:')
        self.sub_var = tk.StringVar(value='')
        ttk.Combobox(sub_r, textvariable=self.sub_var, state='readonly', width=13,
                     values=['','he','en','ar','ru','fr','es','de','zh-Hans','ja','pt','auto'],
                     font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=4)

        # Custom resolution
        rr = section('📏 רזולוציה:')
        self.res_w = tk.Entry(rr, width=7, bg=C['bg3'], fg=C['fg'],
                              insertbackground=C['white'], relief=tk.FLAT, font=('Segoe UI', 10))
        self.res_h = tk.Entry(rr, width=7, bg=C['bg3'], fg=C['fg'],
                              insertbackground=C['white'], relief=tk.FLAT, font=('Segoe UI', 10))
        self.res_w.pack(side=tk.RIGHT, padx=2, ipady=3)
        tk.Label(rr, text='×', bg=C['bg'], fg=C['grey']).pack(side=tk.RIGHT)
        self.res_h.pack(side=tk.RIGHT, padx=2, ipady=3)
        tk.Label(rr, text='W × H (ריק = אוטומטי)', bg=C['bg'],
                 fg=C['grey'], font=('Segoe UI', 8)).pack(side=tk.RIGHT, padx=8)

        # Content type (for playlists/channels)
        ct_r = section('📋 סוג תוכן:')
        self.ct_var = tk.StringVar(value='all')
        ttk.Combobox(ct_r, textvariable=self.ct_var, state='readonly', width=15,
                     values=['all — הכל', 'videos — סרטונים', 'shorts — שורטס'],
                     font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=4)

        sep()

        # Download folder
        pr = section('📂 תיקיית הורדות:')
        self.path_var = tk.StringVar()
        pe = tk.Entry(pr, textvariable=self.path_var, bg=C['bg3'], fg=C['fg'],
                      insertbackground=C['white'], relief=tk.FLAT, font=('Segoe UI', 10))
        pe.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4, ipady=3)
        tk.Button(pr, text='📁 עיון', bg=C['bg4'], fg=C['lblue'], relief=tk.FLAT,
                  cursor='hand2', font=('Segoe UI', 9, 'bold'),
                  command=self._browse).pack(side=tk.LEFT, padx=6, pady=4)

        sep()

        # Download button
        btn_f = tk.Frame(frm, bg=C['bg'])
        btn_f.pack(padx=14, pady=6, fill=tk.X)
        self.dl_btn = tk.Button(
            btn_f, text='⬇   הוריד',
            bg=C['acc'], fg=C['white'], activebackground=C['acc2'],
            activeforeground=C['white'],
            font=('Segoe UI', 13, 'bold'), relief=tk.FLAT, cursor='hand2',
            padx=28, pady=10, command=self._download,
        )
        self.dl_btn.pack(side=tk.RIGHT)

        self.dl_stat = tk.Label(frm, text='', bg=C['bg'],
                                fg=C['lgreen'], font=('Segoe UI', 10))
        self.dl_stat.pack(padx=14, pady=2, anchor='e')

    def _browse(self):
        d = filedialog.askdirectory(
            title='בחר תיקיית הורדות',
            initialdir=self.path_var.get() or os.path.expanduser('~'))
        if d:
            self.path_var.set(d)

    def _download(self):
        url = self.url_var.get().strip()
        if not url:
            self.dl_stat.config(text='⚠ נא להזין קישור', fg=C['red']); return

        fmt  = self.fmt_var.get()
        qual = self.qual_var.get()
        raw_spd = self.spd_var.get().split(' ')[0]  # extract 'slow'/'medium'/'fast'
        ct   = self.ct_var.get().split(' ')[0]

        q_map = {'מקסימום': None, '4K (2160p)': 2160, '1080p': 1080,
                 '720p': 720, '480p': 480, '360p': 360, '240p': 240}
        body = {'url': url, 'format': fmt, 'speed': raw_spd, 'content_type': ct}

        h = q_map.get(qual)
        if h: body['height'] = h

        w = self.res_w.get().strip(); rh = self.res_h.get().strip()
        if w and rh:
            try: body['width'] = int(w); body['height'] = int(rh)
            except: pass

        sl = self.sub_var.get().strip()
        if sl: body['subtitle_lang'] = sl

        bp = self.path_var.get().strip()
        if bp: body['base_path'] = bp

        self.dl_btn.config(state=tk.DISABLED)
        self.dl_stat.config(text='📡 שולח...', fg=C['yellow'])

        def _go():
            try:
                import urllib.request as ur2
                req = ur2.Request(
                    SRV_URL + '/download',
                    data=json.dumps(body).encode(),
                    headers={'Content-Type': 'application/json'},
                    method='POST')
                with ur2.urlopen(req, timeout=10) as r:
                    d = json.loads(r.read())
                if d.get('error'):
                    self.root.after(0, lambda: self.dl_stat.config(
                        text='❌ ' + d['error'][:60], fg=C['red']))
                else:
                    msg = f"✅ {d.get('format','').upper()} נוסף ({d.get('queue',0)} בתור)"
                    self.root.after(0, lambda: self.dl_stat.config(text=msg, fg=C['lgreen']))
            except Exception as e:
                err = str(e)[:60]
                self.root.after(0, lambda: self.dl_stat.config(
                    text='❌ ' + err, fg=C['red']))
            finally:
                self.root.after(0, lambda: self.dl_btn.config(state=tk.NORMAL))
        threading.Thread(target=_go, daemon=True).start()

    # ── Queue tab ─────────────────────────────────────────────────
    def _tab_queue(self, nb):
        frm = tk.Frame(nb, bg=C['bg'])
        nb.add(frm, text='📋  תור')
        tb = tk.Frame(frm, bg=C['bg2'])
        tb.pack(fill=tk.X)
        self.q_stat = tk.Label(tb, text='', bg=C['bg2'], fg=C['fg2'],
                               font=('Segoe UI', 9))
        self.q_stat.pack(side=tk.LEFT, padx=10, pady=5)
        # Scroll canvas
        wrap = tk.Frame(frm, bg=C['bg'])
        wrap.pack(fill=tk.BOTH, expand=True)
        self.qc = tk.Canvas(wrap, bg=C['bg'], highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.qc.yview,
                            style='Vertical.TScrollbar')
        self.qc.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.qc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.qi = tk.Frame(self.qc, bg=C['bg'])
        self._qcw = self.qc.create_window((0, 0), window=self.qi, anchor='nw')
        self.qi.bind('<Configure>',
                     lambda e: self.qc.configure(scrollregion=self.qc.bbox('all')))
        self.qc.bind('<Configure>',
                     lambda e: self.qc.itemconfig(self._qcw, width=e.width))

    def _refresh_queue(self, merged):
        # Remove stale
        for uid in list(self.q_frames):
            if uid not in merged:
                self.q_frames[uid][0].destroy()
                del self.q_frames[uid]

        act = sum(1 for x in merged.values() if x.get('status') == 'downloading')
        inq = sum(1 for x in merged.values() if x.get('status') == 'queued')
        cvt = sum(1 for x in merged.values() if x.get('status') == 'converting')
        parts = []
        if inq:  parts.append(f'{inq} בתור')
        if act:  parts.append(f'{act} יורדים')
        if cvt:  parts.append(f'{cvt} ממירים')
        self.q_stat.config(text=' | '.join(parts) if parts else f'{len(merged)} פריטים')

        COL = {'downloading': C['acc2'], 'converting': C['amber'],
               'done': C['green'], 'err': C['red'], 'queued': C['grey']}
        ICO = {'downloading': '📥', 'converting': '🔄',
               'done': '✅', 'err': '❌', 'queued': '⏳'}

        for uid, info in merged.items():
            raw    = info.get('title', '') or ''
            is_real= raw and len(raw) > 4 and not re.match(r'^[A-Za-z0-9_-]{8,15}$', raw)
            title  = raw if is_real else '📡 טוען...'
            fmt    = (info.get('format') or '').upper()
            pct    = min(100.0, float(info.get('pct', 0) or 0))
            status = info.get('status', 'queued')
            color  = COL.get(status, C['grey'])
            icon   = ICO.get(status, '⏳')
            done_b = info.get('bytes_done', 0) or 0
            spd    = info.get('speed_str', '') or ''

            def _fb(b):
                if b <= 0: return ''
                if b >= 1<<20: return f'{b/(1<<20):.1f}MB'
                if b >= 1<<10: return f'{b/(1<<10):.0f}KB'
                return f'{b}B'

            meta = f'{fmt}  {_fb(done_b)}  {spd}  {icon}'.strip()

            if uid in self.q_frames:
                fw, bar, pct_lbl, title_lbl = self.q_frames[uid]
                self.root.update_idletasks()
                bw = bar.master.winfo_width()
                if bw > 10:
                    new_w = bw if status in ('done', 'err') else max(4, int(bw * pct / 100))
                    bar.place(x=0, y=0, height=4, width=int(new_w))
                bar.config(bg=color)
                if is_real: title_lbl.config(text=title)
                pct_lbl.config(text=icon if status in ('done', 'err') else f'{int(pct)}%',
                               fg=C['green'] if status == 'done' else C['red'] if status == 'err' else C['yellow'])
            else:
                fw = tk.Frame(self.qi, bg=C['bg2'], pady=0)
                fw.pack(fill=tk.X, padx=5, pady=2)
                hr = tk.Frame(fw, bg=C['bg2'])
                hr.pack(fill=tk.X, padx=8, pady=(5, 1))
                pct_lbl = tk.Label(hr, text=f'{int(pct)}%', bg=C['bg2'],
                                   fg=C['yellow'], font=('Consolas', 9, 'bold'), width=5)
                pct_lbl.pack(side=tk.LEFT)
                title_lbl = tk.Label(hr, text=title, bg=C['bg2'], fg=C['fg'],
                                     font=('Segoe UI', 9, 'bold'), anchor='e', justify=tk.RIGHT)
                title_lbl.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                tk.Label(fw, text=meta, bg=C['bg2'], fg=C['grey'],
                         font=('Segoe UI', 8), anchor='e').pack(fill=tk.X, padx=8, pady=(0, 2))
                btrack = tk.Frame(fw, bg=C['bdr'], height=4)
                btrack.pack(fill=tk.X, padx=8, pady=(1, 5))
                btrack.pack_propagate(False)
                bar = tk.Frame(btrack, bg=color, height=4)
                bar.place(x=0, y=0, height=4, width=max(4, int(4 * pct / 100)))
                self.q_frames[uid] = (fw, bar, pct_lbl, title_lbl)
        self.q_data = dict(merged)

    def _clear_done(self):
        for uid in [u for u in list(self.q_frames)
                    if self.q_data.get(u, {}).get('status') in ('done', 'err')]:
            self.q_frames[uid][0].destroy()
            del self.q_frames[uid]
        self.q_data = {u: v for u, v in self.q_data.items()
                       if v.get('status') not in ('done', 'err')}

    def _kill_all(self):
        try:
            import urllib.request as ur2
            ur2.urlopen(ur2.Request(SRV_URL + '/kill_all', data=b'', method='POST'), timeout=3)
        except Exception:
            pass
        self._log('🛑 כל ההורדות הופסקו', 'red')

    def _open_folder(self):
        folder = self.path_var.get().strip()
        if not folder:
            folder = os.path.join(os.path.expanduser('~'), 'Downloads',
                                  'YoniTube (by. The_Yonatan)')
        if os.path.exists(folder):
            if sys.platform == 'win32':
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])
        else:
            self._log(f'❌ תיקייה לא קיימת: {folder}', 'red')

    # ── Settings tab ──────────────────────────────────────────────
    def _tab_settings(self, nb):
        frm = tk.Frame(nb, bg=C['bg'])
        nb.add(frm, text='⚙  הגדרות')

        def row(lbl):
            r = tk.Frame(frm, bg=C['bg'])
            r.pack(fill=tk.X, padx=16, pady=6)
            tk.Label(r, text=lbl, bg=C['bg'], fg=C['fg2'],
                     font=('Segoe UI', 10), width=18, anchor='e').pack(side=tk.RIGHT)
            return r

        sr = row('⚡ מהירות ברירת מחדל:')
        self.gs_spd = tk.StringVar(value='medium')
        ttk.Combobox(sr, textvariable=self.gs_spd, state='readonly', width=18,
                     values=['slow','medium','fast']).pack(side=tk.RIGHT, padx=4)

        pr = row('📂 תיקיית הורדות:')
        self.gs_path = tk.StringVar()
        tk.Entry(pr, textvariable=self.gs_path, bg=C['bg3'], fg=C['fg'],
                 insertbackground=C['white'], relief=tk.FLAT, font=('Segoe UI', 10),
                 width=30).pack(side=tk.RIGHT, padx=4, fill=tk.X, expand=True, ipady=3)
        tk.Button(pr, text='📁', bg=C['bg3'], fg=C['fg2'], relief=tk.FLAT, cursor='hand2',
                  command=lambda: self.gs_path.set(
                      filedialog.askdirectory(initialdir=os.path.expanduser('~')) or self.gs_path.get()
                  )).pack(side=tk.LEFT, padx=4)

        tk.Frame(frm, bg=C['bdr'], height=1).pack(fill=tk.X, padx=16, pady=8)

        tk.Button(frm, text='💾  שמור הגדרות',
                  bg=C['acc'], fg=C['white'], activebackground=C['acc2'],
                  relief=tk.FLAT, cursor='hand2',
                  font=('Segoe UI', 10, 'bold'),
                  padx=20, pady=7, command=self._save_settings
                  ).pack(padx=16, pady=4, anchor='e')

    def _save_settings(self):
        if self.gs_path.get(): self.path_var.set(self.gs_path.get())
        self.spd_var.set(self.gs_spd.get())
        self._log('⚙️  הגדרות נשמרו', 'lgreen')

    # ── Log tab ───────────────────────────────────────────────────
    def _tab_log(self, nb):
        frm = tk.Frame(nb, bg=C['bg'])
        nb.add(frm, text='📜  לוג')
        tb = tk.Frame(frm, bg=C['bg2'])
        tb.pack(fill=tk.X)
        tk.Button(tb, text='🗑 נקה', bg=C['bg3'], fg=C['fg2'], relief=tk.FLAT,
                  cursor='hand2', command=self._clear_log).pack(side=tk.RIGHT, padx=8, pady=4)
        self.log_txt = tk.Text(frm, bg='#070710', fg='#3a4a5a',
                               font=('Consolas', 8), wrap=tk.WORD,
                               state=tk.DISABLED, bd=0, padx=7, pady=4)
        vsb = ttk.Scrollbar(frm, command=self.log_txt.yview)
        self.log_txt.config(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_txt.pack(fill=tk.BOTH, expand=True)
        for tag, col in [('ok', C['lgreen']), ('err', C['pink']), ('inf', C['lblue']),
                         ('warn', C['amber']), ('hdr', '#c084fc'), ('dim', '#3a4a5a')]:
            self.log_txt.tag_config(tag, foreground=col)

    def _log(self, msg, tag='dim'):
        def _do():
            self.log_txt.configure(state=tk.NORMAL)
            ts = time.strftime('%H:%M:%S')
            clean = ANSI.sub('', msg)
            self.log_txt.insert(tk.END, f'[{ts}] {clean}\n', tag)
            self.log_lines.append(clean)
            if len(self.log_lines) > 600:
                self.log_txt.delete('1.0', '2.0')
                self.log_lines.pop(0)
            self.log_txt.see(tk.END)
            self.log_txt.configure(state=tk.DISABLED)
        self.root.after(0, _do)

    def _clear_log(self):
        self.log_txt.configure(state=tk.NORMAL)
        self.log_txt.delete('1.0', tk.END)
        self.log_txt.configure(state=tk.DISABLED)
        self.log_lines.clear()

    # ── Embedded Flask server ─────────────────────────────────────
    def _start_server(self):
        threading.Thread(target=self._run_flask, daemon=True).start()
        self._log(f'🚀 מפעיל שרת מובנה על port {SRV_PORT}...', 'inf')

    def _run_flask(self):
        import sys as _sys, io

        class _Sink(io.TextIOBase):
            def __init__(s, app): s.app = app
            def write(s, m):
                m = m.rstrip()
                if not m: return len(m)
                t = ('ok'   if any(x in m for x in ('✅', 'SUCCESS', 'הורד')) else
                     'err'  if any(x in m for x in ('❌', 'ERROR', 'FAIL')) else
                     'hdr'  if '═' in m or 'YoniTube' in m else
                     'warn' if '⚠' in m else 'dim')
                s.app._log(m, t)
                return len(m)
            def flush(s): pass

        old_out, old_err = _sys.stdout, _sys.stderr
        try:
            sink = _Sink(self)
            _sys.stdout = sink
            _sys.stderr = sink
            sp   = os.path.join(_BD, 'server.py')
            spec = importlib.util.spec_from_file_location('_yn_gui_srv', sp)
            mod  = importlib.util.module_from_spec(spec)
            _sys.modules['_yn_gui_srv'] = mod
            spec.loader.exec_module(mod)
            import logging as _lg
            _lg.getLogger('werkzeug').setLevel(_lg.ERROR)
            mod.app.run(host='127.0.0.1', port=SRV_PORT,
                        debug=False, threaded=True, use_reloader=False)
        except Exception as e:
            self._log(f'❌ שגיאת שרת: {e}', 'err')
        finally:
            _sys.stdout, _sys.stderr = old_out, old_err

    def _restart_server(self):
        self._log('🔄 מאתחל שרת...', 'inf')
        self._start_server()

    # ── Poll server ───────────────────────────────────────────────
    def _poll(self):
        if not self.running: return
        try:
            import urllib.request as ur2
            with ur2.urlopen(SRV_URL + '/status', timeout=2) as r:
                d = json.loads(r.read())
            act = d.get('stats', {}).get('active', 0)
            q   = d.get('queue', 0)
            parts = []
            if q:   parts.append(f'{q} בתור')
            if act: parts.append(f'{act} יורדים')
            txt = '● פעיל' + (' | ' + ' '.join(parts) if parts else '')
            self.srv_lbl.config(text=txt, fg=C['green'])
            self.gline.config(bg=C['green'])
            am = d.get('active_map', {})
            self._refresh_queue(am)
            self.bot_stat.config(
                text=f"✅{d.get('stats',{}).get('success',0)} ❌{d.get('stats',{}).get('failed',0)}")
        except Exception:
            self.srv_lbl.config(text='● מפעיל שרת...', fg=C['yellow'])
            self.gline.config(bg=C['amber'])
        self.root.after(1800, self._poll)

    def _quit(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    App().run()
