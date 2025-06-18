
import requests
import time
import schedule
from git import Repo

# CONFIGURACIÓN
ARCHIVO_M3U8 = "output/IPTV.m3u8"
RUTA_REPO = "."
TIEMPO_MINUTOS = 5
CANAL_OBJETIVO = "TC MI CANAL 10"

def es_url_valida(url):
    try:
        r = requests.head(url, timeout=10)
        return r.status_code == 200
    except:
        return False

def regenerar_tc_micanal():
    # TODO: Lógica para obtener nuevo enlace .m3u8 de TC Mi Canal
    # Por ejemplo, scraping o API.
    print("Intentando regenerar TC Mi Canal desde fuente...")
    return None

def verificar_y_actualizar():
    print("Verificando estado de canales...")
    with open(ARCHIVO_M3U8, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    cambios = False
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        if linea.startswith("#EXTINF"):
            nombre_canal = linea.split(",", 1)[-1].strip().upper()
            url = lineas[i + 1].strip()
            if nombre_canal == CANAL_OBJETIVO:
                if not es_url_valida(url):
                    print(f"[X] {nombre_canal} está caído: {url}")
                    nuevo_link = regenerar_tc_micanal()
                    if nuevo_link:
                        nuevas_lineas.append(lineas[i])
                        nuevas_lineas.append(nuevo_link + "\n")
                        cambios = True
                        i += 2
                        continue
            nuevas_lineas.append(lineas[i])
            nuevas_lineas.append(lineas[i + 1])
            i += 2
        else:
            nuevas_lineas.append(lineas[i])
            i += 1

    if nuevas_lineas != lineas:
        with open(ARCHIVO_M3U8, "w", encoding="utf-8") as f:
            f.writelines(nuevas_lineas)
        print("Archivo actualizado. Subiendo a GitHub...")
        repo = Repo(RUTA_REPO)
        repo.git.add(ARCHIVO_M3U8)
        repo.index.commit("Actualización automática de archivo M3U8")
        origin = repo.remote(name='origin')
        origin.push()
    else:
        print("No hubo cambios.\n")

# Programar cada N minutos
schedule.every(TIEMPO_MINUTOS).minutes.do(verificar_y_actualizar)

print(f"Monitor activo. Verificando cada {TIEMPO_MINUTOS} minutos...\n")
verificar_y_actualizar()

while True:
    schedule.run_pending()
    time.sleep(1)
