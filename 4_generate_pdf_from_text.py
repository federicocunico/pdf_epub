from fpdf import FPDF, XPos, YPos

def create_pdf(input_file, output_pdf):
    # Read Italian text from input file
    with open(input_file, 'r', encoding='utf-8') as f:
        italian_text = f.read()
    
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add Roboto font
    pdf.add_font('Roboto', '', './Roboto/Roboto-Regular.ttf')
    
    # Add a title
    pdf.set_font("Roboto", size=12)
    pdf.cell(200, 10, text="TITLE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)  # Move down by 10 units
    
    # Add Italian text
    pdf.set_font("Roboto", size=10)
    pdf.multi_cell(0, 10, text=italian_text)
    
    # Save the pdf with specified name
    pdf.output(output_pdf)

# File paths
input_file = 'output.ita.txt'
output_pdf = 'output_ita_with_roboto.pdf'

# Generate PDF
create_pdf(input_file, output_pdf)
