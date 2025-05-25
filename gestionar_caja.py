import tkinter as tk
from tkinter import NSEW, EW, W, E
from ttkthemes import ThemedStyle
from tkinter import ttk
from tkfontawesome import icon_to_image

class CajaUI:
    def __init__(self, master, db_config=None):
        self.ventana = master
        self.ventana.title("Gestión de Caja - Lavandería")
        self.ventana.geometry("1000x650")
        self.ventana.minsize(900, 600)
        # Centrar ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() - self.ventana.winfo_width()) // 2
        y = (self.ventana.winfo_screenheight() - self.ventana.winfo_height()) // 3
        self.ventana.geometry(f"+{x}+{y}")

        self._configurar_tema()
        self._configurar_layout_ventana()
        self.construir_interfaz()

    def _configurar_tema(self):
        style = ThemedStyle(self.ventana)
        style.set_theme("arc")
        # Colores y tipografía base
        style.configure("TFrame", background="#f0f2f5")
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#2c3e50", background="#f0f2f5")
        style.configure("State.TFrame", background="#ffffff", relief="ridge", borderwidth=1)
        style.configure("State.TLabel", font=("Segoe UI", 12), background="#ffffff", foreground="#34495e")
        # Botones Accent
        style.configure(
            "Accent.TButton",
            background="#3498db",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            padding=10,
            borderwidth=0
        )
        style.map(
            "Accent.TButton",
            background=[('active', '#5dade2'), ('pressed', '#2980b9')],
            foreground=[('disabled', 'gray'), ('!disabled', 'white')]
        )
        # Notebook
        style.configure("TNotebook", background="#f0f2f5", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 12), padding=(12, 8))
        # Treeview
        style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
            rowheight=28
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#e0e0e0"
        )

    def _configurar_layout_ventana(self):
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(0, weight=1)

    def construir_interfaz(self):
        # Contenedor principal
        self.frame_principal = ttk.Frame(self.ventana, padding=25, style="TFrame")
        self.frame_principal.grid(sticky=NSEW)
        self.frame_principal.columnconfigure(0, weight=1)

        # Header
        lbl_titulo = ttk.Label(self.frame_principal, text="GESTIÓN DE CAJA", style="Header.TLabel")
        lbl_titulo.grid(row=0, column=0, pady=(0, 15))
        ttk.Separator(self.frame_principal, orient="horizontal").grid(row=1, column=0, sticky=EW, pady=(0, 20))

        # Estado caja
        self.frame_estado = ttk.Frame(self.frame_principal, style="State.TFrame")
        self.frame_estado.grid(row=2, column=0, sticky=EW, padx=5, pady=(0, 20))
        for i in range(3): self.frame_estado.columnconfigure(i, weight=1)
        estados = [
            ("Fecha: --/--/----", 0, 0, W),
            ("Hora apertura: --:--:--", 0, 1, W),
            ("Ingresos: $0.00", 0, 2, E),
            ("Responsable: --", 1, 0, W),
            ("Egresos: $0.00", 1, 1, W),
            ("Saldo: $0.00", 1, 2, E)
        ]
        for text, r, c, stick in estados:
            ttk.Label(self.frame_estado, text=text, style="State.TLabel").grid(row=r, column=c, sticky=stick, padx=15, pady=8)

        # Notebook
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.grid(row=3, column=0, sticky=NSEW)
        self.frame_principal.rowconfigure(3, weight=1)

        # Pestañas
        self.tab_operaciones = ttk.Frame(self.notebook)
        self.tab_movimientos = ttk.Frame(self.notebook)
        self.tab_cortes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_operaciones, text="Operaciones de Caja")
        self.notebook.add(self.tab_movimientos, text="Movimientos")
        self.notebook.add(self.tab_cortes, text="Cortes de Caja")

        # Operaciones: botones
        acciones = [
            ("money-bill-wave", "Nueva Venta", self.nueva_venta),
            ("plus-circle", "Otro Ingreso", self.otro_ingreso),
            ("minus-circle", "Registrar Egreso", self.registrar_egreso),
            ("clipboard-list", "Arqueo de Caja", self.arqueo_caja),
            ("chart-bar", "Resumen Ventas", self.resumen_ventas),
            ("lock", "Cerrar Caja", self.cerrar_caja)
        ]
        for idx, (icon_name, text, cmd) in enumerate(acciones):
            img = icon_to_image(icon_name, scale_to_height=28)
            btn = ttk.Button(
                self.tab_operaciones,
                text=f"  {text}",
                image=img,
                compound="left",
                command=cmd,
                style="Accent.TButton",
                cursor="hand2"
            )
            btn.image = img
            btn.grid(row=idx//3, column=idx%3, padx=15, pady=15, sticky=EW)
            self.tab_operaciones.columnconfigure(idx%3, weight=1)

        # Movimientos: tabla
        self.configurar_tab_movimientos()
        # Cortes: tabla
        self.configurar_tab_cortes()

        # Botón Volver
        ttk.Button(
            self.frame_principal,
            text="Volver",
            command=self.ventana.destroy,
            style="Accent.TButton",
            cursor="hand2"
        ).grid(row=4, column=0, sticky=E, pady=25)

    def configurar_tab_movimientos(self):
        self.tab_movimientos.columnconfigure(0, weight=1)
        cols = ("ID", "Tipo", "Monto", "Descripción", "Fecha", "Saldo")
        tree = ttk.Treeview(
            self.tab_movimientos,
            columns=cols,
            show="headings",
            style="Custom.Treeview"
        )
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor=W)
        tree.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
        sb = ttk.Scrollbar(self.tab_movimientos, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    def configurar_tab_cortes(self):
        self.tab_cortes.columnconfigure(0, weight=1)
        cols = ("ID Corte", "Fecha Corte", "Ingresos", "Egresos", "Saldo Final")
        tree = ttk.Treeview(
            self.tab_cortes,
            columns=cols,
            show="headings",
            style="Custom.Treeview"
        )
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor=W)
        tree.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
        sb = ttk.Scrollbar(self.tab_cortes, orient="vertical", command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    # Placeholders
    def nueva_venta(self): pass
    def otro_ingreso(self): pass
    def registrar_egreso(self): pass
    def arqueo_caja(self): pass
    def resumen_ventas(self): pass
    def cerrar_caja(self): pass

if __name__ == "__main__":
    root = tk.Tk()
    app = CajaUI(root)
    root.mainloop()
