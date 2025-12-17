# Automatización de Validación de Pólizas de Seguros

Este proyecto implementa una automatización en Python para validar pólizas de seguros a partir de documentos PDF, comparando la información extraída mediante OCR contra una base de datos estructurada (Excel).

El objetivo principal es reducir el tiempo operativo, minimizar errores manuales y optimizar procesos de validación documentaria en el sector seguros.

---

## 🧠 Problema que resuelve

En muchos procesos operativos de aseguradoras, la validación de pólizas se realiza manualmente:

- Revisión visual de documentos PDF
- Comparación manual de nombres y DNI
- Validación contra bases de datos internas
- Registro manual de resultados

Este proceso es lento, propenso a errores y difícil de escalar cuando se manejan grandes volúmenes de documentos.

Este proyecto automatiza completamente ese flujo.

---

## ⚙️ ¿Qué hace la automatización?

El sistema realiza las siguientes acciones:

1. Procesa múltiples pólizas en formato PDF (batch processing)
2. Extrae información clave mediante OCR:
   - DNI del contratante
   - Nombre completo
   - Número de póliza
   - Dirección
3. Normaliza los datos extraídos para corregir errores de OCR
4. Valida el DNI contra una base de datos en Excel
5. Compara nombres ignorando el orden (nombres vs apellidos)
6. Determina el estado de validación:
   - **COINCIDE**
   - **NO COINCIDE**
   - **DNI NO EXISTE**
7. Genera un reporte consolidado en Excel con el resultado de cada póliza

---

## 🛠️ Tecnologías utilizadas

- Python  
- Tesseract OCR  
- pdf2image  
- Pandas  
- Expresiones regulares (Regex)  

---

## 📁 Estructura del proyecto

```text
automatizacion-polizas-seguros/
│
├─ polizas/                     # Carpeta con pólizas en PDF
│   ├─ poliza 1.pdf
│   ├─ poliza 2.pdf
│   └─ poliza 3.pdf
│
├─ base_dni.xlsx                # Base de datos de DNIs y nombres
├─ read_policy_batch.py         # Script principal
├─ requirements.txt             # Dependencias del proyecto
