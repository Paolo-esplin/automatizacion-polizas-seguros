# ======================================
# 1. IMPORTACIONES
# ======================================
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import re
import os

# ======================================
# 2. CONFIGURACIÓN OCR
# ======================================

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta a tessdata
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Ruta a Poppler
POPPLER_PATH = r"C:\poppler\Library\bin"

# Configuración OCR (optimizada)
OCR_CONFIG = r"--oem 3 --psm 6"

# ======================================
# 3. FUNCIONES DE LIMPIEZA Y NORMALIZACIÓN
# ======================================
def clean_name(raw_name):
    if not raw_name:
        return "NO ENCONTRADO"

    name = raw_name.upper()
    name = re.sub(r"\d+", "", name)  # quitar números
    name = re.sub(r"\b([A-Z])\s+([A-Z]{2,})\b", r"\1\2", name)  # J ESUS → JESUS
    name = re.sub(r"\s+", " ", name)
    return name.strip()

def normalize_text(text):
    text = text.upper()
    text = re.sub(r"[^A-Z ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def name_to_set(name):
    """
    Convierte un nombre completo en un set de palabras,
    ignorando el orden (nombres vs apellidos).
    """
    normalized = normalize_text(name)
    return set(normalized.split())

# ======================================
# 4. LEER BASE DE DNIs (UNA SOLA VEZ)
# ======================================
df_dni = pd.read_excel("base_dni.xlsx")
df_dni["DNI"] = df_dni["DNI"].astype(str)
df_dni["NOMBRE_COMPLETO"] = df_dni["NOMBRE_COMPLETO"].str.upper()

# ======================================
# 5. LISTA PARA RESULTADOS (IMPORTANTE)
# ======================================
resultados = []

# ======================================
# 6. PROCESAR TODAS LAS PÓLIZAS
# ======================================
for archivo in os.listdir("polizas"):

    if not archivo.lower().endswith(".pdf"):
        continue

    print(f"Procesando: {archivo}")
    ruta_pdf = os.path.join("polizas", archivo)

    # ======================================
    # 7. OCR DE LA PÓLIZA (PDF)
    # ======================================
    pages = convert_from_path(
        ruta_pdf,
        dpi=200,
        poppler_path=POPPLER_PATH
    )

    full_text = ""

    for page in pages[:1]:
        text = pytesseract.image_to_string(
            page,
            lang="spa",
            config=OCR_CONFIG
        )
        full_text += text.replace("\x0c", "") + "\n"

    # ======================================
    # 8. PREPARAR TEXTO
    # ======================================
    policy_text = full_text.upper()
    lines = [line.strip() for line in policy_text.split("\n") if line.strip()]

    # ======================================
    # 9. EXTRAER DATOS DE LA PÓLIZA
    # ======================================

    # --- DNI ---
    dni = "NO ENCONTRADO"
    for line in lines:
        match = re.search(r"\b[0-9]{8}\b", line)
        if match:
            dni = match.group()
            break

    # --- NÚMERO DE PÓLIZA ---
    policy_number = "NO ENCONTRADO"
    for line in lines:
        match = re.search(r"P[ÓO]LIZA\s+([0-9]+)\s*-\s*([0-9]+)", line)
        if match:
            policy_number = f"{match.group(1)}-{match.group(2)}"
            break

    # --- NOMBRE ---
    raw_name = "NO ENCONTRADO"
    for i, line in enumerate(lines):
        if "CONTRATANTE" in line and i > 0:
            raw_name = lines[i - 1]
            break

    name = clean_name(raw_name)

    # --- DIRECCIÓN ---
    address = "NO ENCONTRADO"
    for line in lines:
        if any(word in line for word in ["AV.", "AVENIDA", "JR.", "JIRÓN", "CA.","CALLE"]):
            address = line
            break

    # ======================================
    # VALIDACIÓN CONTRA LA BASE
    # ======================================
    registro = df_dni[df_dni["DNI"] == dni]

    if registro.empty:
        estado = "DNI NO EXISTE"
        nombre_base = ""
        dni_base = ""
    else:
        nombre_base = registro.iloc[0]["NOMBRE_COMPLETO"]
        dni_base = registro.iloc[0]["DNI"]

        if name_to_set(name) == name_to_set(nombre_base):
            estado = "COINCIDE"
        else:
            estado = "NO COINCIDE"

    # ======================================
    # GUARDAR RESULTADO
    # ======================================
    resultados.append({
        "archivo_pdf": archivo,
        "dni_poliza": dni,
        "dni_base": dni_base,
        "nombre_poliza": name,
        "nombre_base": nombre_base,
        "poliza": policy_number,
        "direccion": address,
        "estado": estado
    })

# ======================================
# 10. EXPORTAR RESULTADOS
# ======================================
df_resultados = pd.DataFrame(resultados)
df_resultados.to_excel("resultados_validacion.xlsx", index=False)

print("\n✅ PROCESO FINALIZADO")
print("Archivo generado: resultados_validacion.xlsx")  
