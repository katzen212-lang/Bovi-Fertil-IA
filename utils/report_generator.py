import os
from fpdf import FPDF


class PDFReport(FPDF):

  def header(self):
    self.set_font("helvetica", "B", 16)
    self.set_text_color(20, 80, 40)
    self.cell(
        0, 10, "BOVI-FERTIL-IA - REPORTE DE ANALISIS SEMINAL", 0, 1, "CENTER"
    )

    self.set_font("helvetica", "I", 10)
    self.set_text_color(100, 100, 100)
    self.cell(
        0,
        6,
        "Sistema Inteligente de Evaluacion Morfologica y Motilidad Bovina",
        0,
        1,
        "CENTER",
    )
    self.ln(5)

    self.set_draw_color(40, 140, 70)
    self.set_line_width(0.8)
    self.line(10, self.get_y(), 200, self.get_y())
    self.ln(8)

  def footer(self):
    self.set_y(-15)
    self.set_font("helvetica", "I", 8)
    self.set_text_color(120, 120, 120)
    self.cell(
        0,
        10,
        f"Pagina {self.page_no()} | Generado por Bovi-Fertil-IA - Universidad"
        " Tecnica de Machala",
        0,
        0,
        "CENTER",
    )


def generate_seminal_report(
    sample_data: dict, metrics: dict, morphology_counts: dict, output_path: str
):
  pdf = PDFReport(orientation="P", unit="mm", format="A4")
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()

  # --- 1. DATOS DE LA MUESTRA ---
  pdf.set_font("helvetica", "B", 12)
  pdf.set_text_color(30, 30, 30)
  pdf.cell(0, 8, "1. Datos de Identificacion de la Muestra", 0, 1, "L")

  pdf.set_font("helvetica", "", 10)
  col_width = 95
  row_height = 7

  sample_info = [
      ("Codigo del Toro / Donador:", sample_data.get("bull_code", "N/A")),
      ("Raza:", sample_data.get("breed", "N/A")),
      ("Fecha de Recoleccion:", sample_data.get("collection_date", "N/A")),
      ("Analista / Evaluador:", sample_data.get("analyst", "N/A")),
  ]

  for i, (k, v) in enumerate(sample_info):
    pdf.cell(col_width, row_height, f"{k} {v}", border=1)
    if i % 2 != 0:
      pdf.ln()
  if len(sample_info) % 2 != 0:
    pdf.ln()
  pdf.ln(5)

  # --- 2. PARAMETROS GENERALES Y MOTILIDAD ---
  pdf.set_font("helvetica", "B", 12)
  pdf.cell(0, 8, "2. Parametros Generales y Motilidad", 0, 1, "L")

  pdf.set_font("helvetica", "", 10)
  pdf.cell(
      120,
      row_height,
      f"Concentracion Espermatica: {metrics.get('concentration', 0)}"
      " mill/mL",
      border=1,
  )
  pdf.cell(
      70,
      row_height,
      f"Motilidad Progresiva: {metrics.get('progressive_motility', 0)}%",
      border=1,
  )
  pdf.ln()
  pdf.cell(
      190,
      row_height,
      f"Dosis Seminales Viables Estimadas: {metrics.get('viable_doses', 0)}"
      " pajuelas",
      border=1,
  )
  pdf.ln(8)

  # --- 3. ANALISIS MORFOLOGICO (YOLOv8-Segmentation) ---
  pdf.set_font("helvetica", "B", 12)
  pdf.cell(
      0,
      8,
      "3. Evaluacion Morfologica por Categoria (9 Clases YOLOv8)",
      0,
      1,
      "L",
  )

  pdf.set_font("helvetica", "B", 10)
  pdf.set_fill_color(230, 240, 235)
  pdf.cell(130, 7, "Categoria Morfologica", border=1, fill=True)
  pdf.cell(60, 7, "Conteo / Porcentaje", border=1, fill=True, ln=1)

  pdf.set_font("helvetica", "", 10)
  categories = [
      ("Normal", morphology_counts.get("normal", 0)),
      ("Cabeza Suelta (Loose-Head)", morphology_counts.get("loose-head", 0)),
      ("Cola Suelta (Loose-Tail)", morphology_counts.get("loose-tail", 0)),
      (
          "Gota Proximal (Proximal-Droplet)",
          morphology_counts.get("proximal-droplet", 0),
      ),
      (
          "Gota Distal (Distal-Droplet)",
          morphology_counts.get("distal-droplet", 0),
      ),
      ("Cola Enroscada (Coiled-Tail)", morphology_counts.get("coiled-tail", 0)),
      (
          "Cola Doble / Plegada (Folded-Tail)",
          morphology_counts.get("folded-tail", 0),
      ),
      ("Aglutinacion (Agglutination)", morphology_counts.get("agglutination", 0)),
      (
          "Particulas / Escombros (Dirt-Particles)",
          morphology_counts.get("dirt-particles", 0),
      ),
  ]

  for cat_name, count in categories:
    pdf.cell(130, 6, cat_name, border=1)
    pdf.cell(60, 6, str(count), border=1, ln=1)

  pdf.ln(15)

  # --- 4. FIRMAS Y VALIDACIÓN ---
  pdf.set_font("helvetica", "B", 10)
  pdf.cell(95, 5, "_" * 35, 0, 0, "CENTER")
  pdf.cell(95, 5, "_" * 35, 0, 1, "CENTER")

  pdf.cell(95, 6, "Firma del Evaluador", 0, 0, "CENTER")
  pdf.cell(95, 6, "Control de Calidad / Laboratorio", 0, 1, "CENTER")

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  pdf.output(output_path)
  return output_path