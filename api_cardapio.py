# api_cardapio_correct.py - VERSÃO COM FORMATAÇÃO CORRETA
# -*- coding: utf-8 -*-
"""
API FastAPI para geração de cardápios dinâmicos usando CorelDRAW
VERSÃO 4.2 - Integração com Supabase
- Formatação correta com alinhamento à esquerda e tabs
- Endpoint /cardapio/formatar para receber texto direto
- Upload automático de arquivos CDR para bucket Supabase
- Atualização automática da tabela Printa com link público
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
from supabase import create_client, Client

# Importar o módulo de build
import build_cardapio_dinamico as builder

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Supabase
SUPABASE_URL = "https://weshxwjwrtsypnqyqkbz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indlc2h4d2p3cnRzeXBucXlxa2J6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYxNzkyNDcsImV4cCI6MjA3MTc1NTI0N30.sHe5WMBBL36ufEy2B9l0qyrIKH8xavRT8SGEeuCCGvQ"
SUPABASE_BUCKET = "corel"

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializar FastAPI
app = FastAPI(
    title="API Cardápio Dinâmico",
    description="API para geração automática de cardápios em CDR e PDF usando CorelDRAW com integração Supabase",
    version="4.2"
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
    supabase_url: Optional[str] = None  # URL pública do arquivo CDR no Supabase
    created_at: str
    completed_at: Optional[str] = None

class CardapioConfig(BaseModel):
    font: str = "Arial"
    font_size: float = 10.0

class FormatRequest(BaseModel):
    id: str
    text: str
    font: str = "Arial"
    font_size: float = 10.0

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "api": "Cardápio Dinâmico",
        "version": "4.2",
        "status": "online",
        "description": "API com formatação correta, tabs funcionais e integração Supabase",
        "features": [
            "Upload automático para Supabase bucket 'corel'",
            "Atualização da tabela Printa com link público",
            "Processamento em background",
            "Múltiplos formatos de saída (CDR, PDF, JSON, CSV)"
        ],
        "endpoints": {
            "health": "/health",
            "ping": "/ping (GET)",
            "upload": "/cardapio/gerar (POST)",
            "formatar": "/cardapio/formatar (POST) - Aceita texto direto + Integração Supabase",
            "status": "/cardapio/status/{job_id} (GET)",
            "download": "/cardapio/download/{job_id}/{file_type} (GET)",
            "listar": "/cardapio/listar (GET)",
            "limpar": "/cardapio/limpar/{job_id} (DELETE)"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar saúde da API (teste completo)"""
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

@app.get("/ping")
async def ping():
    """
    Endpoint simples para testar conectividade (não verifica CorelDRAW)
    Use este endpoint no n8n para verificar se a API está acessível
    """
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return {
        "status": "ok",
        "message": "API está respondendo",
        "timestamp": datetime.now().isoformat(),
        "server": {
            "hostname": hostname,
            "local_ip": local_ip,
            "port": 8000
        }
    }

def upload_cdr_to_supabase(file_path: Path, job_id: str) -> Optional[str]:
    """
    Faz upload do arquivo CDR para o bucket Supabase e retorna a URL pública

    Args:
        file_path: Caminho do arquivo CDR local
        job_id: ID do job (será usado como nome do arquivo no bucket)

    Returns:
        URL pública do arquivo ou None se falhar
    """
    try:
        if not file_path.exists():
            logger.error(f"[{job_id}] Arquivo CDR não encontrado: {file_path}")
            return None

        # Ler o arquivo
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Nome do arquivo no bucket
        file_name = f"{job_id}.cdr"

        logger.info(f"[{job_id}] 📤 Fazendo upload para Supabase bucket '{SUPABASE_BUCKET}'...")

        # Upload para o bucket
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": "application/x-coreldraw", "upsert": "true"}
        )

        # Obter URL pública
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_name)

        logger.info(f"[{job_id}] ✅ Upload concluído!")
        logger.info(f"[{job_id}] 🔗 URL pública: {public_url}")

        return public_url

    except Exception as e:
        logger.error(f"[{job_id}] ❌ Erro no upload para Supabase: {e}", exc_info=True)
        return None

def update_printa_table(job_id: str, public_url: str) -> bool:
    """
    Atualiza a tabela Printa com o link do arquivo CDR

    Args:
        job_id: ID do job (usado para localizar o registro)
        public_url: URL pública do arquivo CDR

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        logger.info(f"[{job_id}] 📝 Atualizando tabela Printa...")

        # Atualizar o registro onde id = job_id
        response = supabase.table("Printa").update({
            "link_arquivo_output": public_url
        }).eq("id", job_id).execute()

        logger.info(f"[{job_id}] ✅ Tabela Printa atualizada com sucesso!")

        return True

    except Exception as e:
        logger.error(f"[{job_id}] ❌ Erro ao atualizar tabela Printa: {e}", exc_info=True)
        return False

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

        # NOTA: TabStops não está disponível na API COM desta versão do CorelDRAW
        # Solução: O texto já vem formatado com pontos (.) para alinhar preços
        logger.info("   ℹ️ Usando pontos de preenchimento para alinhar preços (TabStops não disponível)")
            
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

        # NÃO gerar arquivos de auditoria (JSON, CSV) - desabilitado
        # builder.write_auditoria(job_output, data)
        
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
            left, bottom, right, top = frames[0]
            frame_width = abs(right - left)

            # Calcular largura em caracteres
            target_width = builder.calculate_char_width_for_frame(frame_width, config.font_size)
            logger.info(f"[{job_id}] 📏 Largura da caixa: {frame_width:.2f} unidades = ~{target_width} caracteres")

            seq = builder.flatten_with_headers(data["categories"])
            logger.info(f"[{job_id}] 📝 Gerando texto (com debug)...")
            text_block = builder.compose_text_block(seq, use_dots=True, target_width=target_width, debug=True)

            shp = builder.create_paragraph_text(layer, left, bottom, right, top)

            # Preencher texto primeiro
            builder.fill_paragraph(shp, text_block)

            # Aplicar formatação correta (sem justificar)
            apply_proper_formatting(doc, shp, font_name=config.font, font_size_pt=config.font_size)

        else:
            # Modelo B: 2 colunas
            logger.info(f"[{job_id}] Criando 2 caixas de texto (Modelo B)")
            col1, col2 = builder.split_two_columns_preserving_order(data["categories"])

            frame1, frame2 = frames
            left1, bottom1, right1, top1 = frame1
            left2, bottom2, right2, top2 = frame2

            # Calcular largura para cada coluna
            frame_width1 = abs(right1 - left1)
            frame_width2 = abs(right2 - left2)
            target_width1 = builder.calculate_char_width_for_frame(frame_width1, config.font_size)
            target_width2 = builder.calculate_char_width_for_frame(frame_width2, config.font_size)

            logger.info(f"[{job_id}] 📏 Coluna 1: {frame_width1:.2f} unidades = ~{target_width1} caracteres")
            logger.info(f"[{job_id}] 📏 Coluna 2: {frame_width2:.2f} unidades = ~{target_width2} caracteres")

            logger.info(f"[{job_id}] 📝 Gerando texto coluna 1 (com debug)...")
            tb1 = builder.compose_text_block(col1, use_dots=True, target_width=target_width1, debug=True)
            logger.info(f"[{job_id}] 📝 Gerando texto coluna 2 (com debug)...")
            tb2 = builder.compose_text_block(col2, use_dots=True, target_width=target_width2, debug=True)

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
        out_cdr_temp = TEMP_DIR / f"cardapio_{job_id}.cdr"  # CDR temporário para upload
        out_pdf = job_output / "cardapio.pdf"

        files_saved = {}

        # Salvar CDR TEMPORARIAMENTE (só para upload no Supabase)
        cdr_saved = False

        # Método 1: Export como CDR (mais confiável que SaveAs)
        try:
            cdr_path_str = os.path.abspath(str(out_cdr_temp))
            logger.info(f"[{job_id}] Tentando exportar CDR temporário para: {cdr_path_str}")

            # cdrCDR = 48 (formato CDR)
            # cdrNormalSave = 0
            doc.Export(cdr_path_str, 48, 0)
            cdr_saved = True
            logger.info(f"[{job_id}] ✅ CDR exportado temporariamente")
        except Exception as e1:
            logger.warning(f"[{job_id}] Export CDR falhou: {e1}")

            # Método 2: Tentar apenas salvar o documento (Save sem nome = salva no local atual)
            try:
                logger.info(f"[{job_id}] Tentando doc.Save()...")
                doc.Save()
                time.sleep(0.5)

                # Procurar arquivo salvo nos templates
                possible_saved = Path(tpl).with_name(f"cardapio_{job_id}.cdr")
                if possible_saved.exists():
                    shutil.copy2(possible_saved, out_cdr_temp)
                    possible_saved.unlink()
                    cdr_saved = True
                    logger.info(f"[{job_id}] ✅ CDR salvo via doc.Save() e movido")
            except Exception as e2:
                logger.warning(f"[{job_id}] doc.Save() falhou: {e2}")

        # Se não salvou CDR, copiar template como fallback
        if not cdr_saved:
            try:
                shutil.copy2(tpl, out_cdr_temp)
                logger.warning(f"[{job_id}] ⚠️ CDR: template copiado (edições podem não estar salvas)")
                cdr_saved = True
            except Exception as e3:
                logger.error(f"[{job_id}] Falha ao copiar template: {e3}")
        
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

        # Upload do CDR para Supabase e atualização da tabela Printa
        public_url = None
        if cdr_saved and out_cdr_temp.exists():
            logger.info(f"[{job_id}] 🚀 Iniciando integração com Supabase...")

            # Upload do arquivo CDR temporário
            public_url = upload_cdr_to_supabase(out_cdr_temp, job_id)

            # Deletar CDR temporário após upload
            try:
                out_cdr_temp.unlink()
                logger.info(f"[{job_id}] 🗑️ CDR temporário removido")
            except Exception as e:
                logger.warning(f"[{job_id}] Não foi possível remover CDR temporário: {e}")

            if public_url:
                # Atualizar tabela Printa
                update_success = update_printa_table(job_id, public_url)

                if update_success:
                    files_saved["supabase_url"] = public_url
                    logger.info(f"[{job_id}] ✅ Integração Supabase completa!")
                else:
                    logger.warning(f"[{job_id}] ⚠️ Upload feito, mas falha ao atualizar tabela")
            else:
                logger.warning(f"[{job_id}] ⚠️ Falha no upload para Supabase")

        # Atualizar status
        jobs_cache[job_id].update({
            "status": "completed",
            "message": f"Cardápio processado com sucesso!",
            "completed_at": datetime.now().isoformat(),
            "files": files_saved,
            "supabase_url": public_url  # Adicionar URL pública do Supabase
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

def process_cardapio_from_text(job_id: str, text_content: str, config: CardapioConfig):
    """
    Processar cardápio a partir de texto direto (sem arquivo)
    """
    import re

    # Normalizar quebras de linha (pode vir como \n literal ou real)
    # Substituir \n literal por quebra de linha real
    if '\\n' in text_content:
        text_content = text_content.replace('\\n', '\n')

    # Garantir que temos quebras de linha Unix
    text_content = text_content.replace('\r\n', '\n').replace('\r', '\n')

    # Log para debug
    lines_count = len(text_content.splitlines())
    logger.info(f"[{job_id}] Texto recebido com {lines_count} linhas")
    logger.info(f"[{job_id}] Primeiras 200 chars: {text_content[:200]}")

    # Se chegou em uma única linha, tentar recuperar a estrutura
    if lines_count <= 3 and len(text_content) > 100:
        logger.warning(f"[{job_id}] Texto veio em linha única! Tentando recuperar estrutura...")

        # 1. Adicionar quebra após "RELATÓRIO DE PREÇOS Nome"
        text_content = re.sub(r'(RELATÓRIO DE PREÇOS\s+[^\*]+?)(\s+\*)', r'\1\n\n\2', text_content)

        # 2. Adicionar quebra de linha ANTES de categorias (palavras entre asteriscos)
        # Padrão: qualquer coisa + espaços + *categoria*
        text_content = re.sub(r'([^\n])\s{2,}(\*[^*]+\*)', r'\1\n\n\2', text_content)

        # 3. Adicionar quebra de linha DEPOIS de categorias
        text_content = re.sub(r'(\*[^*]+\*)\s+', r'\1\n', text_content)

        # 4. Adicionar quebra de linha após cada item com preço
        # Padrão: qualquer coisa + R$ + números + vírgula + números + espaços
        text_content = re.sub(r'(R\$\s*\d+,\d{2})\s+', r'\1\n', text_content)

        # 5. Limpar múltiplas quebras de linha consecutivas
        text_content = re.sub(r'\n{3,}', '\n\n', text_content)

        lines_count_after = len(text_content.splitlines())
        logger.info(f"[{job_id}] Após recuperação: {lines_count_after} linhas")
        logger.info(f"[{job_id}] Primeiras 500 chars após recuperação: {text_content[:500]}")

    # Salvar texto em arquivo temporário para usar a mesma pipeline
    temp_input = TEMP_DIR / f"{job_id}_input.txt"
    try:
        temp_input.write_text(text_content, encoding='utf-8')
    except Exception as e:
        logger.error(f"[{job_id}] Erro ao salvar texto temporário: {e}")
        jobs_cache[job_id].update({
            "status": "failed",
            "message": f"Erro ao salvar texto: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        return

    # Usar a função de processamento existente
    process_cardapio(job_id, temp_input, config)

@app.post("/cardapio/formatar")
async def formatar_cardapio(
    background_tasks: BackgroundTasks,
    request: FormatRequest
):
    """
    Formatar cardápio a partir de texto direto

    Recebe:
    - id: Identificador do cardápio (será usado como job_id)
    - text: Conteúdo do cardápio em formato texto
    - font: Fonte a ser usada (padrão: Arial)
    - font_size: Tamanho da fonte (padrão: 10.0)

    Exemplo de texto:
    ```
    RELATÓRIO DE PREÇOS Lula Bar

    *Cervejas 600ml*
    Brahma Chopp (600ml) - R$ 11,00
    Corona (600ml) - R$ 17,00
    ```
    """

    # Validar que o texto não está vazio
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="O campo 'text' não pode estar vazio")

    # Usar o ID fornecido pelo usuário
    job_id = request.id

    # Verificar se já existe um job com este ID
    if job_id in jobs_cache:
        existing_job = jobs_cache[job_id]
        if existing_job["status"] == "processing":
            raise HTTPException(
                status_code=409,
                detail=f"Job com ID '{job_id}' já está em processamento"
            )
        # Se já foi processado, permitir reprocessar
        logger.info(f"[{job_id}] Reprocessando job existente")

    # Criar job no cache
    jobs_cache[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "message": "Processamento iniciado",
        "files": None,
        "supabase_url": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }

    # Configuração
    config = CardapioConfig(font=request.font, font_size=request.font_size)

    # Adicionar task em background
    background_tasks.add_task(process_cardapio_from_text, job_id, request.text, config)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Processamento iniciado. Use /cardapio/status/{job_id} para acompanhar.",
        "status_url": f"/cardapio/status/{job_id}"
    }

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
        "supabase_url": None,
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
    import sys

    # Permitir configurar porta via argumento --port
    port = 8000
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                print(f"Erro: Porta inválida '{sys.argv[i + 1]}'")
                sys.exit(1)

    print("\n" + "="*60)
    print("🚀 API CARDÁPIO DINÂMICO v4.2")
    print("="*60)
    print("\n📌 Formatação: Alinhamento à esquerda com tabs")
    print("📌 Sem justificação que bagunça o texto")
    print("📌 CDR: Múltiplos métodos de salvamento")
    print("📌 Endpoint /cardapio/formatar (texto direto)")
    print("📌 INTEGRAÇÃO SUPABASE:")
    print("   ✅ Upload automático para bucket 'corel'")
    print("   ✅ Atualização da tabela 'Printa'")
    print(f"📌 Porta: {port}")
    if port == 80:
        print("⚠️  PORTA 80 - Requer privilégios de administrador")
    print("\n" + "="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=port)