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
except ImportError:
    print("pywin32 não encontrado. Instale com: pip install pywin32")
    sys.exit(1)

def get_corel_app(visible=False):
    """Inicializa CorelDRAW COM"""
    try:
        app = win32.GetActiveObject("CorelDRAW.Application")
        app.Visible = visible
        return app
    except Exception:
        pass
    for pid in [
        "CorelDRAW.Application.25",
        "CorelDRAW.Application",
        "CorelDRAW.Application.26",
        "CorelDRAW.Application.24",
    ]:
        try:
            app = win32.Dispatch(pid)
            app.Visible = visible
            return app
        except Exception:
            continue
    raise RuntimeError("CorelDRAW COM indisponível.")

PRICE_RE = re.compile(r"\s-\s*R\$\s*([\d\.,]+)\s*$", flags=re.IGNORECASE)

def parse_txt(txt_path: Path):
    """Parse do arquivo TXT"""
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    lines = [ln.strip() for ln in text.splitlines()]

    # Nome do restaurante após "RELATÓRIO DE PREÇOS"
    restaurant = ""
    for i, ln in enumerate(lines):
        if "RELATÓRIO DE PREÇOS" in ln.upper():
            # Primeiro tenta extrair da mesma linha (depois de "RELATÓRIO DE PREÇOS")
            parts = ln.split("RELATÓRIO DE PREÇOS", 1)
            if len(parts) > 1:
                candidate = parts[1].strip()
                if candidate and not (candidate.startswith("*") and candidate.endswith("*")):
                    restaurant = candidate
                    break
            
            # Se não encontrou na mesma linha, procura nas próximas
            if not restaurant:
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()
                    # Pular linhas vazias e categorias (que começam/terminam com *)
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
        # Categoria entre *asteriscos*
        if ln.startswith("*") and ln.endswith("*") and len(ln) >= 2:
            cat_name = ln.strip("*").strip()
            current = {"category": cat_name, "items": []}
            categories.append(current)
            continue

        # Item - Preço
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
    # Evita começar col2 por item sem categoria
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

def compose_text_block(seq):
    """Compõe bloco de texto com categorias e itens"""
    out = []
    for e in seq:
        if e["type"] == "cat":
            if out and out[-1] != "":
                out.append("")  # Linha em branco antes da categoria
            out.append(e["text"].upper())
        else:
            # Item com tab para alinhar preço
            out.append(f"{e['name']}\t{e['price']}")
    
    # Usar \r\n (Windows line ending) para garantir quebras de linha
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
        # SizeWidth/SizeHeight já vêm nas unidades do documento
        pw = float(page.SizeWidth)
        ph = float(page.SizeHeight)
    except Exception:
        # Fallback: A4 em polegadas
        pw, ph = 8.27, 11.69

    # Converter margens de mm para as mesmas unidades da página
    margin_mm = 12.0
    header_mm = 40.0
    gutter_mm = 8.0

    # Se a página é pequena (< 20), provavelmente está em polegadas
    # Se é grande (> 100), está em points ou outra unidade
    if pw < 20:
        # Página em polegadas - converter mm para polegadas
        margin = margin_mm / 25.4
        header = header_mm / 25.4
        gutter = gutter_mm / 25.4
    else:
        # Usar conversão normal
        margin = to_units(doc, margin_mm)
        header = to_units(doc, header_mm)
        gutter = to_units(doc, gutter_mm)

    # No CorelDRAW: origem no canto inferior esquerdo, Y cresce para cima
    left = margin
    right = pw - margin
    bottom = margin
    top = ph - header

    print(f"  📐 Página: {pw:.2f} x {ph:.2f}")
    print(f"  📐 Margens: L={left:.2f} R={right:.2f} B={bottom:.2f} T={top:.2f}")

    if left >= right or bottom >= top:
        print("  ⚠ ERRO: Coordenadas inválidas! Usando valores padrão...")
        left, bottom, right, top = 0.5, 0.5, 7.77, 10.69

    frames = []
    if model == "A":
        # CreateParagraphText(Left, Bottom, Right, Top)
        frames.append((left, bottom, right, top))
    else:
        col_w = (right - left - gutter) / 2.0
        # Coluna 1: da esquerda até o meio
        frames.append((left, bottom, left + col_w, top))
        # Coluna 2: do meio+gutter até a direita
        frames.append((left + col_w + gutter, bottom, right, top))
    
    return frames

def find_top_title_shape(page):
    """Encontra o shape de texto mais alto (título) ou que contenha palavras-chave"""
    try:
        shapes = page.Shapes
    except Exception:
        return None
    
    top_shape, top_y = None, -1e9
    keyword_shape = None
    
    for i in range(1, shapes.Count + 1):
        s = shapes.Item(i)
        try:
            if s.Type == 3:  # cdrTextShape
                # Verificar se contém palavras-chave de título
                try:
                    text = s.Text.Story.Text.upper()
                    if "NOME DO RESTAURANTE" in text or "RESTAURANTE" in text:
                        keyword_shape = s
                        print(f"    🔍 Encontrado shape com keyword: '{s.Text.Story.Text}'")
                except Exception:
                    pass
                
                # Também rastrear o shape mais alto
                y = float(s.TopY)
                if y > top_y:
                    top_y, top_shape = y, s
        except Exception:
            continue
    
    # Priorizar shape com keyword, senão o mais alto
    return keyword_shape if keyword_shape else top_shape

def create_paragraph_text(layer, x1, y1, x2, y2):
    """Cria caixa de texto de parágrafo
    No CorelDRAW: CreateParagraphText(Left, Bottom, Right, Top)
    """
    # Converter para float explicitamente
    try:
        # Garantir que Left < Right e Bottom < Top
        left = min(float(x1), float(x2))
        right = max(float(x1), float(x2))
        bottom = min(float(y1), float(y2))
        top = max(float(y1), float(y2))
        
        shape = layer.CreateParagraphText(left, bottom, right, top, "")
        
        largura = right - left
        altura = top - bottom
        print(f"    ✓ Caixa criada: {largura:.2f} x {altura:.2f} (L={left:.0f} B={bottom:.0f} R={right:.0f} T={top:.0f})")
        return shape
    except Exception as e:
        print(f"    ❌ ERRO ao criar caixa: {e}")
        raise

def apply_text_style_and_tabs(doc, shape, font_name="Arial", font_size_pt=10.0, right_tab_margin_mm=3.0):
    """Aplica estilo e tabs ao texto"""
    try:
        tr = shape.Text.Story
        
        # Estilo padrão para todo o texto
        tr.Characters.All.Font = str(font_name)
        tr.Characters.All.Size = float(font_size_pt)
        
        # Cor preta explícita
        try:
            tr.Characters.All.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
        except Exception:
            pass
        
        # TAB à direita com líder '.'
        try:
            shape.Text.TabStops.Clear()
            pos = abs(float(shape.SizeWidth)) - (right_tab_margin_mm / 25.4)  # mm para polegadas
            shape.Text.TabStops.Add(float(pos), 2, ".")
        except Exception as e:
            print(f"    ⚠ TabStop falhou: {e}")
        
        # Aplicar negrito nas categorias (linhas em MAIÚSCULO)
        try:
            text = tr.Text
            lines = text.split('\r\n')
            char_pos = 0
            
            for line in lines:
                if line and line.isupper() and not line.startswith('R$'):
                    # Esta é uma categoria - aplicar negrito
                    start = char_pos + 1  # Corel é 1-indexed
                    end = start + len(line) - 1
                    
                    try:
                        tr.Characters.Range(start, end).Bold = True
                        tr.Characters.Range(start, end).Size = float(font_size_pt + 1)  # +1pt
                    except Exception:
                        pass
                
                char_pos += len(line) + 2  # +2 para \r\n
        except Exception as e:
            print(f"    ⚠ Negrito falhou: {e}")
        
        print(f"    ✓ Estilo aplicado: {font_name} {font_size_pt}pt")
    except Exception as e:
        print(f"    ⚠ Erro ao aplicar estilo: {e}")

def fill_paragraph(shape, text_block):
    """Preenche caixa de texto"""
    try:
        shape.Text.Story.Text = str(text_block)
        print(f"    ✓ Texto preenchido: {len(text_block)} chars, {text_block.count(chr(10))+1} linhas")
    except Exception as e:
        print(f"    ⚠ Erro ao preencher texto: {e}")
        try:
            shape.Text.Story.Replace(shape.Text.Story.Text, str(text_block), False, False)
            print(f"    ✓ Texto preenchido (método alternativo)")
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

    # Parse
    print("\n1️⃣ Parsing do arquivo...")
    data = parse_txt(in_path)
    write_auditoria(outdir, data)
    
    print(f"   ✅ Restaurante: {data['restaurant']}")
    print(f"   ✅ Total de itens: {data['total_items']}")
    print(f"   ✅ Modelo: {data['model']} ({'1 coluna' if data['model']=='A' else '2 colunas'})")
    print(f"   ✅ Categorias: {len(data['categories'])}")

    # CorelDRAW
    print("\n2️⃣ Abrindo CorelDRAW...")
    corel = get_corel_app(visible=True)  # Visível para debug
    print("   ✅ CorelDRAW inicializado")

    # Abre template
    tpl = str(tplA if data["model"] == "A" else tplB)
    print(f"\n3️⃣ Abrindo template: {Path(tpl).name}")
    doc = corel.OpenDocument(tpl)
    page = doc.ActivePage
    layer = page.ActiveLayer
    print(f"   ✅ Template aberto")

    # Atualiza título
    print("\n4️⃣ Preparando título...")
    
    # Deletar TODOS os textos existentes no template
    try:
        shapes = page.Shapes
        deleted_count = 0
        for i in range(shapes.Count, 0, -1):  # Iterar de trás pra frente
            s = shapes.Item(i)
            try:
                if s.Type == 3:  # cdrTextShape
                    s.Delete()
                    deleted_count += 1
            except Exception:
                pass
        print(f"   🗑️ {deleted_count} texto(s) do template removido(s)")
    except Exception as e:
        print(f"   ⚠ Erro ao limpar template: {e}")
    
    # Criar título novo
    print("   📝 Criando título...")
    try:
        # Posição: centralizado, no topo (1" do topo da página)
        pw = float(page.SizeWidth)
        ph = float(page.SizeHeight)
        
        title_x = pw / 2.0
        title_y = ph - 1.0  # 1 polegada do topo
        
        # Criar texto artístico temporário para calcular largura
        title_shape = layer.CreateArtisticText(0.0, float(title_y), str(data["restaurant"]))
        
        # Estilizar primeiro
        title_shape.Text.Story.Font = "Arial"
        title_shape.Text.Story.Size = float(24)
        title_shape.Text.Story.Bold = True
        
        # Cor preta
        try:
            title_shape.Text.Story.Fill.UniformColor.CMYKAssign(0, 0, 0, 100)
        except Exception:
            pass
        
        # Agora que sabemos a largura, centralizar
        try:
            text_width = float(title_shape.SizeWidth)
            title_shape.LeftX = title_x - (text_width / 2.0)
        except Exception:
            # Se falhar, usar alinhamento de texto
            try:
                title_shape.Text.Story.Alignment = 2  # Center
                title_shape.CenterX = title_x
            except Exception:
                pass
        
        print(f"   ✅ Título criado e centralizado: '{data['restaurant']}'")
    except Exception as e:
        print(f"   ❌ Erro ao criar título: {e}")

    # Cria conteúdo
    print(f"\n5️⃣ Criando conteúdo ({data['model']})...")
    frames = ensure_area_frames(page, doc, data["model"])
    
    if data["model"] == "A":
        print("   📝 Modelo A - 1 coluna")
        seq = flatten_with_headers(data["categories"])
        text_block = compose_text_block(seq)
        left, bottom, right, top = frames[0]
        
        print(f"   🔧 Criando coluna única")
        shp = create_paragraph_text(layer, left, bottom, right, top)
        apply_text_style_and_tabs(doc, shp, font_name=args.font, font_size_pt=args.size)
        fill_paragraph(shp, text_block)
        print("   ✅ Conteúdo preenchido")
    else:
        print("   📝 Modelo B - 2 colunas")
        col1, col2 = split_two_columns_preserving_order(data["categories"])
        tb1 = compose_text_block(col1)
        tb2 = compose_text_block(col2)

        frame1, frame2 = frames
        left1, bottom1, right1, top1 = frame1
        left2, bottom2, right2, top2 = frame2
        
        print(f"   🔧 Coluna 1")
        shp1 = create_paragraph_text(layer, left1, bottom1, right1, top1)
        apply_text_style_and_tabs(doc, shp1, font_name=args.font, font_size_pt=args.size)
        fill_paragraph(shp1, tb1)
        
        print(f"   🔧 Coluna 2")
        shp2 = create_paragraph_text(layer, left2, bottom2, right2, top2)
        apply_text_style_and_tabs(doc, shp2, font_name=args.font, font_size_pt=args.size)
        fill_paragraph(shp2, tb2)
        print("   ✅ Conteúdo preenchido (2 colunas)")

    # Salvar e exportar
    print("\n6️⃣ Salvando arquivos...")
    out_cdr = outdir / "cardapio_output.cdr"
    out_pdf = outdir / "cardapio_output.pdf"
    out_png = outdir / "cardapio_output.png"

    try:
        # Converter Path para string com barras invertidas
        cdr_path = str(out_cdr.absolute()).replace('/', '\\')
        doc.SaveAs(cdr_path)
        print(f"   ✅ CDR: {out_cdr.name}")
    except Exception as e:
        print(f"   ⚠ CDR: {e}")

    try:
        pdf_path = str(out_pdf.absolute()).replace('/', '\\')
        doc.PublishToPDF(pdf_path)
        print(f"   ✅ PDF: {out_pdf.name}")
    except Exception as e:
        print(f"   ⚠ PDF: {e}")

    try:
        png_path = str(out_png.absolute()).replace('/', '\\')
        # Usar valores numéricos em vez de constantes
        # cdrPNG = 13, cdrCurrentPage = 1
        doc.Export(png_path, 13, 1)
        print(f"   ✅ PNG: {out_png.name}")
    except Exception as e:
        print(f"   ⚠ PNG: {e}")

    # Fechar
    print("\n7️⃣ Finalizando...")
    try:
        doc.Close(False)
        corel.Quit()
        print("   ✅ CorelDRAW fechado")
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO!")
    print("=" * 60)
    print(f"📁 Saídas em: {outdir}")
    print(f"   • {out_cdr.name}")
    print(f"   • {out_pdf.name}")
    print(f"   • {out_png.name}")
    print(f"   • parsed.json")
    print(f"   • auditoria.csv")

if __name__ == "__main__":
    main()