# respaldo_automatico.py
import threading
import time
from datetime import datetime
import json
import subprocess
import os

CONFIG_FILE = "config_respaldo.json"

class RespaldoAutomatico:
    def __init__(self, callback_actualizacion=None):
        self._activo = False
        self._intervalo = 3600  # Por defecto cada hora
        self._hilo = None
        self._directorio = "respaldos"
        self._callback_actualizacion = callback_actualizacion
        self._cargar_configuracion()

    def configurar_intervalo(self, tipo):
        intervalos = {
            "Cada hora": 60,
            "Cada día": 86400,
            "Cada semana": 604800,
            "Cada mes": 2592000
        }
        self._intervalo = intervalos.get(tipo, 3600)
        self._guardar_configuracion(tipo)

    def iniciar(self):
        if self._activo and self._hilo and self._hilo.is_alive():
            print("[INFO] El respaldo automático ya está activo.")
            return
        self._activo = True
        self._hilo = threading.Thread(target=self._ejecutar_respaldo)
        self._hilo.daemon = True
        self._hilo.start()


    def detener(self):
        self._activo = False
        if self._hilo and self._hilo.is_alive():
            self._hilo.join(timeout=2)  # Aumentamos un poco el tiempo de espera

        self._hilo = None  # << IMPORTANTE: limpiar el hilo
        self._guardar_configuracion(None)



    def _ejecutar_respaldo(self):
        time.sleep(self._intervalo)  # Espera inicial
        while self._activo:
            try:
                self._generar_respaldo()
            except Exception as e:
                print(f"[ERROR] No se pudo generar el respaldo: {e}")
            time.sleep(self._intervalo)

    def _generar_respaldo(self):
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self._directorio, exist_ok=True)
        archivo_sql = os.path.join(self._directorio, f"respaldo_bd_{fecha}.sql")

        with open("config.json", "r") as f:
            config = json.load(f)

        usuario = config["user"]
        password = config["password"]
        base_datos = config["database"]

        with open(archivo_sql, "w", encoding="utf-8") as out_file:
            subprocess.run([
                "mysqldump",
                "-u", usuario,
                f"-p{password}",
                base_datos
            ], stdout=out_file, check=True)

        print(f"[INFO] Respaldo generado: {archivo_sql}")

        # Notificar a la interfaz si hay callback
        if self._callback_actualizacion:
            self._callback_actualizacion()

    def _guardar_configuracion(self, tipo_intervalo):
        data = {"intervalo": tipo_intervalo if tipo_intervalo else ""}
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    def _cargar_configuracion(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                tipo = data.get("intervalo")
                if tipo:
                    self.configurar_intervalo(tipo)
                    self.iniciar()
