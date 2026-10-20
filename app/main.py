import os
import re
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import PDF_DIR
from .pipeline import indexar_pdf
from .rag import preguntar
from .store import count

app = FastAPI(title="RAG Facturas")

APP_KEY = os.getenv("APP_KEY", "")

INDEX_HTML = Path(__file__).parent / "static" / "index.html"


def _check_key(x_app_key: str | None):
    if APP_KEY and x_app_key != APP_KEY:
        raise HTTPException(status_code=401, detail="Clave incorrecta")


class Pregunta(BaseModel):
    pregunta: str
    clave: str = ""


class SubidaRespuesta(BaseModel):
    archivo: str
    trozos: int
    error: str = ""


@app.get("/")
def inicio():
    return FileResponse(INDEX_HTML)


@app.post("/api/preguntar")
def api_preguntar(body: Pregunta, x_app_key: str | None = None):
    _check_key(body.clave or x_app_key)
    if not body.pregunta.strip():
        raise HTTPException(status_code=400, detail="Pregunta vacía")
    if count() == 0:
        raise HTTPException(status_code=400, detail="No hay facturas indexadas todavía")
    r = preguntar(body.pregunta)
    return {"respuesta": r.texto, "fuentes": sorted({f["source"] for f in r.fuentes})}


@app.post("/api/subir", response_model=list[SubidaRespuesta])
async def api_subir(archivos: list[UploadFile] = File(...), clave: str = ""):
    _check_key(clave)
    resultados = []
    for archivo in archivos:
        nombre = Path(archivo.filename or "sin_nombre.pdf").name
        if not nombre.lower().endswith(".pdf"):
            resultados.append(SubidaRespuesta(archivo=nombre, trozos=0, error="Solo se admiten PDF"))
            continue
        nombre = re.sub(r"[^\w\-. ]", "_", nombre)
        destino = PDF_DIR / nombre
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await archivo.read())
            tmp_path = Path(tmp.name)
        try:
            destino.write_bytes(tmp_path.read_bytes())
            trozos = indexar_pdf(destino)
            if trozos == 0:
                destino.unlink(missing_ok=True)
                resultados.append(
                    SubidaRespuesta(archivo=nombre, trozos=0, error="Sin texto extraible (¿PDF escaneado?)")
                )
            else:
                resultados.append(SubidaRespuesta(archivo=nombre, trozos=trozos))
        except Exception as e:
            destino.unlink(missing_ok=True)
            resultados.append(SubidaRespuesta(archivo=nombre, trozos=0, error=f"Error: {e}"))
        finally:
            tmp_path.unlink(missing_ok=True)
    return resultados


@app.get("/api/estado")
def api_estado():
    facturas = len(list(PDF_DIR.glob("*.pdf")))
    return {"documentos": count(), "facturas": facturas, "protegida": bool(APP_KEY)}


@app.get("/api/documentos")
def api_documentos(clave: str = ""):
    _check_key(clave)
    docs = []
    for p in sorted(PDF_DIR.glob("*.pdf")):
        docs.append({"nombre": p.name, "tamano": p.stat().st_size})
    return {"documentos": docs}


@app.get("/api/pdf/{nombre}")
def api_pdf(nombre: str, clave: str = ""):
    _check_key(clave)
    seguro = Path(nombre).name
    destino = PDF_DIR / seguro
    if not destino.exists() or not seguro.lower().endswith(".pdf"):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return FileResponse(
        destino,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{seguro}"'},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
