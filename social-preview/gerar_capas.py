"""Gera as imagens de social preview (1280x640) dos 6 projetos principais no estilo do perfil."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 640
SAIDA = Path(sys.argv[1])
SAIDA.mkdir(parents=True, exist_ok=True)

F = "C:/Windows/Fonts/"
fonte = lambda nome, tam: ImageFont.truetype(F + nome, tam)
F_TITULO = fonte("segoeuib.ttf", 70)
F_TEXTO = fonte("segoeui.ttf", 30)
F_ROTULO = fonte("seguisb.ttf", 24)
F_CHIP = fonte("consolab.ttf", 22)
F_RODAPE = fonte("consola.ttf", 24)
F_AUTOR = fonte("seguisb.ttf", 26)

CORES = ((15, 32, 39), (32, 58, 67), (44, 83, 100))  # 0f2027 → 203a43 → 2c5364 (banner do perfil)
BRANCO = (255, 255, 255)
CINZA = (176, 196, 205)

PROJETOS = [
    ("erp-bi-dashboard", "ERP · SAP & TOTVS", (54, 188, 247),
     "ERP BI Dashboard",
     "Dashboard BI unificado SAP e TOTVS Protheus com datasets prontos para Power BI",
     ["Python", "SAP", "TOTVS Protheus", "Power BI"]),
    ("health-data-platform", "ENGENHARIA DE DADOS", (122, 162, 247),
     "Health Data Platform",
     "Plataforma completa de dados de saúde, pronta com um docker compose up",
     ["FastAPI", "Airflow", "PostgreSQL", "Grafana", "Prometheus"]),
    ("sap-data-extractor-pipeline", "ERP · SAP & TOTVS", (54, 188, 247),
     "SAP Data Extractor",
     "Pipeline ETL dos módulos SAP MM/SD/FI via RFC/BAPI até o PostgreSQL",
     ["Python", "RFC/BAPI", "Pandas", "PostgreSQL"]),
    ("erp-migration-toolkit", "ERP · SAP & TOTVS", (54, 188, 247),
     "ERP Migration Toolkit",
     "Migração de dados SAP → TOTVS Protheus com validação e audit trail",
     ["Python", "SAP", "TOTVS Protheus", "ETL"]),
    ("multicloud-emulation-lab", "INFRAESTRUTURA · CLOUD", (158, 206, 106),
     "Multi-Cloud Emulation Lab",
     "Infraestrutura multi-cloud local, 100% em Docker, sem gastar com nuvem",
     ["Docker", "LocalStack", "Azurite", "Supabase", "PowerShell"]),
    ("observability-platform", "OBSERVABILIDADE", (247, 118, 142),
     "Observability Platform",
     "Métricas de jobs Control-M, infraestrutura Linux e logs com score de saúde e alertas",
     ["Python", "Control-M", "Grafana", "LocalStack", "Azurite"]),
]


def fundo():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for x in range(W):
        for y in range(H):
            t = (x / W) * 0.7 + (y / H) * 0.3
            a, b = (CORES[0], CORES[1]) if t < 0.5 else (CORES[1], CORES[2])
            k = t * 2 if t < 0.5 else (t - 0.5) * 2
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
    return img


def grade(d):
    for x in range(0, W, 40):
        for y in range(0, H, 40):
            d.point((x, y), fill=(255, 255, 255, 28))


def onda(img, cor):
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    for i, (amp, fase, alfa) in enumerate(((22, 0.0, 70), (16, 1.7, 45))):
        base = H - 70 + i * 18
        pts = [(x, base + amp * math.sin(x / 160 + fase)) for x in range(0, W + 1, 8)]
        d.polygon(pts + [(W, H), (0, H)], fill=(*cor, alfa))
    img.alpha_composite(camada)


def quebra(texto, fonte_, largura, d):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if d.textlength(teste, font=fonte_) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    return linhas + [atual]


def capa(repo, rotulo, cor, titulo, texto, chips):
    img = fundo().convert("RGBA")

    # brilho suave da cor da categoria no canto
    brilho = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(brilho).ellipse((W - 420, -260, W + 220, 300), fill=(*cor, 60))
    img.alpha_composite(brilho.filter(ImageFilter.GaussianBlur(90)))
    onda(img, cor)

    # o Draw "RGBA" só mistura a transparência sobre imagem RGB
    img = img.convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    grade(d)

    x0 = 80
    d.rounded_rectangle((x0, 78, x0 + 8, 118), radius=4, fill=cor)
    d.text((x0 + 24, 80), rotulo, font=F_ROTULO, fill=cor)

    d.text((x0, 140), titulo, font=F_TITULO, fill=BRANCO)

    y = 250
    for linha in quebra(texto, F_TEXTO, W - 2 * x0, d)[:2]:
        d.text((x0, y), linha, font=F_TEXTO, fill=CINZA)
        y += 44

    x, y = x0, 370
    for c in chips:
        w = d.textlength(c, font=F_CHIP) + 36
        if x + w > W - x0:
            break
        d.rounded_rectangle((x, y, x + w, y + 46), radius=23, fill=(*cor, 38), outline=(*cor, 200), width=2)
        d.text((x + 18, y + 10), c, font=F_CHIP, fill=BRANCO)
        x += w + 14

    d.text((x0, H - 140), f"github.com/RafaGarciaDev/{repo}", font=F_RODAPE, fill=(*BRANCO, 200))
    autor = "Rafael Garcia"
    d.text((W - x0 - d.textlength(autor, font=F_AUTOR), H - 142), autor, font=F_AUTOR, fill=BRANCO)

    destino = SAIDA / f"{repo}.png"
    img.convert("RGB").save(destino, optimize=True)
    return destino


for p in PROJETOS:
    arq = capa(*p)
    print(arq.name, Image.open(arq).size, f"{arq.stat().st_size // 1024} KB")
