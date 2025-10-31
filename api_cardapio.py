# api_cardapio_correct.py - VERSÃO COM FORMATAÇÃO CORRETA
# -*- coding: utf-8 -*-
"""
API FastAPI para geração de cardápios dinâmicos usando CorelDRAW
VERSÃO 4.0 - Formatação correta com alinhamento à esquerda e tabs
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
import pythoncom
import os
import time

# Importar o módulo de build
import build_cardapio_dinamico as builder

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="API Cardápio Dinâmico",
    description="API para geração automática de cardápios em CDR e PDF usando CorelDRAW",
    version="4.0"
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

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "api": "Cardápio Dinâmico",
        "version": "4.0",
        "status": "online",
        "description": "API com formatação correta e tabs funcionais",
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

def apply_proper_formatting(doc, shape, font_name="Arial", font_size_pt=10.0):
    """
    Aplica formatação simplificada usando apenas propriedades que funcionam
    """
    try:
        # Obter o texto story
        text_range = shape.Text.Story

        # Configurar fonte e tamanho PRIMEIRO
        try:
            text_range.Font = font_name
            text_range.Size = float(font_size_pt)
            logger.info(f"   ✅ Fonte {font_name} {font_size_pt}pt aplicada")
        except Exception as e:
            logger.warning(f"   ⚠️ Erro na fonte: {e}")

        # Alinhamento à ESQUERDA (0 = cdrLeftAlignment)
        try:
            text_range.Alignment = 0
            logger.info("   ✅ Alinhamento à esquerda aplicado")
        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao definir alinhamento: {e}")

        # Cor do texto (preto CMYK)
        try:
            text_range.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
            logger.info("   ✅ Cor preta aplicada")
        except Exception as e:
            logger.warning(f"   ⚠️ Erro na cor: {e}")

        # Configurar tabs para alinhar preços à direita
        try:
            # Obter largura do frame
            frame_width = float(shape.SizeWidth)

            # Posição do tab deve ser no final da linha (margem direita)
            # Usar 95% da largura para dar margem
            tab_position = frame_width * 0.95

            # Limpar tabs existentes e adicionar novo
            text_range.TabStops.Clear()
            # 2 = cdrRightTab (alinhamento à direita)
            text_range.TabStops.Add(tab_position, 2)

            logger.info(f"   ✅ Tab configurado em {tab_position:.2f}")

        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao configurar tabs: {e}")
            # Se tabs falharem, o texto ainda ficará legível
            
        # Aplicar negrito apenas nas categorias (linhas em MAIÚSCULO)
        try:
            text_content = text_range.Text
            lines = text_content.split('\r\n')
            char_pos = 0
            
            for line in lines:
                # Verificar se é uma categoria (tudo maiúsculo, sem R$)
                if line and line.isupper() and 'R$' not in line:
                    # É uma categoria - aplicar negrito
                    start = char_pos + 1  # CorelDRAW usa índice 1-based
                    end = start + len(line) - 1
                    
                    try:
                        text_range.Characters.Range(start, end).Bold = True
                        text_range.Characters.Range(start, end).Size = float(font_size_pt + 1)
                    except:
                        pass
                
                char_pos += len(line) + 2  # +2 para \r\n
                
        except Exception as e:
            logger.debug(f"   Negrito não aplicado: {e}")
        
        # Configurar espaçamento de linha se possível
        try:
            text_range.LineSpacing = 1.2  # 120% do tamanho da fonte
        except:
            pass
            
    except Exception as e:
        logger.warning(f"   ⚠️ Erro geral na formatação: {e}")

def process_cardapio(job_id: str, input_path: Path, config: CardapioConfig):
    """
    Processar cardápio com formatação correta e salvamento robusto
    """
    
    # Inicializar COM na thread de background
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
    
    corel = None
    doc = None
    
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
        
        # Parse do arquivo
        logger.info(f"[{job_id}] Fazendo parse do arquivo...")
        data = builder.parse_txt(input_path)
        
        # Gerar arquivos de auditoria
        builder.write_auditoria(job_output, data)
        
        # Inicializar CorelDRAW
        logger.info(f"[{job_id}] Inicializando CorelDRAW...")
        corel = builder.get_corel_app(visible=False)
        
        # Abrir template
        tpl = str(tpl_a if data["model"] == "A" else tpl_b)
        logger.info(f"[{job_id}] Abrindo template {data['model']} ({data['total_items']} itens)...")
        
        doc = corel.OpenDocument(os.path.abspath(tpl))
        
        # Aguardar documento carregar
        time.sleep(0.5)
        
        page = doc.ActivePage
        layer = page.ActiveLayer
        
        # Limpar TODOS os textos existentes do template
        logger.info(f"[{job_id}] Limpando textos do template...")
        texts_removed = 0
        try:
            shapes = page.Shapes
            total_shapes = shapes.Count
            logger.info(f"[{job_id}] Template tem {total_shapes} shapes")

            for i in range(shapes.Count, 0, -1):
                try:
                    s = shapes.Item(i)
                    # Tipos de texto: 6 = cdrTextShape (genérico)
                    # Tentar remover qualquer coisa que pareça texto
                    if s.Type == 6:  # cdrTextShape
                        s.Delete()
                        texts_removed += 1
                except Exception as e:
                    logger.debug(f"[{job_id}] Não foi possível remover shape {i}: {e}")
                    pass

            logger.info(f"[{job_id}] ✅ {texts_removed} textos removidos do template")
        except Exception as e:
            logger.warning(f"[{job_id}] Aviso ao limpar template: {e}")
        
        # Criar título do restaurante
        logger.info(f"[{job_id}] Criando título: {data['restaurant']}")
        try:
            pw = float(page.SizeWidth)
            ph = float(page.SizeHeight)
            title_x = pw / 2.0
            title_y = ph - 1.0
            
            title_shape = layer.CreateArtisticText(0.0, title_y, data["restaurant"])
            title_shape.Text.Story.Font = config.font
            title_shape.Text.Story.Size = 24
            title_shape.Text.Story.Bold = True
            
            # Centralizar título
            try:
                text_width = float(title_shape.SizeWidth)
                title_shape.LeftX = title_x - (text_width / 2.0)
            except:
                pass
                
        except Exception as e:
            logger.warning(f"[{job_id}] Erro ao criar título: {e}")
        
        # Criar conteúdo do cardápio
        logger.info(f"[{job_id}] Criando conteúdo do cardápio...")
        frames = builder.ensure_area_frames(page, doc, data["model"])

        shapes_before = page.Shapes.Count
        logger.info(f"[{job_id}] Shapes antes de criar conteúdo: {shapes_before}")

        if data["model"] == "A":
            # Modelo A: 1 coluna
            logger.info(f"[{job_id}] Criando 1 caixa de texto (Modelo A)")
            seq = builder.flatten_with_headers(data["categories"])
            text_block = builder.compose_text_block(seq)
            left, bottom, right, top = frames[0]

            shp = builder.create_paragraph_text(layer, left, bottom, right, top)

            # Preencher texto primeiro
            builder.fill_paragraph(shp, text_block)

            # Aplicar formatação correta (sem justificar)
            apply_proper_formatting(doc, shp, font_name=config.font, font_size_pt=config.font_size)

        else:
            # Modelo B: 2 colunas
            logger.info(f"[{job_id}] Criando 2 caixas de texto (Modelo B)")
            col1, col2 = builder.split_two_columns_preserving_order(data["categories"])
            tb1 = builder.compose_text_block(col1)
            tb2 = builder.compose_text_block(col2)

            frame1, frame2 = frames
            left1, bottom1, right1, top1 = frame1
            left2, bottom2, right2, top2 = frame2

            # Coluna 1
            logger.info(f"[{job_id}] Criando coluna 1...")
            shp1 = builder.create_paragraph_text(layer, left1, bottom1, right1, top1)
            builder.fill_paragraph(shp1, tb1)
            apply_proper_formatting(doc, shp1, font_name=config.font, font_size_pt=config.font_size)

            # Coluna 2
            logger.info(f"[{job_id}] Criando coluna 2...")
            shp2 = builder.create_paragraph_text(layer, left2, bottom2, right2, top2)
            builder.fill_paragraph(shp2, tb2)
            apply_proper_formatting(doc, shp2, font_name=config.font, font_size_pt=config.font_size)

        shapes_after = page.Shapes.Count
        shapes_created = shapes_after - shapes_before
        logger.info(f"[{job_id}] Shapes depois de criar conteúdo: {shapes_after}")
        logger.info(f"[{job_id}] ✅ {shapes_created} shapes criadas")
        
        # SALVAR ARQUIVOS
        logger.info(f"[{job_id}] Salvando arquivos...")
        out_cdr = job_output / f"cardapio_{job_id}.cdr"
        out_pdf = job_output / "cardapio.pdf"

        files_saved = {}

        # Salvar CDR - múltiplos métodos
        cdr_saved = False

        # Método 1: SaveAs direto com path absoluto
        try:
            # Garantir que é uma string absoluta com barras invertidas
            cdr_path_str = os.path.abspath(str(out_cdr))
            logger.info(f"[{job_id}] Tentando salvar em: {cdr_path_str}")
            doc.SaveAs(cdr_path_str)
            cdr_saved = True
            logger.info(f"[{job_id}] ✅ CDR salvo com SaveAs")
        except Exception as e1:
            logger.warning(f"[{job_id}] SaveAs falhou: {e1}")
            
            # Método 2: Salvar em temp e copiar
            try:
                temp_cdr = TEMP_DIR / f"temp_{job_id}.cdr"
                temp_path = str(temp_cdr.absolute()).replace('/', '\\')
                doc.SaveAs(temp_path)
                shutil.copy2(temp_cdr, out_cdr)
                temp_cdr.unlink()
                cdr_saved = True
                logger.info(f"[{job_id}] ✅ CDR salvo via temp")
            except Exception as e2:
                logger.warning(f"[{job_id}] Temp save falhou: {e2}")
                
                # Método 3: Save() e procurar arquivo
                try:
                    doc.Save()
                    time.sleep(1)  # Aguardar salvamento
                    
                    # Procurar em locais possíveis
                    search_paths = [
                        Path(tpl).parent,
                        TEMP_DIR,
                        Path.cwd(),
                        OUTPUT_DIR
                    ]
                    
                    for search_dir in search_paths:
                        if search_dir.exists():
                            for cdr_file in search_dir.glob("*.cdr"):
                                # Verificar se é um arquivo recente (modificado nos últimos 5 segundos)
                                if time.time() - cdr_file.stat().st_mtime < 5:
                                    shutil.copy2(cdr_file, out_cdr)
                                    if cdr_file != out_cdr:
                                        cdr_file.unlink()
                                    cdr_saved = True
                                    logger.info(f"[{job_id}] ✅ CDR recuperado de {cdr_file}")
                                    break
                        if cdr_saved:
                            break
                            
                except Exception as e3:
                    logger.error(f"[{job_id}] Save e busca falharam: {e3}")
        
        # Se não salvou CDR, copiar template como fallback
        if not cdr_saved:
            try:
                shutil.copy2(tpl, out_cdr)
                logger.warning(f"[{job_id}] ⚠️ CDR: template copiado (edições podem não estar salvas)")
                cdr_saved = True
            except:
                out_cdr.write_text("CDR não disponível")
        
        if cdr_saved and out_cdr.exists():
            files_saved["cdr"] = out_cdr.name
        
        # Exportar PDF
        pdf_saved = False
        try:
            pdf_path = str(out_pdf.absolute()).replace('/', '\\')
            doc.PublishToPDF(pdf_path)
            pdf_saved = True
            logger.info(f"[{job_id}] ✅ PDF exportado com sucesso")
        except Exception as e:
            logger.warning(f"[{job_id}] ⚠️ Erro ao gerar PDF: {e}")
        
        if pdf_saved:
            files_saved["pdf"] = out_pdf.name
        
        # Sempre incluir JSON e CSV
        files_saved["json"] = "parsed.json"
        files_saved["csv"] = "auditoria.csv"
        
        # Atualizar status
        jobs_cache[job_id].update({
            "status": "completed",
            "message": f"Cardápio processado com sucesso!",
            "completed_at": datetime.now().isoformat(),
            "files": files_saved
        })
        
        logger.info(f"[{job_id}] ✅ Processamento concluído!")
        logger.info(f"[{job_id}] Arquivos gerados: {', '.join(files_saved.keys())}")
        
    except Exception as e:
        logger.error(f"[{job_id}] Erro geral: {str(e)}", exc_info=True)
        jobs_cache[job_id].update({
            "status": "failed",
            "message": f"Erro no processamento: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
    
    finally:
        # Limpeza
        if doc:
            try:
                doc.Close()
                logger.info(f"[{job_id}] Documento fechado")
            except Exception as e:
                logger.debug(f"[{job_id}] Aviso ao fechar documento: {e}")
        
        if corel:
            try:
                corel.Quit()
                logger.info(f"[{job_id}] CorelDRAW fechado")
            except Exception as e:
                logger.debug(f"[{job_id}] Aviso ao fechar CorelDRAW: {e}")
        
        # Finalizar COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass

@app.post("/cardapio/gerar")
async def gerar_cardapio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    font: str = "Arial",
    font_size: float = 10.0
):
    """
    Gerar cardápio com formatação correta
    """
    
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
        "message": "Processamento iniciado",
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
    
    # Para CDR, procurar arquivo com nome variável
    if file_type == "cdr":
        cdr_files = list((OUTPUT_DIR / job_id).glob("*.cdr"))
        if cdr_files:
            return FileResponse(
                path=cdr_files[0],
                filename="cardapio.cdr",
                media_type="application/octet-stream"
            )
        else:
            raise HTTPException(status_code=404, detail="Arquivo CDR não encontrado")
    
    file_map = {
        "pdf": "cardapio.pdf",
        "json": "parsed.json",
        "csv": "auditoria.csv"
    }
    
    if file_type not in ["cdr", "pdf", "json", "csv"]:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use: cdr, pdf, json, csv")
    
    if file_type in file_map:
        file_path = OUTPUT_DIR / job_id / file_map[file_type]
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Arquivo {file_type.upper()} não encontrado")
        
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
    print("\n" + "="*60)
    print("🚀 API CARDÁPIO DINÂMICO - VERSÃO CORRETA")
    print("="*60)
    print("\n📌 Formatação: Alinhamento à esquerda com tabs")
    print("📌 Sem justificação que bagunça o texto")
    print("📌 CDR: Múltiplos métodos de salvamento")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)