import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import os
import sys




def _legacy_resource_path(filename: str) -> str:
    """Compatibility helper retained for older packaged builds."""
    if getattr(sys, 'frozen', False):
        # PyInstaller exe içinden
        base = os.path.dirname(sys.executable)
    else:
        # Normal python script çalıştırırken
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)







import sys

def resource_path(relpath: str) -> str:
    """Return a resource path for both source and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relpath)







# ===================== NASA NeoWs CSV -> PRESET dönüştürücü =====================
def load_presets_from_csv(csv_path, default_rho=3000.0, hazard_rho=3500.0, limit=None):
    """
    neo_feed.csv (DictReader) -> Python dict
      d: ortalama çap (m)
      v: km/s (CSV'deki km/h -> /3600)
      rho: kg/m^3 (tehlikeli ise hazard_rho, değilse default_rho)
    limit: ilk N kaydı al (None = hepsi)
    """
    import csv
    presets = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for i, row in enumerate(r):
                if limit is not None and i >= limit:
                    break
                try:
                    name_src = row["name"].strip()
                    date_src = row["date"].strip()
                    dmin = float(row["estimated_diameter_m_min"])
                    dmax = float(row["estimated_diameter_m_max"])
                    vel_kmh = float(row["rel_velocity_km_h"]) if row["rel_velocity_km_h"] else 0.0
                    haz_raw = str(row.get("is_potentially_hazardous", "")).strip().lower()
                    haz = haz_raw in ("true", "1", "yes", "y")
                except Exception:
                    # eksik/sorunlu satır varsa atla
                    continue

                key = f"{name_src} ({date_src})"   # örn: "(1991 GO) (2025-10-01)"
                d_avg = (dmin + dmax) / 2.0                    # metre
                v_kms = vel_kmh / 3600.0                       # km/s
                rho   = hazard_rho if haz else default_rho     # kg/m^3

                presets[key] = {"d": round(d_avg, 3),
                                "v": round(v_kms, 3),
                                "rho": float(rho)}
    except FileNotFoundError:
        # CSV yoksa sessizce boş dön
        return {}
    return presets

# =========================== HARİTA DOSYASI ===========================
MAP_FILE_CANDIDATES = ["Turkey_location_map.gif", "turkey_map.gif", "turkey_map.gif"]  # sende 'turkey_map.gif' var
for _cand in MAP_FILE_CANDIDATES:
    candidate = resource_path(_cand)
    if os.path.exists(candidate):
        MAP_FILE = candidate
        break
else:
    MAP_FILE = resource_path(MAP_FILE_CANDIDATES[-1])


# =========================== ŞEHİR LİSTESİ (81) ===========================
TURKEY_81 = [
    "Adana","Adıyaman","Afyonkarahisar","Ağrı","Aksaray","Amasya","Ankara","Antalya","Ardahan","Artvin",
    "Aydın","Balıkesir","Bartın","Batman","Bayburt","Bilecik","Bingöl","Bitlis","Bolu","Burdur",
    "Bursa","Çanakkale","Çankırı","Çorum","Denizli","Diyarbakır","Düzce","Edirne","Elazığ","Erzincan",
    "Erzurum","Eskişehir","Gaziantep","Giresun","Gümüşhane","Hakkâri","Hatay","Iğdır","Isparta","İstanbul",
    "İzmir","Kahramanmaraş","Karabük","Karaman","Kars","Kastamonu","Kayseri","Kırıkkale","Kırklareli","Kırşehir",
    "Kilis","Kocaeli","Konya","Kütahya","Malatya","Manisa","Mardin","Mersin","Muğla","Muş",
    "Nevşehir","Niğde","Ordu","Osmaniye","Rize","Sakarya","Samsun","Siirt","Sinop","Sivas",
    "Şanlıurfa","Şırnak","Tekirdağ","Tokat","Trabzon","Tunceli","Uşak","Van","Yalova","Yozgat","Zonguldak"
]

# =========================== 2024 NÜFUS (PopCap) ===========================
CITY_POP_CAP = {
    "İstanbul": 15701602, "Ankara": 5864049, "İzmir": 4493242, "Bursa": 3238618, "Antalya": 2722103,
    "Konya": 2330024, "Adana": 2280484, "Şanlıurfa": 2237745, "Gaziantep": 2193363, "Kocaeli": 2130006,
    "Mersin": 1954279, "Diyarbakır": 1833684, "Hatay": 1562185, "Manisa": 1475353, "Kayseri": 1452458,
    "Samsun": 1382376, "Balıkesir": 1276096, "Tekirdağ": 1187162, "Aydın": 1165943, "Kahramanmaraş": 1134105,
    "Van": 1118087, "Sakarya": 1110735, "Muğla": 1081867, "Denizli": 1061371, "Eskişehir": 921630,
    "Mardin": 895911, "Trabzon": 822270, "Ordu": 770711, "Malatya": 750491, "Afyonkarahisar": 750193,
    "Erzurum": 745005, "Batman": 654528, "Sivas": 637007, "Tokat": 612674, "Adıyaman": 611037,
    "Elazığ": 603941, "Zonguldak": 586802, "Kütahya": 571078, "Şırnak": 570826, "Çanakkale": 568966,
    "Osmaniye": 561061, "Çorum": 521335, "Ağrı": 499801, "Giresun": 455922, "Isparta": 446409,
    "Aksaray": 439474, "Edirne": 421247, "Yozgat": 413161, "Düzce": 412344, "Muş": 392301,
    "Kastamonu": 381991, "Kırklareli": 379031, "Uşak": 375310, "Niğde": 372708, "Bitlis": 359808,
    "Rize": 346977, "Amasya": 342378, "Siirt": 336453, "Bolu": 326409, "Nevşehir": 317952,
    "Yalova": 307882, "Bingöl": 283276, "Kırıkkale": 283053, "Hakkâri": 282191, "Burdur": 275826,
    "Kars": 272300, "Karaman": 262791, "Karabük": 250478, "Kırşehir": 244546, "Erzincan": 241239,
    "Bilecik": 228495, "Sinop": 226957, "Iğdır": 206857, "Bartın": 206715, "Çankırı": 199981,
    "Artvin": 169280, "Kilis": 156739, "Gümüşhane": 142617, "Ardahan": 91354, "Tunceli": 86612,
    "Bayburt": 83676,
}
DEFAULT_POP_GUESS = 350_000
for city in TURKEY_81:
    CITY_POP_CAP.setdefault(city, DEFAULT_POP_GUESS)

# =========================== 2024 NÜFUS YOĞUNLUĞU (/km²) ===========================
CITY_DENSITIES_81 = {
    "İstanbul": 2751, "Kocaeli": 549, "İzmir": 351, "Yalova": 320, "Gaziantep": 295, "Hatay": 284,
    "Bursa": 272, "Ankara": 212, "Sakarya": 206, "Zonguldak": 188, "Trabzon": 169, "Adana": 163,
    "Tekirdağ": 162, "Osmaniye": 157, "Düzce": 145, "Samsun": 136, "Aydın": 134, "Batman": 130,
    "Ordu": 128, "Antalya": 116, "Mersin": 111, "Diyarbakır": 111, "Manisa": 108, "Şanlıurfa": 103,
    "Kilis": 98.2, "Mardin": 94.0, "Rize": 86.2, "Denizli": 85.2, "Balıkesir": 82.5, "Adıyaman": 82.0,
    "Bartın": 80.8, "Kayseri": 79.9, "Kahramanmaraş": 78.8, "Muğla": 74.7, "Şırnak": 69.4, "Edirne": 65.6,
    "Uşak": 65.5, "Malatya": 64.1, "Elazığ": 63.8, "Giresun": 63.3, "Eskişehir": 61.1, "Tokat": 60.1,
    "Amasya": 58.6, "Karabük": 58.5, "Kırıkkale": 58.4, "Siirt": 58.0, "Kırklareli": 55.6, "Iğdır": 54.6,
    "Çanakkale": 54.1, "Konya": 53.5, "Nevşehir": 53.4, "Van": 53.3, "Bilecik": 53.3, "Aksaray": 51.4,
    "Afyonkarahisar": 51.0, "Isparta": 49.9, "Niğde": 49.3, "Kütahya": 48.4, "Ağrı": 47.3, "Muş": 46.3,
    "Çorum": 42.1, "Bitlis": 41.2, "Hakkâri": 39.1, "Sinop": 36.8, "Bolu": 36.7, "Burdur": 36.1,
    "Kırşehir": 35.6, "Bingöl": 33.1, "Yozgat": 31.1, "Erzurum": 30.4, "Karaman": 28.9, "Kastamonu": 28.5,
    "Kars": 28.0, "Gümüşhane": 25.2, "Çankırı": 24.6, "Artvin": 22.5, "Bayburt": 22.2, "Sivas": 21.6,
    "Erzincan": 19.8, "Ardahan": 19.7, "Tunceli": 10.8,
}
for city in TURKEY_81:
    CITY_DENSITIES_81.setdefault(city, 60.0)

# =========================== SEISMIC MAP — SADECE bu 7 şehir ===========================
SEISMIC_INCLUDE = [
    ("Antalya", 36.89, 30.70),
    ("Ankara", 39.93, 32.86),
    ("İzmir", 38.42, 27.14),
    ("İstanbul", 41.01, 28.97),
    ("Rize", 41.02, 40.52),
    ("Erzurum", 39.90, 41.27),
    ("Adana", 37.00, 35.32),
]

# Başlangıç offsetleri (harita pikseli) — program açılışında böyle görünsün
DEFAULT_OFFSETS = {
    "Antalya":  (9, 32),
    "Ankara":   (0, 0),
    "İzmir":    (14, 22),
    "İstanbul": (15, 0),
    "Rize":     (16, 5),
    "Erzurum":  (0, 0),
    "Adana":    (14, 55),
}

# =========================== METEOR PRESETS (BÖLÜNMEMİŞ DEĞERLER) ===========================
# d: metre, v: km/s, rho: kg/m³
PRESETS = {
    "Impactor 2025":      {"d": 250.0,  "v": 25.0,   "rho": 3000.0},
    "Chelyabinsk (2013)": {"d": 19.0,   "v": 19.0,   "rho": 3600.0},
    "Tunguska (1908)":    {"d": 75.0,   "v": 15.5,   "rho": 2500.0},  # temsilî orta değerler
    "Apophis":            {"d": 370.0,  "v": 30.73,  "rho": 3200.0},
    "1950 DA":            {"d": 1300.0, "v": 17.0,   "rho": 3000.0},
    "Chicxulub":          {"d": 10000.0,"v": 20.0,   "rho": 2700.0},
    "Barringer":          {"d": 50.0,   "v": 17.0,   "rho": 7800.0},
    "2019 OK":            {"d": 100.0,  "v": 24.5,   "rho": 3000.0},
    "2008 TC3":           {"d": 4.0,    "v": 12.4,   "rho": 1800.0},
}

# CSV'den otomatik NASA NEO presetleri ekle (dosya varsa)
PRESETS.update(load_presets_from_csv(resource_path("neo_feed.csv")))


# Harita coğrafi sınırları
LAT_MIN, LAT_MAX = 35.0, 42.0
LON_MIN, LON_MAX = 26.0, 45.0

# ===================== FİZİK / HESAPLAR ==================
def kinetic_energy_mt(d_m, rho, v_kms):
    r = d_m / 2.0
    vol = (4.0/3.0) * math.pi * (r**3)
    m = vol * rho
    v = v_kms * 1000.0
    E = 0.5 * m * v * v
    return E / 4.184e15  # Mt TNT

def crater_diameter_km(d_m, v_kms, rho):
    # Görsel ölçek (demo); gerçek krater fiziği değildir
    D_m = max(5.0, (d_m**0.78) * (v_kms**0.44) * ((rho/3000.0)**0.26) * 140.0)
    return D_m / 1000.0

def casualties_capped(D_km, dens, pop_cap):
    """
    Etki alanı ~ pi*(3*D)^2, people = alan * yoğunluk.
    Dead=20%, Inj=40%, fakat:
      - dead >= pop_cap -> dead=pop_cap, inj=0
      - dead+inj > pop_cap -> inj = pop_cap - dead
    """
    area = math.pi * (D_km * 3.0)**2
    people = area * dens
    dead = int(people * 0.20)
    inj  = int(people * 0.40)
    if dead >= pop_cap:
        return pop_cap, 0
    total = dead + inj
    if total > pop_cap:
        inj = max(0, pop_cap - dead)
    return dead, inj

# =========================== ANA UYGULAMA ===========================
class MeteorCitySim:
    def __init__(self, root):
        self.root = root
        root.title("☄️ Meteor Impact — Black/Red")
        root.geometry("1500x980")
        root.minsize(1200, 820)
        root.configure(bg="#0a0a0a")

        # Sol: kanvas, Sağ: panel
        self.canvas = tk.Canvas(root, bg="#050505", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10,6), pady=10)
        side = tk.Frame(root, width=500, bg="#0a0a0a")
        side.pack(side="right", fill="y", padx=(6,10), pady=10)

        # -------- Inputlar --------
        self.d_var   = tk.StringVar(value="50")
        self.v_var   = tk.StringVar(value="20")
        self.rho_var = tk.StringVar(value="3000")

        self._num_input(side, "Diameter (m):", self.d_var)
        self._num_input(side, "Velocity (km/s):", self.v_var)
        self._num_input(side, "Density (kg/m³):", self.rho_var)

        # Preset seçici (seçildiği anda otomatik uygular)
        box = tk.Frame(side, bg="#0a0a0a"); box.pack(fill="x", padx=12, pady=(6,0))
        tk.Label(box, text="Meteor Preset:", fg="#ffcccc", bg="#0a0a0a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        # PRESETS boş değilse ilkini seç; yoksa boş string
        first_key = list(PRESETS.keys())[0] if PRESETS else ""
        self.preset_var = tk.StringVar(value=first_key)
        self.preset_combo = ttk.Combobox(box, textvariable=self.preset_var,
                                         values=list(PRESETS.keys()), state="readonly")
        self.preset_combo.pack(fill="x", pady=4)
        self.preset_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_preset())
        tk.Button(box, text="Apply", command=self.apply_preset,
                  bg="#111", fg="#ff2a2a", activebackground="#1c1c1c",
                  activeforeground="#ffd6d6", relief="flat").pack(anchor="e")

        # >>> YENİ: CSV'den tekrar yükle butonu
        tk.Button(box, text="Load NASA CSV", command=self.reload_presets,
                  bg="#151515", fg="#ff8a8a",
                  activebackground="#1c1c1c", activeforeground="#ffd6d6",
                  relief="flat").pack(anchor="e", pady=(6,0))

        btn_style = dict(bg="#111", fg="#ff2a2a", activebackground="#1c1c1c",
                         activeforeground="#ffd6d6", relief="flat", bd=0, font=("Segoe UI", 11, "bold"))
        tk.Button(side, text="IMPACT", command=self.impact, **btn_style).pack(fill="x", padx=12, pady=(10,6))
        tk.Button(side, text="Seismic Map", command=self.open_seismic, **btn_style).pack(fill="x", padx=12, pady=4)
        tk.Button(side, text="Needs Planner", command=self.open_needs, **btn_style).pack(fill="x", padx=12, pady=4)
        tk.Button(side, text="Nüfus Düzenleyici", command=self.open_pop_editor, **btn_style).pack(fill="x", padx=12, pady=4)
        tk.Button(side, text="Yoğunluk Düzenleyici", command=self.open_density_editor, **btn_style).pack(fill="x", padx=12, pady=4)

        self.info = tk.Label(side, text="Preset seç → Apply, sonra IMPACT 👆",
                             justify="left", fg="#ddd", bg="#0a0a0a", font=("Consolas", 10))
        self.info.pack(anchor="w", padx=12, pady=8)

        # Sonuç araçları
        tools = tk.Frame(side, bg="#0a0a0a")
        tools.pack(fill="x", padx=12, pady=(2, 0))
        tk.Label(tools, text="Şehir filtrele", fg="#ffcccc", bg="#0a0a0a",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        search_row = tk.Frame(tools, bg="#0a0a0a")
        search_row.pack(fill="x", pady=(3, 5))
        self.city_filter = tk.StringVar()
        self.city_filter.trace_add("write", lambda *_: self.render_results())
        ttk.Entry(search_row, textvariable=self.city_filter).pack(side="left", fill="x", expand=True)
        tk.Button(search_row, text="Temizle", command=lambda: self.city_filter.set(""),
                  bg="#151515", fg="#ffcccc", activebackground="#1c1c1c",
                  activeforeground="#fff", relief="flat").pack(side="left", padx=(6, 0))
        tk.Button(search_row, text="CSV Aktar", command=self.export_results,
                  bg="#151515", fg="#ff8a8a", activebackground="#1c1c1c",
                  activeforeground="#fff", relief="flat").pack(side="left", padx=(6, 0))
        self.result_count = tk.Label(tools, text="Şehirleri karşılaştırmak için etkiyi çalıştırın",
                                     fg="#aaa", bg="#0a0a0a", font=("Segoe UI", 9))
        self.result_count.pack(anchor="w")

        # Tablo (81 il)
        style = ttk.Style()
        try: style.theme_use("clam")
        except: pass
        style.configure("Treeview", background="#0f0f0f", foreground="#eaeaea",
                        fieldbackground="#0f0f0f", rowheight=22, bordercolor="#222", borderwidth=0)
        style.configure("Treeview.Heading", background="#111", foreground="#ff3b3b",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#8a1f1f")], foreground=[("selected", "#ffffff")])
        cols = ("City","Dens(/km²)","PopCap","Dead","Injured")
        self.tree = ttk.Treeview(side, columns=cols, show="headings", height=18, style="Treeview")
        self.sort_column = "City"
        self.sort_reverse = False
        self.result_rows = []
        for c in cols:
            self.tree.heading(c, text=c, command=lambda column=c: self.sort_results(column))
        self.tree.column("City", width=120, anchor="w")
        for c in cols[1:]:
            self.tree.column(c, width=88, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)

        # İlk çizim
        self.last_D = None
        self.last_E_Mt = None
        self.canvas.bind("<Configure>", lambda e: self.draw_scene(self.last_D))
        root.bind("<Control-Return>", lambda _e: self.impact())
        root.bind("<Control-s>", lambda _e: self.export_results())

    def apply_preset(self):
        name = self.preset_var.get()
        p = PRESETS.get(name)
        if not p: 
            return
        self.d_var.set(str(p["d"]))
        self.v_var.set(str(p["v"]))
        self.rho_var.set(str(p["rho"]))

    # >>> YENİ: CSV'yi tekrar okuyup combobox'ı tazele
    def reload_presets(self):
        """
        neo_feed.csv dosyasını tekrar okur, PRESETS'e ekler/günceller
        ve combobox listesini tazeler.
        """
        try:
            added = load_presets_from_csv(resource_path("neo_feed.csv"))
        except Exception as e:
            messagebox.showerror("Hata", f"CSV okunamadı:\n{e}")
            return

        if not added:
            messagebox.showinfo("Bilgi", "neo_feed.csv bulunamadı veya yeni preset yok.")
            return

        # Aynı anahtar varsa günceller, yeni varsa ekler
        PRESETS.update(added)

        # Combobox listesini güncelle
        all_keys = list(PRESETS.keys())
        self.preset_combo["values"] = all_keys

        # Seçimi koru; yoksa ilkini seç
        current = self.preset_var.get()
        if current not in PRESETS and all_keys:
            self.preset_var.set(all_keys[0])

        self.info.config(text=f"{len(added)} NASA preset yüklendi. Listeden seç → Apply → IMPACT")

    def _num_input(self, parent, label, var):
        f = tk.Frame(parent, bg="#0a0a0a"); f.pack(fill="x", padx=12, pady=6)
        tk.Label(f, text=label, fg="#ff3b3b", bg="#0a0a0a", font=("Segoe UI", 11)).pack(anchor="w")
        e = ttk.Entry(f, textvariable=var); e.pack(fill="x", pady=2)
        def val(P):
            if P.strip()=="": return True
            try: float(P); return True
            except: return False
        e.config(validate="key", validatecommand=(parent.register(val), "%P"))

    def draw_scene(self, D_km=None):
        c = self.canvas
        w, h = max(800, c.winfo_width()), max(600, c.winfo_height())
        c.delete("all")

        # Arkaplan gradyan
        for i in range(h):
            r = int(20 + 40*i/h); g = int(10 + 18*i/h); b = int(10 + 18*i/h)
            c.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        # Şehir alanı
        margin = int(min(w,h) * 0.08)
        left, right = margin, w - margin
        top  = int(h*0.16); bottom = h - margin
        c.create_rectangle(left, top, right, bottom, fill="#0b0b0b", outline="#8a1f1f", width=3)

        # Grid
        city_width_km = 50.0
        px_per_km = (right-left) / city_width_km
        step = max(5, int(px_per_km))
        x = left
        while x <= right:
            c.create_line(x, top, x, bottom, fill="#1c1c1c", width=1); x += step
        y = top
        while y <= bottom:
            c.create_line(left, y, right, y, fill="#1c1c1c", width=1); y += step

        # Ölçek
        c.create_text(left, top-28, anchor="w", fill="#ffcccc", font=("Segoe UI", 16, "bold"),
                      text="City — width: 50 km")
        bar_km = 5.0; bar_px = int(bar_km * px_per_km); y0 = bottom + 16
        c.create_line(left, y0, left+bar_px, y0, fill="#ff3b3b", width=4)
        c.create_line(left, y0-8, left, y0+8, fill="#ff3b3b", width=3)
        c.create_line(left+bar_px, y0-8, left+bar_px, y0+8, fill="#ff3b3b", width=3)
        c.create_text(left + bar_px/2, y0+14, text=f"{bar_km:.0f} km", fill="#ffcccc")

        # Krater
        if D_km:
            cx, cy = (left+right)//2, (top+bottom)//2
            r = (D_km * px_per_km) / 2.0
            r = max(4, min(r, (right-left)*0.45))
            affected_r = max(12, min(D_km * 3.0 * px_per_km, (right-left)*0.48))
            c.create_oval(cx-affected_r, cy-affected_r, cx+affected_r, cy+affected_r,
                          outline="#ffb21a", width=2, dash=(7, 5))
            c.create_text(cx+affected_r, cy, text="  tahmini etki alanı",
                          anchor="w", fill="#ffb21a", font=("Segoe UI", 9, "bold"))
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#ff6b6b", width=3)
            c.create_oval(cx-r*0.94, cy-r*0.94, cx+r*0.94, cy+r*0.94, fill="#7a00f0", outline="")
            if self.last_E_Mt is not None:
                h_eq = self.last_E_Mt / 0.015
                c.create_text(cx, cy-r-38, text=f"Hiroşima eşdeğeri: {h_eq:,.0f}x",
                              fill="#ffdede", font=("Segoe UI", 12, "bold"))
            c.create_text(cx, cy-r-22, text=f"Crater {D_km:.2f} km",
                          fill="#ffdede", font=("Segoe UI", 14, "bold"))

    def impact(self):
        try:
            d = float(self.d_var.get()); v = float(self.v_var.get()); rho = float(self.rho_var.get())
        except:
            messagebox.showerror("Error", "Invalid input"); return
        if d <= 0 or v <= 0 or rho <= 0:
            messagebox.showerror("Error", "All values must be positive"); return

        E = kinetic_energy_mt(d, rho, v)
        D = crater_diameter_km(d, v, rho)
        self.last_D = D; self.last_E_Mt = E
        self.draw_scene(D)

        level = "Local airburst"
        if E >= 0.01: level = "City-scale damage"
        if E >= 10:   level = "Regional catastrophe"
        if E >= 1000: level = "Global-scale event"

        h_eq = E / 0.015
        self.info.config(text=f"Energy: {E:.2f} Mt TNT  (Hiroşima ≈ {h_eq:,.0f}x)\n"
                              f"Crater: {D:.2f} km — {level}")

        # 81 il karşılaştırması — nüfus tavanıyla sınırlı
        self.result_rows = []
        for city in sorted(TURKEY_81):
            dens = CITY_DENSITIES_81.get(city, 60.0)
            pop_cap = CITY_POP_CAP.get(city, DEFAULT_POP_GUESS)
            dead, inj = casualties_capped(D, dens, pop_cap)
            self.result_rows.append((city, dens, pop_cap, dead, inj))
        self.render_results()

    def visible_results(self):
        query = self.city_filter.get().strip().casefold()
        rows = [
            row for row in self.result_rows
            if not query or query in row[0].casefold()
        ]
        column_index = {
            "City": 0, "Dens(/km²)": 1, "PopCap": 2, "Dead": 3, "Injured": 4
        }[self.sort_column]
        rows.sort(
            key=lambda row: row[column_index].casefold()
            if column_index == 0 else row[column_index],
            reverse=self.sort_reverse,
        )
        return rows

    def render_results(self):
        if not hasattr(self, "tree"):
            return
        rows = self.visible_results()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for city, dens, pop_cap, dead, injured in rows:
            self.tree.insert(
                "", "end",
                values=(city, f"{dens:g}", f"{pop_cap:,}", f"{dead:,}", f"{injured:,}")
            )
        total = len(self.result_rows)
        self.result_count.config(
            text=f"{total} senaryodan {len(rows)} tanesi gösteriliyor"
            if total else "Şehirleri karşılaştırmak için etkiyi çalıştırın"
        )

    def sort_results(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.render_results()

    def export_results(self):
        rows = self.visible_results()
        if not rows:
            messagebox.showinfo("Dışa Aktar", "Sonuçları aktarmadan önce etkiyi çalıştırın.")
            return
        output_path = filedialog.asksaveasfilename(
            title="Etki senaryolarını dışa aktar",
            defaultextension=".csv",
            filetypes=[("CSV dosyaları", "*.csv")],
            initialfile="meteor-etki-senaryolari.csv",
        )
        if not output_path:
            return
        import csv
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as output:
                writer = csv.writer(output)
                writer.writerow(("Şehir", "Yoğunluk / km²", "Nüfus tavanı", "Ölü", "Yaralı"))
                writer.writerows(rows)
        except OSError as error:
            messagebox.showerror("Dışa aktarma başarısız", str(error))
            return
        messagebox.showinfo("Dışa aktarma tamamlandı", f"{len(rows)} senaryo kaydedildi.")

    def open_seismic(self):
        if not self.last_D:
            messagebox.showinfo("Info", "Run IMPACT first."); return
        SeismicMapWindow(self.root, crater_km=self.last_D)

    def open_needs(self):
        if not self.last_D:
            messagebox.showinfo("Info", "Run IMPACT first."); return
        NeedsPlanner(self.root, self.last_D)

    def open_pop_editor(self):
        PopEditor(self.root)

    def open_density_editor(self):
        DensityEditor(self.root)

# ===================== SEISMIC MAP (7 şehir, küçük eşit nokta, offset zoom’la) =====================
class SeismicMapWindow:
    """
    - SADECE: Antalya, Ankara, İzmir, İstanbul, Rize, Erzurum, Adana
    - Nokta r=4 (eşit ve küçük)
    - Offset’ler HARİTA piksel uzayında tutulur → zoom/pan ile ölçeklenir.
    - Şiddet numaraları SOLDAN.
    """
    def __init__(self, master, crater_km):
        try:
            from PIL import Image, ImageTk
        except Exception:
            Image = None; ImageTk = None

        self.top = tk.Toplevel(master)
        self.top.title("🌍 Seismic Map — adjustable offsets")
        self.top.geometry("1250x860")
        self.top.configure(bg="#0a0a0a")

        # Sol kontrol paneli
        self.side = tk.Frame(self.top, width=300, bg="#0a0a0a")
        self.side.pack(side="left", fill="y", padx=(10,6), pady=10)

        self.lab_city = tk.Label(self.side, text="Şehir: —", fg="#ffd6d6", bg="#0a0a0a", font=("Segoe UI", 12, "bold"))
        self.lab_city.pack(anchor="w", pady=(0,6))
        self.lab_info = tk.Label(self.side, text="Krater/Halkalar için şehre tıkla",
                                 justify="left", fg="#ddd", bg="#0a0a0a", font=("Consolas", 10))
        self.lab_info.pack(anchor="w", pady=(0,10))

        tk.Label(self.side, text="Offset Düzenle (harita pikseli)", fg="#ffcccc", bg="#0a0a0a",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6,4))

        # Varsayılan offsetler (program açılışında)
        self.offset_vars = {}
        self.CITY_OFFSET_BASE = {name: [DEFAULT_OFFSETS[name][0], DEFAULT_OFFSETS[name][1]] for name,_,_ in SEISMIC_INCLUDE}

        # Panel kontrolleri — başlangıç değerleri yukarıdaki defaultlardan
        for name, _, _ in SEISMIC_INCLUDE:
            f = tk.Frame(self.side, bg="#0a0a0a"); f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{name:12}", fg="#ffd6d6", bg="#0a0a0a", width=12, anchor="w").pack(side="left")
            dx0, dy0 = self.CITY_OFFSET_BASE.get(name, [0, 0])
            dx = tk.IntVar(value=dx0)
            dy = tk.IntVar(value=dy0)
            self.offset_vars[name] = (dx, dy)
            tk.Label(f, text="dx", fg="#bbb", bg="#0a0a0a").pack(side="left")
            tk.Spinbox(f, from_=-400, to=400, textvariable=dx, width=6, command=self.redraw).pack(side="left", padx=4)
            tk.Label(f, text="dy", fg="#bbb", bg="#0a0a0a").pack(side="left")
            tk.Spinbox(f, from_=-400, to=400, textvariable=dy, width=6, command=self.redraw).pack(side="left", padx=4)

        # Harita kanvası
        self.canvas = tk.Canvas(self.top, bg="#050505", highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True, padx=(6,10), pady=10)

        # Harita resmi
        self.Image = Image; self.ImageTk = ImageTk
        self.base_img = None; self.tk_img = None
        self.img_w0, self.img_h0 = 1791, 768
        if self.Image is not None and os.path.exists(MAP_FILE):
            try:
                self.base_img = self.Image.open(MAP_FILE).convert("RGB")
                self.img_w0, self.img_h0 = self.base_img.size
            except Exception as e:
                print("Harita yüklenemedi:", e)

        # Coğrafya & iç kutu
        self.lat_min, self.lat_max = LAT_MIN, LAT_MAX
        self.lon_min, self.lon_max = LON_MIN, LON_MAX
        self.LEFT_FRAC, self.RIGHT_FRAC = 0.020, 0.985
        self.TOP_FRAC,  self.BOTTOM_FRAC = 0.070, 0.960

        # Etkileşim
        self.zoom = 1.0
        self.offx = 0.0
        self.offy = 0.0
        self.dragging = False
        self.drag_start = (0,0)

        self.crater_km = crater_km
        self.city_points = []  # (name, x_screen, y_screen)

        # Events
        self.canvas.bind("<Configure>", self.redraw)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag, add="+")
        self.canvas.bind("<ButtonRelease-1>", self.on_click, add="+")
        self.canvas.bind("<MouseWheel>", self.on_zoom)      # Win/Mac
        self.canvas.bind("<Button-4>", self.on_zoom_button) # Linux up
        self.canvas.bind("<Button-5>", self.on_zoom_button) # Linux down

        self.redraw()

    # ---------- Yardımcı yerleşim ----------
    def _base_box(self):
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        if W < 10 or H < 10: return (0,0,0,0,0,0)
        img_aspect = self.img_w0 / self.img_h0
        can_aspect = W / H
        if can_aspect >= img_aspect:
            base_h = H
            base_w = int(img_aspect * base_h)
            x0 = (W - base_w)//2; y0 = 0
        else:
            base_w = W
            base_h = int(base_w / img_aspect)
            x0 = 0; y0 = (H - base_h)//2
        return x0, y0, base_w, base_h, W, H

    def _fit_box(self):
        x0, y0, base_w, base_h, W, H = self._base_box()
        draw_w = int(base_w * self.zoom)
        draw_h = int(base_h * self.zoom)
        x = x0 + int(self.offx); y = y0 + int(self.offy)
        return (x, y, draw_w, draw_h, x0, y0, base_w, base_h)

    def _render_map(self):
        if self.base_img is None or self.ImageTk is None:
            return None, (0,0,0,0)
        x, y, w, h, *_ = self._fit_box()
        if w < 5 or h < 5:
            return None, (x,y,w,h)
        resized = self.base_img.resize((w, h), resample=self.Image.BILINEAR)
        self.tk_img = self.ImageTk.PhotoImage(resized)
        self.canvas.create_image(x, y, image=self.tk_img, anchor="nw")
        return self.tk_img, (x, y, w, h)

    def _inner_box(self, outer):
        x, y, w, h = outer
        ix0 = x + self.LEFT_FRAC   * w
        ix1 = x + self.RIGHT_FRAC  * w
        iy0 = y + self.TOP_FRAC    * h
        iy1 = y + self.BOTTOM_FRAC * h
        return ix0, iy0, ix1, iy1

    def latlon_to_screen(self, lat, lon, inner):
        ix0, iy0, ix1, iy1 = inner
        tx = (lon - self.lon_min) / (self.lon_max - self.lon_min)
        ty = 1.0 - (lat - self.lat_min) / (self.lat_max - self.lat_min)
        sx = ix0 + tx * (ix1 - ix0)
        sy = iy0 + ty * (iy1 - iy0)
        return sx, sy

    # ---------- Çizim ----------
    def redraw(self, _=None):
        # paneldeki offset değerlerini (harita piksel uzayı) güncelle
        for name in list(self.CITY_OFFSET_BASE.keys()):
            dx_var, dy_var = self.offset_vars[name]
            self.CITY_OFFSET_BASE[name][0] = int(dx_var.get())
            self.CITY_OFFSET_BASE[name][1] = int(dy_var.get())

        c = self.canvas
        c.delete("all")

        tkimg, outer_box = self._render_map()
        if tkimg is None:
            W, H = c.winfo_width(), c.winfo_height()
            for i in range(0, W, 80): c.create_line(i, 0, i, H, fill="#220909")
            for j in range(0, H, 80): c.create_line(0, j, W, j, fill="#220909")
            outer_box = (0,0,W,H)

        inner = self._inner_box(outer_box)

        # Zoom ölçeği: harita pikselinden ekrana — tam olarak zoom
        _, _, draw_w, draw_h, _, _, base_w, base_h = self._fit_box()
        scale_x = draw_w / max(1, base_w)
        scale_y = draw_h / max(1, base_h)

        self.city_points.clear()
        for name, lat, lon in SEISMIC_INCLUDE:
            sx, sy = self.latlon_to_screen(lat, lon, inner)
            dx0, dy0 = self.CITY_OFFSET_BASE.get(name, [0,0])
            sx += dx0 * scale_x
            sy += dy0 * scale_y
            self.city_points.append((name, sx, sy))

        # Eşit ve küçük nokta (r=4)
        for name, x, y in self.city_points:
            r = 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#ff3b3b", outline="")
        for name, x, y in self.city_points:
            self.canvas.create_text(x+10, y, text=name, anchor="w",
                                    fill="#ffd6d6", font=("Segoe UI", 11, "bold"))

    # ---------- Etkileşim ----------
    def start_drag(self, e):
        self.dragging = True
        self.drag_start = (e.x, e.y)

    def drag_move(self, e):
        if not self.dragging: return
        dx, dy = e.x - self.drag_start[0], e.y - self.drag_start[1]
        self.offx += dx; self.offy += dy
        self.drag_start = (e.x, e.y)
        self.redraw()

    def end_drag(self, _e):
        self.dragging = False

    def _zoom_at(self, mx, my, factor):
        # Zoom'u imleç (mx,my) etrafında
        x0, y0, base_w, base_h, W, H = self._base_box()
        cur_x0 = x0 + self.offx; cur_y0 = y0 + self.offy
        dx = mx - cur_x0; dy = my - cur_y0
        old = self.zoom; new = max(0.5, min(6.0, old * factor))
        s = new / old
        self.offx = self.offx + (1 - s) * dx
        self.offy = self.offy + (1 - s) * dy
        self.zoom = new

    def on_zoom(self, e):
        self._zoom_at(e.x, e.y, 1.1 if e.delta > 0 else 1/1.1)
        self.redraw()

    def on_zoom_button(self, e):
        self._zoom_at(e.x, e.y, 1.1 if e.num == 4 else 1/1.1)
        self.redraw()

    def on_click(self, e):
        # En yakın şehir (25 px)
        nearest, best = None, 1e18
        for name, x, y in self.city_points:
            d2 = (x - e.x)**2 + (y - e.y)**2
            if d2 < best:
                best = d2; nearest = (name, x, y)
        if not nearest or best > (25**2): return
        name, cx, cy = nearest

        self.redraw()

        # Dinamik halkalar + numaralar SOLDAN
        _, _, w, _, _, _, _, _ = self._fit_box()
        px_per_km = max(w / 1650.0, 0.1)  # TR eni ~1650 km
        ring_km = [self.crater_km * i for i in (1,2,3,4,5)]
        colors  = ["#ff2b2b", "#ff6a1a", "#ffb21a", "#22c55e", "#3b82f6"]
        labels  = ["9","8","7","6","5"]
        for km, col, lab in zip(ring_km, colors, labels):
            r = max(4, km * px_per_km)
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=col, width=3)
            self.canvas.create_text(cx - r - 8, cy, text=lab, fill=col, anchor="e",
                                    font=("Segoe UI", 10, "bold"))
        self.canvas.create_oval(cx-7, cy-7, cx+7, cy+7, outline="#ff7a7a", width=2)

        info_lines = [f"Şehir: {name}", f"Krater: {self.crater_km:.2f} km", "Halkalar (km):"]
        info_lines += [f"  ×{i}: {rk:.2f}" for i, rk in zip((1,2,3,4,5), ring_km)]
        self.lab_city.config(text=f"Şehir: {name}")
        self.lab_info.config(text="\n".join(info_lines))

# =========================== NEEDS PLANNER (81 il + gün seçimi) ===========================
class NeedsPlanner:
    """
    Su: 2 L/kişi/gün, Kalori: 2500 kcal/kişi/gün, Çadır: 4 kişilik,
    Medkit: 1/50, Tuvalet: 1/20, Battaniye: 1/kişi, Powerbank: 1/10.
    Değerler nüfus tavanıyla sınırlandırılmış 'displaced = dead+injured' üstünden hesaplanır.
    """
    def __init__(self, master, D_km):
        self.D_km = D_km
        self.top = tk.Toplevel(master)
        self.top.title("🏕️ Needs Planner — Black/Red")
        self.top.geometry("980x640")
        self.top.configure(bg="#0a0a0a")

        controls = tk.Frame(self.top, bg="#0a0a0a"); controls.pack(fill="x", padx=12, pady=8)
        tk.Label(controls, text="Gün sayısı:", fg="#ffd6d6", bg="#0a0a0a").pack(side="left")
        self.days_var = tk.IntVar(value=7)
        tk.Spinbox(controls, from_=1, to=120, textvariable=self.days_var, width=5).pack(side="left", padx=6)
        tk.Button(controls, text="Hesapla", command=self.render, bg="#111", fg="#ff2a2a",
                  activebackground="#1c1c1c", activeforeground="#ffd6d6", relief="flat").pack(side="left", padx=8)

        self.txt = tk.Text(self.top, bg="#0f0f0f", fg="#ffd6d6", insertbackground="#ffd6d6",
                           font=("Consolas", 11), borderwidth=0, highlightthickness=0)
        self.txt.pack(fill="both", expand=True, padx=12, pady=12)

        self.render()

    def render(self):
        days = max(1, int(self.days_var.get()))
        lines = []
        lines.append(f"Crater diameter used: {self.D_km:.2f} km")
        lines.append(f"Gün sayısı: {days}\n")
        header = "City           | PopCap    | Displaced | Tents | Water(L) | Calories(kcal) | MedKits | Toilets | Blankets | Powerbanks"
        sep    = "---------------+-----------+-----------+-------+----------+----------------+---------+---------+----------+-----------"
        lines.append(header); lines.append(sep)

        for city in sorted(TURKEY_81):
            dens = CITY_DENSITIES_81.get(city, 60.0)
            pop_cap = CITY_POP_CAP.get(city, DEFAULT_POP_GUESS)
            dead, inj = casualties_capped(self.D_km, dens, pop_cap)
            displaced = min(pop_cap, dead + inj)

            tents      = (displaced + 3)//4
            water_l    = displaced * 2 * days
            calories   = displaced * 2500 * days
            medkits    = (displaced + 49)//50
            toilets    = (displaced + 19)//20
            blankets   = displaced
            powerbanks = (displaced + 9)//10

            lines.append(
                f"{city:<15} | {pop_cap:>9,} | {displaced:>9,} | {tents:>5,} | {water_l:>8,} | "
                f"{calories:>14,} | {medkits:>7,} | {toilets:>7,} | {blankets:>8,} | {powerbanks:>9,}"
            )

        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "\n".join(lines))

# =========================== NÜFUS DÜZENLEYİCİ ===========================
class PopEditor:
    """Şehir nüfus üst limitlerini (PopCap) düzenle — default: 2024 nüfusları."""
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("👥 Nüfus Düzenleyici (PopCap)")
        self.top.geometry("560x640")
        self.top.configure(bg="#0a0a0a")

        hdr = tk.Label(self.top, text="Şehir Nüfus Üst Limitleri (PopCap) — Enter ile kaydet",
                       fg="#ffd6d6", bg="#0a0a0a", font=("Segoe UI", 11, "bold"))
        hdr.pack(anchor="w", padx=12, pady=8)

        self.listf = tk.Frame(self.top, bg="#0a0a0a"); self.listf.pack(fill="both", expand=True, padx=12, pady=8)

        canvas = tk.Canvas(self.listf, bg="#0a0a0a", highlightthickness=0)
        sb = tk.Scrollbar(self.listf, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg="#0a0a0a")
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

        self.vars = {}
        for city in sorted(TURKEY_81):
            f = tk.Frame(self.inner, bg="#0a0a0a"); f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{city:<15}", fg="#ffd6d6", bg="#0a0a0a", width=16, anchor="w",
                     font=("Consolas", 10)).pack(side="left")
            var = tk.IntVar(value=CITY_POP_CAP.get(city, DEFAULT_POP_GUESS))
            e = ttk.Entry(f, textvariable=var, width=14); e.pack(side="left", padx=6)
            e.bind("<Return>", lambda _e, c=city, v=var: self.save_city(c, v))
            self.vars[city] = var

        tk.Button(self.top, text="Hepsini Kaydet", command=self.save_all,
                  bg="#111", fg="#ff2a2a", activebackground="#1c1c1c",
                  activeforeground="#ffd6d6", relief="flat").pack(pady=10)

    def save_city(self, city, var):
        try:
            val = max(0, int(var.get()))
            CITY_POP_CAP[city] = val
        except:
            pass

    def save_all(self):
        for c, v in self.vars.items():
            self.save_city(c, v)
        messagebox.showinfo("Kaydedildi", "Tüm nüfus üst limitleri (PopCap) güncellendi.")

# =========================== YOĞUNLUK DÜZENLEYİCİ ===========================
class DensityEditor:
    """Her şehrin yoğunluğunu (/km²) düzenle — default: verdiğin 2024 yoğunlukları."""
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("📈 Yoğunluk Düzenleyici (/km²)")
        self.top.geometry("560x640")
        self.top.configure(bg="#0a0a0a")

        hdr = tk.Label(self.top, text="Şehir Yoğunlukları (/km²) — Enter ile kaydet",
                       fg="#ffd6d6", bg="#0a0a0a", font=("Segoe UI", 11, "bold"))
        hdr.pack(anchor="w", padx=12, pady=8)

        self.listf = tk.Frame(self.top, bg="#0a0a0a"); self.listf.pack(fill="both", expand=True, padx=12, pady=8)

        canvas = tk.Canvas(self.listf, bg="#0a0a0a", highlightthickness=0)
        sb = tk.Scrollbar(self.listf, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg="#0a0a0a")
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

        self.vars = {}
        for city in sorted(TURKEY_81):
            f = tk.Frame(self.inner, bg="#0a0a0a"); f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{city:<15}", fg="#ffd6d6", bg="#0a0a0a", width=16, anchor="w",
                     font=("Consolas", 10)).pack(side="left")
            var = tk.DoubleVar(value=CITY_DENSITIES_81.get(city, 60.0))
            e = ttk.Entry(f, textvariable=var, width=14); e.pack(side="left", padx=6)
            e.bind("<Return>", lambda _e, c=city, v=var: self.save_city(c, v))
            self.vars[city] = var

        tk.Button(self.top, text="Hepsini Kaydet", command=self.save_all,
                  bg="#111", fg="#ff2a2a", activebackground="#1c1c1c",
                  activeforeground="#ffd6d6", relief="flat").pack(pady=10)

    def save_city(self, city, var):
        try:
            val = max(0.1, float(var.get()))
            CITY_DENSITIES_81[city] = val
        except:
            pass

    def save_all(self):
        for c, v in self.vars.items():
            self.save_city(c, v)
        messagebox.showinfo("Kaydedildi", "Tüm yoğunluklar güncellendi.")

# =============================== MAIN ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = MeteorCitySim(root)
    root.mainloop()
