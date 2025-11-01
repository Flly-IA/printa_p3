# build_cardapio_dinamico.py
# -*- coding: utf-8 -*-
import argparse
import csv
import json
import re
import sys
from pathlib import Path

try:
    import win32com.client as win32
    import pythoncom  # ADICIONADO: necessário para CoInitialize
except ImportError:
    print("pywin32 não encontrado. Instale com: pip install pywin32")
    sys.exit(1)

def get_corel_app(visible=True):
    """Inicializa CorelDRAW COM com suporte a multi-threading"""
    
    # CRÍTICO: Inicializar COM na thread atual
    try:
        pythoncom.CoInitialize()
    except Exception as e:
        print(f"Aviso ao inicializar COM: {e}")
    
    # Tentar conectar ao CorelDRAW já aberto
    try:
        app = win32.GetActiveObject("CorelDRAW.Application")
        app.Visible = visible
        return app
    except Exception:
        pass
    
    # Tentar iniciar CorelDRAW 25 especificamente
    try:
        app = win32.Dispatch("CorelDRAW.Application.25")
        app.Visible = visible
        return app
    except Exception as e:
        print(f"Tentativa CorelDRAW.Application.25: {e}")
    
    # Tentar versões genéricas
    for pid in [
        "CorelDRAW.Application",
        "CorelDRAW.Application.26",
        "CorelDRAW.Application.24",
        "CorelDRAW.Application.23",
        "CorelDRAW.Application.22",
    ]:
        try:
            app = win32.Dispatch(pid)
            app.Visible = visible
            return app
        except Exception:
            continue
    
    raise RuntimeError("CorelDRAW COM indisponível. Verifique se o CorelDRAW está instalado.")

PRICE_RE = re.compile(r"\s-\s*R\$\s*([\d\.,]+)\s*$", flags=re.IGNORECASE)

def parse_txt(txt_path: Path):
    """Parse do arquivo TXT"""
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    lines = [ln.strip() for ln in text.splitlines()]

    # Nome do restaurante após "RELATÓRIO DE PREÇOS"
    restaurant = ""
    for i, ln in enumerate(lines):
        if "RELATÓRIO DE PREÇOS" in ln.upper():
            parts = ln.split("RELATÓRIO DE PREÇOS", 1)
            if len(parts) > 1:
                candidate = parts[1].strip()
                if candidate and not (candidate.startswith("*") and candidate.endswith("*")):
                    restaurant = candidate
                    break
            
            if not restaurant:
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()
                    if candidate and not (candidate.startswith("*") and candidate.endswith("*")):
                        restaurant = candidate
                        break
            break

    categories = []
    current = None
    total_items = 0

    for ln in lines:
        if not ln:
            continue
        if ln.startswith("*") and ln.endswith("*") and len(ln) >= 2:
            cat_name = ln.strip("*").strip()
            current = {"category": cat_name, "items": []}
            categories.append(current)
            continue

        if current is not None and " - R$" in ln:
            parts = ln.rsplit(" - R$", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                price = "R$ " + parts[1].strip()
                if PRICE_RE.search(ln):
                    current["items"].append({"name": name, "price": price})
                    total_items += 1

    model = "A" if total_items <= 30 else "B"
    return {
        "restaurant": restaurant,
        "model": model,
        "total_items": total_items,
        "categories": categories,
    }

def flatten_with_headers(categories):
    """Achata categorias em lista sequencial"""
    flat = []
    for c in categories:
        flat.append({"type": "cat", "text": c["category"]})
        for it in c["items"]:
            flat.append({"type": "item", "name": it["name"], "price": it["price"]})
    return flat

def split_two_columns_preserving_order(categories):
    """Divide em 2 colunas preservando ordem"""
    flat = flatten_with_headers(categories)
    n = len(flat)
    mid = n // 2
    if mid < n and flat[mid]["type"] == "item":
        k = mid
        while k > 0 and flat[k]["type"] != "cat":
            k -= 1
        if k > 0:
            mid = k
    col1 = flat[:mid]
    col2 = flat[mid:]
    if not col1:
        col1, col2 = col2, col1
    return col1, col2

def calculate_char_width_for_frame(frame_width_units, font_size_pt, use_monospace=False):
    """
    Calcula quantos caracteres (aproximadamente) cabem na largura do frame

    Args:
        frame_width_units: Largura do frame em unidades do CorelDRAW (polegadas)
        font_size_pt: Tamanho da fonte em pontos
        use_monospace: Se True, usa cálculo para fonte monoespaçada

    Returns:
        Número aproximado de caracteres que cabem na linha
    """
    # Conversões:
    # 1 polegada = 72 pontos

    frame_width_points = frame_width_units * 72  # Converter para pontos

    if use_monospace:
        # Courier New: largura ≈ 0.6 * font_size
        avg_char_width_points = font_size_pt * 0.6
    else:
        # Arial (proporcional): largura média ≈ 0.5 * font_size
        # Mas vamos usar 0.55 para ser mais conservador e evitar overflow
        avg_char_width_points = font_size_pt * 0.55

    chars_per_line = int(frame_width_points / avg_char_width_points)

    # Reduzir em 10% para margem de segurança
    chars_per_line = int(chars_per_line * 0.9)

    return chars_per_line

def compose_text_block(seq, use_dots=True, target_width=50, debug=False):
    """
    Compõe bloco de texto com categorias e itens

    Args:
        seq: Sequência de items e categorias
        use_dots: Se True, usa pontos para preencher espaço entre nome e preço
        target_width: Largura alvo em caracteres para alinhar preços
        debug: Se True, imprime debug info
    """
    out = []

    # Encontrar o maior nome e maior preço para calcular espaçamento
    if use_dots:
        max_name_length = 0
        max_price_length = 0
        item_count = 0
        for e in seq:
            if e["type"] == "item":
                max_name_length = max(max_name_length, len(e['name']))
                max_price_length = max(max_price_length, len(e['price']))
                item_count += 1

        if debug:
            print(f"    📊 DEBUG: target_width={target_width}, items={item_count}")
            print(f"    📊 DEBUG: max_name_length={max_name_length}, max_price_length={max_price_length}")

    for e in seq:
        if e["type"] == "cat":
            if out and out[-1] != "":
                out.append("")
            out.append(e["text"].upper())
        else:
            if use_dots:
                # Calcular quantos pontos colocar entre nome e preço
                name = e['name']
                price = e['price']

                # CRÍTICO: Todos os preços devem terminar na mesma posição
                # Posição final = target_width
                # Preço começa em: target_width - max_price_length
                # Nome termina em: (preço começa) - (espaço) - (pontos mínimos)

                # Espaço total disponível para nome + pontos (reservar espaço para o maior preço)
                available_for_name_and_dots = target_width - max_price_length - 1  # -1 para espaço antes do preço

                # Espaço usado pelo nome
                name_length = len(name)

                # Pontos necessários (mínimo 3)
                dots_count = max(3, available_for_name_and_dots - name_length - 1)  # -1 para espaço depois do nome
                dots = "." * dots_count

                # Preencher o preço à direita para que todos tenham o mesmo comprimento
                price_padded = price.rjust(max_price_length)

                line = f"{name} {dots} {price_padded}"
                out.append(line)

                # Debug: mostrar primeira linha
                if debug and len(out) <= 3:
                    print(f"    📝 DEBUG linha {len(out)}: [{line}] (len={len(line)})")
            else:
                # Fallback: usar tab (mas não funcionará sem TabStops)
                out.append(f"{e['name']}\t{e['price']}")

    return "\r\n".join(out)

def to_units(doc, value_mm):
    """Converte mm para unidades do documento"""
    cdrMillimeter = 7
    try:
        return float(doc.ToUnits(float(value_mm), cdrMillimeter))
    except Exception:
        return float(value_mm * 0.0393701)

def ensure_area_frames(page, doc, model):
    """Calcula áreas para caixas de texto"""
    try:
        pw = float(page.SizeWidth)
        ph = float(page.SizeHeight)
    except Exception:
        pw, ph = 8.27, 11.69

    margin_mm = 12.0
    header_mm = 40.0
    gutter_mm = 8.0

    if pw < 20:
        margin = margin_mm / 25.4
        header = header_mm / 25.4
        gutter = gutter_mm / 25.4
    else:
        margin = to_units(doc, margin_mm)
        header = to_units(doc, header_mm)
        gutter = to_units(doc, gutter_mm)

    left = margin
    right = pw - margin
    bottom = margin
    top = ph - header

    if left >= right or bottom >= top:
        left, bottom, right, top = 0.5, 0.5, 7.77, 10.69

    frames = []
    if model == "A":
        frames.append((left, bottom, right, top))
    else:
        col_w = (right - left - gutter) / 2.0
        frames.append((left, bottom, left + col_w, top))
        frames.append((left + col_w + gutter, bottom, right, top))
    
    return frames

def create_paragraph_text(layer, x1, y1, x2, y2):
    """Cria caixa de texto de parágrafo com configuração inicial"""
    try:
        left = min(float(x1), float(x2))
        right = max(float(x1), float(x2))
        bottom = min(float(y1), float(y2))
        top = max(float(y1), float(y2))

        shape = layer.CreateParagraphText(left, bottom, right, top, "")

        # CRÍTICO: Desabilitar FitToFrame IMEDIATAMENTE após criação
        # Isso evita que o CorelDRAW ajuste automaticamente o texto
        try:
            shape.Text.FitToFrame = False
        except Exception:
            pass

        # Forçar alinhamento à esquerda desde o início
        try:
            shape.Text.Alignment = 0  # cdrLeftAlignment
        except Exception:
            pass

        return shape
    except Exception as e:
        print(f"    ❌ ERRO ao criar caixa: {e}")
        raise

def apply_text_style_and_tabs(doc, shape, font_name="Arial", font_size_pt=10.0, right_tab_margin_mm=3.0):
    """Aplica estilo simplificado usando apenas propriedades que funcionam"""
    try:
        tr = shape.Text.Story

        # Fonte e tamanho
        try:
            tr.Font = str(font_name)
            tr.Size = float(font_size_pt)
            print(f"    ✅ Fonte {font_name} {font_size_pt}pt")
        except Exception as e:
            print(f"    ⚠ Erro na fonte: {e}")

        # Alinhamento à ESQUERDA (0 = cdrLeftAlignment)
        try:
            tr.Alignment = 0
            print("    ✅ Alinhamento à esquerda")
        except Exception as e:
            print(f"    ⚠ Erro no alinhamento: {e}")

        # Cor do texto
        try:
            tr.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
        except Exception:
            pass

        # NOTA: TabStops não está disponível na API COM desta versão do CorelDRAW
        # Solução: O texto já vem formatado com pontos (.) para alinhar preços
        print("    ℹ️ Usando pontos de preenchimento para alinhar preços")

        # Negrito para categorias
        try:
            text = tr.Text
            lines = text.split('\r\n')
            char_pos = 0
            for line in lines:
                if line and line.isupper() and 'R$' not in line:
                    start = char_pos + 1
                    end = start + len(line) - 1
                    try:
                        tr.Characters.Range(start, end).Bold = True
                        tr.Characters.Range(start, end).Size = float(font_size_pt + 1)
                    except Exception:
                        pass
                char_pos += len(line) + 2
        except Exception as e:
            print(f"    ⚠ Negrito falhou: {e}")

    except Exception as e:
        print(f"    ⚠ Erro ao aplicar estilo: {e}")

def fill_paragraph(shape, text_block):
    """Preenche caixa de texto"""
    try:
        shape.Text.Story.Text = str(text_block)
    except Exception as e:
        print(f"    ⚠ Erro ao preencher texto: {e}")
        try:
            shape.Text.Story.Replace(shape.Text.Story.Text, str(text_block), False, False)
        except Exception as e2:
            print(f"    ❌ Falha total ao preencher: {e2}")

def write_auditoria(outdir: Path, data):
    """Salva logs de auditoria"""
    rows = [["tipo", "valor"]]
    rows.append(["restaurant", data["restaurant"]])
    rows.append(["model", data["model"]])
    rows.append(["total_items", str(data["total_items"])])
    for c in data["categories"]:
        rows.append(["categoria", c["category"]])
        for it in c["items"]:
            rows.append(["item", f"{it['name']}|{it['price']}"])

    aud = outdir / "auditoria.csv"
    with aud.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows)
    (outdir / "parsed.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def cleanup_com():
    """Finaliza COM na thread atual"""
    try:
        pythoncom.CoUninitialize()
    except Exception:
        pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Caminho do teste_input.txt")
    ap.add_argument("--tplA", required=True, help="Modelo A (CDR, 1 coluna)")
    ap.add_argument("--tplB", required=True, help="Modelo B (CDR, 2 colunas)")
    ap.add_argument("--outdir", required=True, help="Pasta de saída")
    ap.add_argument("--font", default="Arial", help="Fonte para o conteúdo")
    ap.add_argument("--size", type=float, default=10.0, help="Tamanho da fonte (pt)")
    args = ap.parse_args()

    in_path = Path(args.input).resolve()
    tplA = Path(args.tplA).resolve()
    tplB = Path(args.tplB).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        print(f"❌ Input não encontrado: {in_path}")
        sys.exit(2)
    if not tplA.exists() or not tplB.exists():
        print("❌ Modelos CDR não encontrados (tplA/tplB).")
        sys.exit(3)

    print("=" * 60)
    print("🚀 INICIANDO GERAÇÃO DE CARDÁPIO")
    print("=" * 60)

    data = parse_txt(in_path)
    write_auditoria(outdir, data)
    
    print(f"   ✅ Restaurante: {data['restaurant']}")
    print(f"   ✅ Total de itens: {data['total_items']}")
    print(f"   ✅ Modelo: {data['model']}")

    corel = get_corel_app(visible=False)
    print("   ✅ CorelDRAW inicializado")

    tpl = str(tplA if data["model"] == "A" else tplB)
    doc = corel.OpenDocument(tpl)
    page = doc.ActivePage
    layer = page.ActiveLayer

    # Limpar textos existentes do template
    print("   🔍 Limpando textos do template...")
    texts_removed = 0
    try:
        shapes = page.Shapes
        total_shapes = shapes.Count
        print(f"   📊 Template tem {total_shapes} shapes")

        for i in range(shapes.Count, 0, -1):
            try:
                s = shapes.Item(i)
                # Tipo 6 = cdrTextShape (inclui artistic text e paragraph text)
                if s.Type == 6:
                    s.Delete()
                    texts_removed += 1
            except Exception:
                pass

        print(f"   ✅ {texts_removed} textos removidos")
    except Exception as e:
        print(f"   ⚠ Erro ao limpar template: {e}")
    
    # Criar título
    try:
        pw = float(page.SizeWidth)
        ph = float(page.SizeHeight)
        
        title_x = pw / 2.0
        title_y = ph - 1.0
        
        title_shape = layer.CreateArtisticText(0.0, float(title_y), str(data["restaurant"]))
        title_shape.Text.Story.Font = "Arial"
        title_shape.Text.Story.Size = float(24)
        title_shape.Text.Story.Bold = True
        
        try:
            title_shape.Text.Story.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
        except Exception:
            pass
        
        try:
            text_width = float(title_shape.SizeWidth)
            title_shape.LeftX = title_x - (text_width / 2.0)
        except Exception:
            pass
        
    except Exception as e:
        print(f"   ❌ Erro ao criar título: {e}")

    # Criar conteúdo
    print("   📝 Criando conteúdo do cardápio...")
    frames = ensure_area_frames(page, doc, data["model"])

    shapes_before = page.Shapes.Count
    print(f"   📊 Shapes antes: {shapes_before}")

    if data["model"] == "A":
        print("   📄 Modelo A: 1 coluna")
        left, bottom, right, top = frames[0]
        frame_width = abs(right - left)

        # Calcular largura em caracteres
        target_width = calculate_char_width_for_frame(frame_width, args.size)
        print(f"   📏 Largura da caixa: {frame_width:.2f} unidades = ~{target_width} caracteres")

        seq = flatten_with_headers(data["categories"])
        print("   📝 Gerando texto (com debug)...")
        text_block = compose_text_block(seq, use_dots=True, target_width=target_width, debug=True)

        shp = create_paragraph_text(layer, left, bottom, right, top)
        fill_paragraph(shp, text_block)
        apply_text_style_and_tabs(doc, shp, font_name=args.font, font_size_pt=args.size)
    else:
        print("   📄 Modelo B: 2 colunas")
        col1, col2 = split_two_columns_preserving_order(data["categories"])

        frame1, frame2 = frames
        left1, bottom1, right1, top1 = frame1
        left2, bottom2, right2, top2 = frame2

        # Calcular largura para cada coluna
        frame_width1 = abs(right1 - left1)
        frame_width2 = abs(right2 - left2)
        target_width1 = calculate_char_width_for_frame(frame_width1, args.size)
        target_width2 = calculate_char_width_for_frame(frame_width2, args.size)

        print(f"   📏 Coluna 1: {frame_width1:.2f} unidades = ~{target_width1} caracteres")
        print(f"   📏 Coluna 2: {frame_width2:.2f} unidades = ~{target_width2} caracteres")

        print("   📝 Gerando texto coluna 1 (com debug)...")
        tb1 = compose_text_block(col1, use_dots=True, target_width=target_width1, debug=True)
        print("   📝 Gerando texto coluna 2 (com debug)...")
        tb2 = compose_text_block(col2, use_dots=True, target_width=target_width2, debug=True)

        print("   📝 Coluna 1...")
        shp1 = create_paragraph_text(layer, left1, bottom1, right1, top1)
        fill_paragraph(shp1, tb1)
        apply_text_style_and_tabs(doc, shp1, font_name=args.font, font_size_pt=args.size)

        print("   📝 Coluna 2...")
        shp2 = create_paragraph_text(layer, left2, bottom2, right2, top2)
        fill_paragraph(shp2, tb2)
        apply_text_style_and_tabs(doc, shp2, font_name=args.font, font_size_pt=args.size)

    shapes_after = page.Shapes.Count
    shapes_created = shapes_after - shapes_before
    print(f"   📊 Shapes depois: {shapes_after}")
    print(f"   ✅ {shapes_created} shapes criadas")

    # Salvar e exportar
    out_cdr = outdir / "cardapio_output.cdr"
    out_pdf = outdir / "cardapio_output.pdf"
    out_png = outdir / "cardapio_output.png"

    print("\n   💾 Salvando arquivos...")

    try:
        import os
        cdr_path = os.path.abspath(str(out_cdr))
        print(f"   🔍 Exportando CDR para: {cdr_path}")

        # Tentar exportar como CDR (mais confiável)
        try:
            doc.Export(cdr_path, 48, 0)  # 48 = cdrCDR
            print(f"   ✅ CDR: {out_cdr.name}")
        except Exception as e1:
            print(f"   ⚠ Export falhou: {e1}")
            # Fallback: tentar SaveAs
            doc.SaveAs(cdr_path)
            print(f"   ✅ CDR: {out_cdr.name} (via SaveAs)")
    except Exception as e:
        print(f"   ⚠ CDR: {e}")

    try:
        pdf_path = os.path.abspath(str(out_pdf))
        print(f"   🔍 Gerando PDF em: {pdf_path}")
        doc.PublishToPDF(pdf_path)
        print(f"   ✅ PDF: {out_pdf.name}")
    except Exception as e:
        print(f"   ⚠ PDF: {e}")

    try:
        png_path = os.path.abspath(str(out_png))
        print(f"   🔍 Exportando PNG em: {png_path}")
        doc.Export(png_path, 13, 1)
        print(f"   ✅ PNG: {out_png.name}")
    except Exception as e:
        print(f"   ⚠ PNG: {e}")

    try:
        doc.Close(False)
        corel.Quit()
        print("   ✅ CorelDRAW fechado")
    except Exception:
        pass
    
    # Limpar COM
    cleanup_com()

    print("\n✅ CONCLUÍDO!")

if __name__ == "__main__":
    main()