# api_cardapio.py
# -*- coding: utf-8 -*-
"""
API FastAPI para geração de cardápios dinâmicos usando CorelDRAW
Roda em Windows Server ou localmente
VERSÃO CORRIGIDA: suporte a COM em threads
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil
import uuid
import logging
from typing import Optional
from datetime import datetime
import pythoncom  # ADICIONADO: para inicializar COM em threads

# Importar o módulo de build
import build_cardapio_dinamico as builder

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="API Cardápio Dinâmico",
    description="API para geração automática de cardápios em PDF/PNG/CDR usando CorelDRAW",
    version="1.0.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Cache de jobs
jobs_cache = {}

class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    files: Optional[dict] = None
    created_at: str
    completed_at: Optional[str] = None

class CardapioConfig(BaseModel):
    font: str = "Arial"
    font_size: float = 10.0
    template_a: Optional[str] = None
    template_b: Optional[str] = None

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "api": "Cardápio Dinâmico",
        "version": "1.0.1",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "upload": "/cardapio/gerar (POST)",
            "status": "/cardapio/status/{job_id} (GET)",
            "download": "/cardapio/download/{job_id}/{file_type} (GET)",
        }
    }

@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    try:
        # Inicializar COM temporariamente para teste
        pythoncom.CoInitialize()
        try:
            corel = builder.get_corel_app(visible=False)
            corel_status = "available"
            try:
                corel.Quit()
            except:
                pass
        except Exception as e:
            corel_status = f"unavailable: {str(e)}"
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        corel_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "corel_draw": corel_status,
        "templates": {
            "tplA": (TEMPLATES_DIR / "tplA.cdr").exists(),
            "tplB": (TEMPLATES_DIR / "tplB.cdr").exists(),
        }
    }

def process_cardapio(job_id: str, input_path: Path, config: CardapioConfig):
    """
    Processar cardápio em background
    CRÍTICO: Esta função roda em uma thread separada, precisa inicializar COM
    """
    
    # CRÍTICO: Inicializar COM na thread de background
    try:
        pythoncom.CoInitialize()
    except Exception as e:
        logger.error(f"[{job_id}] Erro ao inicializar COM: {e}")
        jobs_cache[job_id].update({
            "status": "failed",
            "message": f"Erro ao inicializar COM: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        return
    
    try:
        logger.info(f"[{job_id}] Iniciando processamento...")
        jobs_cache[job_id]["status"] = "processing"
        
        # Diretório de saída
        job_output = OUTPUT_DIR / job_id
        job_output.mkdir(exist_ok=True)
        
        # Templates
        tpl_a = TEMPLATES_DIR / "tplA.cdr"
        tpl_b = TEMPLATES_DIR / "tplB.cdr"
        
        if not tpl_a.exists() or not tpl_b.exists():
            raise FileNotFoundError("Templates CDR não encontrados.")
        
        # Parse
        logger.info(f"[{job_id}] Parsing input...")
        data = builder.parse_txt(input_path)
        
        # Auditoria
        builder.write_auditoria(job_output, data)
        
        # Inicializar CorelDRAW
        logger.info(f"[{job_id}] Inicializando CorelDRAW...")
        corel = builder.get_corel_app(visible=False)
        
        # Abrir template
        tpl = str(tpl_a if data["model"] == "A" else tpl_b)
        logger.info(f"[{job_id}] Abrindo template {data['model']}...")
        doc = corel.OpenDocument(tpl)
        page = doc.ActivePage
        layer = page.ActiveLayer
        
        # Limpar textos existentes
        shapes = page.Shapes
        for i in range(shapes.Count, 0, -1):
            s = shapes.Item(i)
            try:
                if s.Type == 3:
                    s.Delete()
            except:
                pass
        
        # Criar título
        logger.info(f"[{job_id}] Criando título...")
        pw = float(page.SizeWidth)
        ph = float(page.SizeHeight)
        title_x = pw / 2.0
        title_y = ph - 1.0
        
        title_shape = layer.CreateArtisticText(0.0, float(title_y), str(data["restaurant"]))
        title_shape.Text.Story.Font = config.font
        title_shape.Text.Story.Size = float(24)
        title_shape.Text.Story.Bold = True
        
        try:
            title_shape.Text.Story.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
        except:
            pass
        
        try:
            text_width = float(title_shape.SizeWidth)
            title_shape.LeftX = title_x - (text_width / 2.0)
        except:
            pass
        
        # Criar conteúdo
        logger.info(f"[{job_id}] Criando conteúdo...")
        frames = builder.ensure_area_frames(page, doc, data["model"])
        
        if data["model"] == "A":
            seq = builder.flatten_with_headers(data["categories"])
            text_block = builder.compose_text_block(seq)
            left, bottom, right, top = frames[0]
            
            shp = builder.create_paragraph_text(layer, left, bottom, right, top)
            builder.apply_text_style_and_tabs(doc, shp, font_name=config.font, font_size_pt=config.font_size)
            builder.fill_paragraph(shp, text_block)
        else:
            col1, col2 = builder.split_two_columns_preserving_order(data["categories"])
            tb1 = builder.compose_text_block(col1)
            tb2 = builder.compose_text_block(col2)
            
            frame1, frame2 = frames
            left1, bottom1, right1, top1 = frame1
            left2, bottom2, right2, top2 = frame2
            
            shp1 = builder.create_paragraph_text(layer, left1, bottom1, right1, top1)
            builder.apply_text_style_and_tabs(doc, shp1, font_name=config.font, font_size_pt=config.font_size)
            builder.fill_paragraph(shp1, tb1)
            
            shp2 = builder.create_paragraph_text(layer, left2, bottom2, right2, top2)
            builder.apply_text_style_and_tabs(doc, shp2, font_name=config.font, font_size_pt=config.font_size)
            builder.fill_paragraph(shp2, tb2)
        
        # Salvar arquivos
        logger.info(f"[{job_id}] Salvando arquivos...")
        out_cdr = job_output / "cardapio_output.cdr"
        out_pdf = job_output / "cardapio_output.pdf"
        out_png = job_output / "cardapio_output.png"
        
        doc.SaveAs(str(out_cdr.absolute()).replace('/', '\\'))
        doc.PublishToPDF(str(out_pdf.absolute()).replace('/', '\\'))
        doc.Export(str(out_png.absolute()).replace('/', '\\'), 13, 1)
        
        # Fechar
        doc.Close(False)
        corel.Quit()
        
        # Atualizar status
        jobs_cache[job_id].update({
            "status": "completed",
            "message": "Cardápio gerado com sucesso",
            "completed_at": datetime.now().isoformat(),
            "files": {
                "cdr": out_cdr.name,
                "pdf": out_pdf.name,
                "png": out_png.name,
                "json": "parsed.json",
                "csv": "auditoria.csv"
            }
        })
        
        logger.info(f"[{job_id}] Processamento concluído!")
        
    except Exception as e:
        logger.error(f"[{job_id}] Erro: {str(e)}", exc_info=True)
        jobs_cache[job_id].update({
            "status": "failed",
            "message": f"Erro: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
    
    finally:
        # CRÍTICO: Finalizar COM ao terminar
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

@app.post("/cardapio/gerar")
async def gerar_cardapio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    font: str = "Arial",
    font_size: float = 10.0
):
    """Gerar cardápio a partir de arquivo TXT"""
    
    # Validar arquivo
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .txt")
    
    # Gerar job_id único
    job_id = str(uuid.uuid4())
    
    # Salvar arquivo temporário
    temp_input = TEMP_DIR / f"{job_id}_input.txt"
    try:
        with temp_input.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Criar job no cache
    jobs_cache[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "message": "Aguardando processamento",
        "files": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # Configuração
    config = CardapioConfig(font=font, font_size=font_size)
    
    # Adicionar task em background
    background_tasks.add_task(process_cardapio, job_id, temp_input, config)
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Processamento iniciado. Use /cardapio/status/{job_id} para acompanhar.",
        "status_url": f"/cardapio/status/{job_id}"
    }

@app.get("/cardapio/status/{job_id}")
async def get_status(job_id: str):
    """Verificar status do processamento"""
    if job_id not in jobs_cache:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return jobs_cache[job_id]

@app.get("/cardapio/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """Baixar arquivo gerado"""
    if job_id not in jobs_cache:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = jobs_cache[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processamento ainda não concluído")
    
    file_map = {
        "pdf": "cardapio_output.pdf",
        "png": "cardapio_output.png",
        "cdr": "cardapio_output.cdr",
        "json": "parsed.json",
        "csv": "auditoria.csv"
    }
    
    if file_type not in file_map:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use: {', '.join(file_map.keys())}")
    
    file_path = OUTPUT_DIR / job_id / file_map[file_type]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )

@app.delete("/cardapio/limpar/{job_id}")
async def limpar_job(job_id: str):
    """Remover arquivos de um job"""
    if job_id not in jobs_cache:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job_output = OUTPUT_DIR / job_id
    if job_output.exists():
        shutil.rmtree(job_output)
    
    temp_input = TEMP_DIR / f"{job_id}_input.txt"
    if temp_input.exists():
        temp_input.unlink()
    
    del jobs_cache[job_id]
    
    return {"message": "Job removido com sucesso"}

@app.get("/cardapio/listar")
async def listar_jobs():
    """Listar todos os jobs"""
    return {
        "total": len(jobs_cache),
        "jobs": list(jobs_cache.values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)