# RAG Facturas

Consultas inteligentes sobre facturas y recibos de venta usando RAG (Retrieval-Augmented Generation).

Sube PDFs de facturas y pregunta en lenguaje natural: *"¿Cuánto me facturó Panadería La Espiga?"*. El asistente responde **solo** con la información de tus facturas, citando las fuentes.

## Stack

- **FastAPI** — backend y API web
- **ChromaDB** — base de datos vectorial local
- **Google Gemini** — embeddings (`gemini-embedding-001`) y respuestas (`gemini-3.8-flash`), capa gratuita
- **pypdf** — extracción de texto de PDFs
- **HTML + JS vanilla** — interfaz, sin frameworks

## Puesta en marcha

1. Instala dependencias:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

2. Crea el archivo `.env` con tu API key de [Google AI Studio](https://aistudio.google.com):

```
GEMINI_API_KEY=tu_clave
APP_KEY=clave_opcional_para_proteger_la_app
```

3. Copia tus facturas (PDF) a `data/pdfs/` y genera el índice:

```bash
.venv\Scripts\python.exe scripts/indexar.py
```

4. Arranca la app web:

```bash
.venv\Scripts\uvicorn.exe app.main:app --port 8000
```

Abre http://localhost:8000

## Uso por línea de comandos

```bash
# Indexar (--reset borra el índice anterior)
python scripts/indexar.py --reset

# Preguntar
python scripts/preguntar.py "¿Cuánto me facturó Ferretería El Tornillo?"

# Probar la búsqueda semántica
python scripts/probar_busqueda.py "aceite de oliva"
```

## Estructura

```
app/
  config.py      configuración y rutas
  gemini.py      cliente de Gemini (embeddings + LLM)
  ingest.py      extracción de texto y troceado
  pipeline.py    indexado de un PDF
  store.py       ChromaDB (guardar/consultar)
  rag.py         lógica del RAG (búsqueda + respuesta)
  main.py        API FastAPI
  static/        interfaz web
scripts/         comandos de terminal
data/
  pdfs/          tus facturas (no se suben a git)
  index/         índice vectorial (no se sube a git)
```

## Notas

- Los PDFs escaneados (imágenes) no funcionan sin OCR.
- El front es HTML puro: la interfaz se puede reemplazar sin tocar la lógica.
- Para producción existe un pequeño adaptador en `store.py` que permite migrar de ChromaDB a PostgreSQL + pgvector.
