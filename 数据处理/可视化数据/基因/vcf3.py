import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# 设置 matplotlib 字体
plt.rcParams["font.family"] = "Arial"

# 解析 VCF (保持你原来的函数不变)
def parse_vcf(vcf_file):
    print("📂 Reading VCF file line by line...")

    data = []
    with open(vcf_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            cols = line.strip().split('\t')
            if len(cols) < 8:
                continue
            chrom, pos, vid, ref, alt, qual, flt, info = cols[:8]
            data.append([chrom, pos, vid, ref, alt, qual, flt, info])

    df = pd.DataFrame(data, columns=['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'])
    df = df.dropna(subset=['REF', 'ALT'])

    # 添加变异类型列
    df['TYPE'] = df.apply(lambda row: classify_variant(row['REF'], row['ALT']), axis=1)
    return df


def classify_variant(ref, alt):
    if pd.isna(ref) or pd.isna(alt):
        return "Unknown"
    if "," in str(alt):
        return "Multiple"
    if len(ref) == len(alt) == 1:
        return "SNV"
    elif len(ref) != len(alt):
        return "Indel"
    else:
        return "Other"


def plot_variant_distribution(df, output_png):
    print("📈 Generating plot...")
    plt.figure(figsize=(8, 6))
    df['TYPE'].value_counts().plot(kind='bar', color='skyblue')
    plt.title("Variant Type Distribution")
    plt.xlabel("Variant Type")
    plt.ylabel("Count")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_png, dpi=200)
    plt.close()


def generate_pdf_report(pdf_path, vcf_file, df, plot_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    elements = []

    # 标题页
    title = Paragraph("VCF Variant Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    filename = os.path.basename(vcf_file)
    gen_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    meta_text = f"""
    Filename: {filename}<br/>
    Total Variants: {len(df)}<br/>
    Generated on: {gen_time}
    """
    elements.append(Paragraph(meta_text, styles['Normal']))
    elements.append(Spacer(1, 24))

    # 插入图表
    elements.append(Paragraph("Variant Type Distribution", styles['Heading2']))
    elements.append(Spacer(1, 12))
    img = Image(plot_path)
    img._restrictSize(6*inch, 4*inch)
    elements.append(img)
    elements.append(Spacer(1, 24))

    # 插入表格 - 取前10条记录
    elements.append(Paragraph("Top 10 Variant Records", styles['Heading2']))
    elements.append(Spacer(1, 12))

    table_data = [ ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'TYPE'] ]
    for _, row in df.head(10).iterrows():
        table_data.append([
            str(row['CHROM']),
            str(row['POS']),
            str(row['ID']),
            str(row['REF']),
            str(row['ALT']),
            str(row['TYPE'])
        ])

    table = Table(table_data, colWidths=[50, 50, 80, 40, 40, 40])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(table)

    # 生成PDF
    doc.build(elements)
    print(f"✅ Report saved as: {pdf_path}")


def main():
    vcf_file = r"dbSnp.vcf"  # 改成你的路径，注意加r防止转义
    output_png = "variant_plot.png"
    output_pdf = "vcf_report_reportlab.pdf"

    df = parse_vcf(vcf_file)
    plot_variant_distribution(df, output_png)
    generate_pdf_report(output_pdf, vcf_file, df, output_png)


if __name__ == "__main__":
    main()
