import random
import time
import tkinter as tk
from tkinter import messagebox, ttk

# --- CATÀLEG I IMATGES VISUALS DE COMPONENTS ---
DIBUIXOS_PECES = {
    "Placa Base": "🟫 [🔲 Motherboard]",
    "Processador (CPU)": "🔲 [🔳 CPU Intel/AMD]",
    "Memòria RAM": "🟩 [▮▮ RAM DDR4/DDR5]",
    "Font d'alimentació": "⬛ [🔌 Font ATX 650W]",
    "Disc SSD SATA": "💾 [📼 SSD SATA 2.5\"]",
    "Disc M.2 NVMe": "⚡ [💳 NVMe PCIe 4.0]",
    "Tarjeta Gràfica (GPU)": "🎮 [📼 RTX GPU 3-Fan]",
    "Dissipador RGB": "🌀 [💨 Dissipador Aire]",
    "Refrigeració Líquida": "💧 [🌊 Watercooling 240mm]",
    "Caixa Bàsica": "📦 [🖥️ Caixa Micro-ATX]",
    "Caixa Gaming": "✨ [🖥️ Caixa RGB Glass]",
}

CATALEG_PECES = list(DIBUIXOS_PECES.keys())

TASQUES_TEMPS = {
    "Neteja i Preparació": {"temps": 3, "icona": "🧼"},
    "Instal·lació de SO": {"temps": 6, "icona": "💿"},
    "Actualització Drivers/BIOS": {"temps": 8, "icona": "🔄"},
    "Test de Stress / MemTest": {"temps": 12, "icona": "🔥"},
}

TIPUS_COMPONENTS = {
    "PC Oficina": {
        "punts": 100,
        "peces": [
            "Placa Base",
            "Processador (CPU)",
            "Memòria RAM",
            "Font d'alimentació",
            "Disc SSD SATA",
            "Caixa Bàsica",
        ],
        "fases_temps": ["Neteja i Preparació", "Instal·lació de SO"],
    },
    "PC Gaming": {
        "punts": 200,
        "peces": [
            "Placa Base",
            "Processador (CPU)",
            "Memòria RAM",
            "Font d'alimentació",
            "Tarjeta Gràfica (GPU)",
            "Dissipador RGB",
            "Disc M.2 NVMe",
            "Caixa Gaming",
        ],
        "fases_temps": [
            "Neteja i Preparació",
            "Instal·lació de SO",
            "Actualització Drivers/BIOS",
        ],
    },
    "Workstation Server": {
        "punts": 300,
        "peces": [
            "Placa Base",
            "Processador (CPU)",
            "Memòria RAM",
            "Font d'alimentació",
            "Refrigeració Líquida",
            "Disc M.2 NVMe",
        ],
        "fases_temps": [
            "Neteja i Preparació",
            "Instal·lació de SO",
            "Actualització Drivers/BIOS",
            "Test de Stress / MemTest",
        ],
    },
}


class TargetaTasca:

    def __init__(self, id_comanda, tipus, dades):
        self.id_comanda = id_comanda
        self.tipus = tipus
        self.punts = dades["punts"]
        self.peces_requerides = list(dades["peces"])
        self.peces_recollides = []

        self.fases_requerides = list(dades["fases_temps"])
        self.fases_estat = {fase: "Pendent" for fase in self.fases_requerides}
        self.fase_activa = None
        self.temps_fase_restant = 0

        self.estat = "Pendent"


class PCOvercookedAppV52:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "🎮 PC Rush V5.2: Comandes Automàtiques i Selecció Paral·lela"
        )
        self.root.geometry("1300x940")

        self.tasques = []
        self.comanda_count = 1
        self.tasca_seleccionada = None

        # Mètrics del joc
        self.temps_restant_partida = 300  # 5 minuts
        self.partida_activa = False
        self.puntuacio = 0
        self.errors_comessos = 0
        self.comandes_lliurades = 0

        # Control del temporitzador de generació automàtica
        self.temps_fins_proxima_comanda = 0

        self.setup_ui()

    def setup_ui(self):
        # 1. PANELL SUPERIOR
        top_panel = tk.Frame(self.root, bg="#2d3436", padx=10, pady=10)
        top_panel.pack(fill=tk.X)

        self.btn_iniciar = tk.Button(
            top_panel,
            text="🚀 Iniciar Partida (5 min)",
            font=("Arial", 11, "bold"),
            bg="#00b894",
            fg="white",
            command=self.iniciar_partida,
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)

        self.btn_nova_comanda = tk.Button(
            top_panel,
            text="📥 Forçar Comanda Extra",
            font=("Arial", 10, "bold"),
            bg="#0984e3",
            fg="white",
            state=tk.DISABLED,
            command=self.generar_comanda,
        )
        self.btn_nova_comanda.pack(side=tk.LEFT, padx=5)

        self.lbl_timer = tk.Label(
            top_panel,
            text="⏱️ Temps: 05:00",
            font=("Arial", 14, "bold"),
            bg="#2d3436",
            fg="#fdcb6e",
        )
        self.lbl_timer.pack(side=tk.LEFT, padx=20)

        self.lbl_score = tk.Label(
            top_panel,
            text="🏆 Punts: 0 | ❌ Errors: 0",
            font=("Arial", 12, "bold"),
            bg="#2d3436",
            fg="white",
        )
        self.lbl_score.pack(side=tk.RIGHT, padx=10)

        # 2. ÀREA KANBAN (3 Columnes)
        kanban_frame = tk.Frame(self.root, bg="#dfe6e9")
        kanban_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        kanban_frame.columnconfigure(0, weight=1)
        kanban_frame.columnconfigure(1, weight=1)
        kanban_frame.columnconfigure(2, weight=1)
        kanban_frame.rowconfigure(0, weight=1)

        self.col_pendent = tk.LabelFrame(
            kanban_frame,
            text=" 🔴 Pendents (Arriben Auto) ",
            font=("Arial", 11, "bold"),
            bg="#f5f6fa",
        )
        self.col_pendent.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        self.col_proces = tk.LabelFrame(
            kanban_frame,
            text=" 🟡 En Procés (Clica per seleccionar) ",
            font=("Arial", 11, "bold"),
            bg="#f5f6fa",
        )
        self.col_proces.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        self.col_acabat = tk.LabelFrame(
            kanban_frame, text=" 🟢 Completats ", font=("Arial", 11, "bold"), bg="#f5f6fa"
        )
        self.col_acabat.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)

        self.frame_pendent = self.crear_scrollable_frame(self.col_pendent)
        self.frame_proces = self.crear_scrollable_frame(self.col_proces)
        self.frame_acabat = self.crear_scrollable_frame(self.col_acabat)

        # 3. PANELL INFERIOR: MAGATZEM VISUAL
        magatzem_frame = tk.LabelFrame(
            self.root,
            text=" 📦 Magatzem Visual de Components (S'afegeixen al PC SELECCIONAT) ",
            font=("Arial", 10, "bold"),
            bg="#b2bec3",
            padx=10,
            pady=5,
        )
        magatzem_frame.pack(fill=tk.X, padx=10, pady=5)

        row1 = tk.Frame(magatzem_frame, bg="#b2bec3")
        row1.pack(fill=tk.X, pady=2)
        row2 = tk.Frame(magatzem_frame, bg="#b2bec3")
        row2.pack(fill=tk.X, pady=2)

        for i, peca in enumerate(CATALEG_PECES):
            parent_row = row1 if i < 6 else row2
            text_visual = DIBUIXOS_PECES[peca]
            btn = tk.Button(
                parent_row,
                text=f"{text_visual}",
                font=("Arial", 8, "bold"),
                bg="#0984e3",
                fg="white",
                relief="raised",
                command=lambda p=peca: self.afegir_peca_a_tasca(p),
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    def crear_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, bg="#f5f6fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f5f6fa")

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scroll_frame

    def iniciar_partida(self):
        self.partida_activa = True
        self.temps_restant_partida = 300
        self.puntuacio = 0
        self.errors_comessos = 0
        self.comandes_lliurades = 0
        self.tasques = []
        self.comanda_count = 1
        self.tasca_seleccionada = None
        self.temps_fins_proxima_comanda = random.randint(8, 14)

        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_nova_comanda.config(state=tk.NORMAL)

        # Generem 2 comandes inicials
        self.generar_comanda()
        self.generar_comanda()

        self.actualitzar_marcador()
        self.update_loop()

    def generar_comanda(self):
        if not self.partida_activa:
            return

        # Limitem a un màxim de 6 comandes no finalitzades alhora
        actives = [t for t in self.tasques if t.estat != "Acabat"]
        if len(actives) >= 6:
            return

        tipus = random.choice(list(TIPUS_COMPONENTS.keys()))
        dades = TIPUS_COMPONENTS[tipus]

        tasca = TargetaTasca(self.comanda_count, tipus, dades)
        self.tasques.append(tasca)
        self.comanda_count += 1

        self.renderitzar_tauler()

    def seleccionar_tasca(self, tasca):
        if tasca.estat == "En Procés":
            self.tasca_seleccionada = tasca
            self.renderitzar_tauler()

    def afegir_peca_a_tasca(self, peca):
        if not self.partida_activa:
            return

        tasques_en_proces = [t for t in self.tasques if t.estat == "En Procés"]

        if not tasques_en_proces:
            messagebox.showwarning("Atenció", "No hi ha cap comanda 'En Procés'!")
            return

        if (
            self.tasca_seleccionada is None
            or self.tasca_seleccionada.estat != "En Procés"
        ):
            self.tasca_seleccionada = tasques_en_proces[0]

        tasca = self.tasca_seleccionada

        if peca in tasca.peces_requerides:
            if peca not in tasca.peces_recollides:
                tasca.peces_recollides.append(peca)
                self.renderitzar_tauler()
            else:
                messagebox.showinfo(
                    "Info", f"Ja tens la peça '{peca}' col·locada al PC #{tasca.id_comanda}!"
                )
        else:
            self.errors_comessos += 1
            self.puntuacio = max(0, self.puntuacio - 15)
            self.actualitzar_marcador()
            messagebox.showerror(
                "Error Hardware (-15 pts)",
                f"❌ La peça '{peca}' no és per al PC #{tasca.id_comanda} ({tasca.tipus})!",
            )

    def moure_estat(self, tasca, nou_estat):
        if not self.partida_activa:
            return

        if nou_estat == "En Procés":
            tasca.estat = nou_estat
            self.tasca_seleccionada = tasca

        elif nou_estat == "Acabat":
            peces_faltants = set(tasca.peces_requerides) - set(tasca.peces_recollides)
            if peces_faltants:
                self.errors_comessos += 1
                self.puntuacio = max(0, self.puntuacio - 20)
                self.actualitzar_marcador()
                messagebox.showerror(
                    "Error", f"❌ Incomplet! Falten peces: {', '.join(peces_faltants)}"
                )
                return

            for fase, estat in tasca.fases_estat.items():
                if estat != "Fet":
                    messagebox.showwarning(
                        "Software Pendent", f"⚠️ Falta completar la fase: {fase}!"
                    )
                    return

            tasca.estat = nou_estat
            self.puntuacio += tasca.punts
            self.comandes_lliurades += 1

            if self.tasca_seleccionada == tasca:
                self.tasca_seleccionada = None

            self.actualitzar_marcador()

        self.renderitzar_tauler()

    def iniciar_fase_temps(self, tasca, fase):
        if not self.partida_activa:
            return

        peces_faltants = set(tasca.peces_requerides) - set(tasca.peces_recollides)
        if peces_faltants:
            self.errors_comessos += 1
            self.puntuacio = max(0, self.puntuacio - 25)
            self.actualitzar_marcador()
            messagebox.showerror(
                "🛑 Hardware Incomplet! (-25 pts)",
                f"No pots encendre el PC #{tasca.id_comanda} ni iniciar '{fase}'!\n"
                f"Peces faltants: {', '.join(peces_faltants)}",
            )
            return

        if tasca.fase_activa is not None:
            messagebox.showwarning(
                "Atenció", "Ja hi ha un procés executant-se en aquest PC!"
            )
            return

        tasca.fase_activa = fase
        tasca.fases_estat[fase] = "En Curs"
        tasca.temps_fase_restant = TASQUES_TEMPS[fase]["temps"]
        self.renderitzar_tauler()

    def solucionar_error_test(self, tasca, fase):
        tasca.fases_estat[fase] = "Pendent"
        self.renderitzar_tauler()

    def actualitzar_marcador(self):
        self.lbl_score.config(
            text=f"🏆 Punts: {self.puntuacio} | ❌ Errors: {self.errors_comessos}"
        )

    def finalitzar_partida(self):
        self.partida_activa = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_nova_comanda.config(state=tk.DISABLED)

        total_accions = self.comandes_lliurades + self.errors_comessos
        eficiencia = (
            round((self.comandes_lliurades / total_accions) * 100, 1)
            if total_accions > 0
            else 0.0
        )

        if eficiencia >= 85 and self.puntuacio >= 800:
            rang = "🥇 Master System Builder (Excel·lent)"
        elif eficiencia >= 70 and self.puntuacio >= 400:
            rang = "🥈 Tècnic Sènior de Taller (Notable)"
        elif self.puntuacio > 0:
            rang = "🥉 Tècnic Novell / En Pràctiques (Aprovat)"
        else:
            rang = "⚠️ Requereix Repàs de Hardware"

        resum = (
            f"⏱️ TEMPS ESGOTAT!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 PCs Lliurats: {self.comandes_lliurades}\n"
            f"❌ Errors comessos: {self.errors_comessos}\n"
            f"🏆 Puntuació Final: {self.puntuacio} punts\n"
            f"📈 Eficiència del Taller: {eficiencia}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Nivell Aconseguit:\n{rang}"
        )

        messagebox.showinfo("📊 RESULTATS FINALS DE LA PARTIDA", resum)

    def update_loop(self):
        if not self.partida_activa:
            return

        # 1. Temporitzador General
        self.temps_restant_partida -= 0.5
        minuts = int(self.temps_restant_partida // 60)
        segons = int(self.temps_restant_partida % 60)
        self.lbl_timer.config(text=f"⏱️ Temps: {minuts:02d}:{segons:02d}")

        if self.temps_restant_partida <= 0:
            self.finalitzar_partida()
            return

        # 2. Control d'entrada AUTOMÀTICA de comandes
        pendents = [t for t in self.tasques if t.estat == "Pendent"]
        
        # Regla 1: Si no hi ha CAP comanda pendent, en generem una immediatament!
        if len(pendents) == 0:
            self.generar_comanda()
            self.temps_fins_proxima_comanda = random.randint(8, 14)
        else:
            # Regla 2: Generació periòdica segons el temporitzador
            self.temps_fins_proxima_comanda -= 0.5
            if self.temps_fins_proxima_comanda <= 0:
                self.generar_comanda()
                self.temps_fins_proxima_comanda = random.randint(8, 14)

        # 3. Procés de fases temporitzades de software/stress
        for tasca in self.tasques:
            if tasca.estat == "En Procés" and tasca.fase_activa is not None:
                tasca.temps_fase_restant -= 0.5

                if tasca.temps_fase_restant <= 0:
                    fase_acabada = tasca.fase_activa
                    tasca.fase_activa = None

                    if (
                        fase_acabada == "Test de Stress / MemTest"
                        and random.random() < 0.15
                    ):
                        tasca.fases_estat[fase_acabada] = "Error"
                    else:
                        tasca.fases_estat[fase_acabada] = "Fet"

                    self.renderitzar_tauler()
                else:
                    if (
                        hasattr(tasca, "widget_timer")
                        and tasca.widget_timer.winfo_exists()
                    ):
                        tasca.widget_timer.config(
                            text=f"⏳ {tasca.fase_activa}: {int(tasca.temps_fase_restant)}s restants"
                        )

        self.root.after(500, self.update_loop)

    def renderitzar_tauler(self):
        for widget in self.frame_pendent.winfo_children():
            widget.destroy()
        for widget in self.frame_proces.winfo_children():
            widget.destroy()
        for widget in self.frame_acabat.winfo_children():
            widget.destroy()

        tasques_en_proces = [t for t in self.tasques if t.estat == "En Procés"]
        if tasques_en_proces and (
            self.tasca_seleccionada is None
            or self.tasca_seleccionada not in tasques_en_proces
        ):
            self.tasca_seleccionada = tasques_en_proces[0]

        for tasca in self.tasques:
            if tasca.estat == "Pendent":
                parent = self.frame_pendent
            elif tasca.estat == "En Procés":
                parent = self.frame_proces
            else:
                parent = self.frame_acabat

            self.crear_targeta_widget(parent, tasca)

    def crear_targeta_widget(self, parent, tasca):
        es_seleccionat = (
            tasca.estat == "En Procés" and tasca == self.tasca_seleccionada
        )

        color_fons = (
            "#ffffff"
            if tasca.tipus == "PC Oficina"
            else ("#fff3cd" if tasca.tipus == "PC Gaming" else "#f8d7da")
        )
        bd_size = 4 if es_seleccionat else 1
        relief_type = "solid" if es_seleccionat else "groove"

        card = tk.Frame(
            parent, bg=color_fons, bd=bd_size, relief=relief_type, padx=8, pady=8
        )
        card.pack(fill=tk.X, padx=5, pady=5, expand=True)

        card.bind("<Button-1>", lambda e, t=tasca: self.seleccionar_tasca(t))

        header_text = f"Comanda #{tasca.id_comanda} - {tasca.tipus} (+{tasca.punts} pts)"
        if es_seleccionat:
            header_text += " 👉 [ACTIU]"

        lbl_head = tk.Label(
            card,
            text=header_text,
            font=("Arial", 10, "bold"),
            bg=color_fons,
            fg="#000000" if not es_seleccionat else "#d63031",
        )
        lbl_head.pack(anchor="w")
        lbl_head.bind("<Button-1>", lambda e, t=tasca: self.seleccionar_tasca(t))

        # Components Hardware
        tk.Label(
            card, text="Components Hardware:", font=("Arial", 8, "bold"), bg=color_fons
        ).pack(anchor="w", pady=(2, 0))

        for peca in tasca.peces_requerides:
            icona = "✅" if peca in tasca.peces_recollides else "❌ (Falta)"
            color = "green" if peca in tasca.peces_recollides else "#d63031"
            text_dibuix = DIBUIXOS_PECES[peca]

            lbl_p = tk.Label(
                card,
                text=f"{icona} {text_dibuix}",
                font=("Arial", 8),
                fg=color,
                bg=color_fons,
            )
            lbl_p.pack(anchor="w")
            lbl_p.bind("<Button-1>", lambda e, t=tasca: self.seleccionar_tasca(t))

        # Software
        if tasca.estat == "En Procés":
            tk.Label(
                card, text="---------------------------", bg=color_fons, fg="#888"
            ).pack()

            hw_complet = set(tasca.peces_requerides) == set(tasca.peces_recollides)
            estat_hw_txt = (
                "🟢 Hardware a punt" if hw_complet else "🔴 Falten peces!"
            )
            tk.Label(
                card,
                text=f"Estat Hardware: {estat_hw_txt}",
                font=("Arial", 8, "italic"),
                bg=color_fons,
            ).pack(anchor="w")

            for fase in tasca.fases_requerides:
                estat_fase = tasca.fases_estat[fase]
                icona = TASQUES_TEMPS[fase]["icona"]

                if estat_fase == "Pendent":
                    btn = tk.Button(
                        card,
                        text=f"{icona} Executar {fase} ({TASQUES_TEMPS[fase]['temps']}s)",
                        font=("Arial", 7, "bold"),
                        bg="#0984e3" if hw_complet else "#b2bec3",
                        fg="white",
                        command=lambda t=tasca, f=fase: self.iniciar_fase_temps(t, f),
                    )
                    btn.pack(fill=tk.X, pady=2)

                elif estat_fase == "En Curs":
                    lbl = tk.Label(
                        card,
                        text=f"⏳ {fase}: {int(tasca.temps_fase_restant)}s restants",
                        font=("Arial", 8, "bold"),
                        fg="#d63031",
                        bg=color_fons,
                    )
                    lbl.pack(pady=2)
                    tasca.widget_timer = lbl

                elif estat_fase == "Fet":
                    tk.Label(
                        card,
                        text=f"✅ {fase} OK!",
                        font=("Arial", 8, "bold"),
                        fg="#27ae60",
                        bg=color_fons,
                    ).pack(anchor="w")

                elif estat_fase == "Error":
                    btn_err = tk.Button(
                        card,
                        text=f"💥 ERROR EN {fase}! (Reajustar)",
                        font=("Arial", 8, "bold"),
                        bg="#d63031",
                        fg="white",
                        command=lambda t=tasca, f=fase: self.solucionar_error_test(
                            t, f
                        ),
                    )
                    btn_err.pack(fill=tk.X, pady=2)

        # Botons Kanban
        btn_frame = tk.Frame(card, bg=color_fons)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        if tasca.estat == "Pendent":
            tk.Button(
                btn_frame,
                text="Començar Muntatge ➔",
                bg="#e17055",
                fg="white",
                font=("Arial", 8, "bold"),
                command=lambda t=tasca: self.moure_estat(t, "En Procés"),
            ).pack(fill=tk.X)

        elif tasca.estat == "En Procés":
            tk.Button(
                btn_frame,
                text="Lliurar / Finalitzar ✅",
                bg="#00b894",
                fg="white",
                font=("Arial", 9, "bold"),
                command=lambda t=tasca: self.moure_estat(t, "Acabat"),
            ).pack(fill=tk.X)


if __name__ == "__main__":
    root = tk.Tk()
    app = PCOvercookedAppV52(root)
    root.mainloop()