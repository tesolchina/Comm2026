import os
import sys

# Define paths
input_pdf = '/Users/simonwang/Documents/Usage/ZhouWorkshop/Comm2026/demo/PDF2md/Li_23_AI-based conversational agents for promoting mental health and wellbeing.pdf'
output_dir = '/Users/simonwang/Documents/Usage/ZhouWorkshop/Comm2026/demo/PDF2md'
output_file = os.path.join(output_dir, 'Li_23_AI-based conversational agents for promoting mental health and wellbeing.md')

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Starting PDF to Markdown conversion...")
print(f"Input PDF: {input_pdf}")
print(f"Output file: {output_file}")

try:
    # Try using PyMuPDF (fitz) - most reliable for PDF extraction
    import fitz  # PyMuPDF
    
    print("Using PyMuPDF for PDF extraction...")
    
    # Open the PDF
    doc = fitz.open(input_pdf)
    total_pages = len(doc)
    print(f"PDF opened successfully. Total pages: {total_pages}")
    
    markdown_content = []
    
    # Process each page
    for page_num in range(total_pages):
        print(f"Processing page {page_num + 1}/{total_pages}...")
        page = doc[page_num]
        
        # Extract text with formatting - using "text" mode preserves structure
        text = page.get_text("text")
        
        # Add page break for multi-page documents (except first page)
        if page_num > 0:
            markdown_content.append("\n\n---\n\n")
        
        # Process and format the text
        if text:
            # Split into lines and process
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    formatted_lines.append("")
                    continue
                
                # Detect potential section headings (all caps, short, no ending punctuation)
                # Common patterns: "INTRODUCTION", "RESULTS", "METHODS", etc.
                if (line.isupper() and 
                    len(line) < 80 and 
                    len(line.split()) < 12 and
                    not line.endswith('.') and
                    not line.endswith(',') and
                    not line.endswith(';')):
                    # Format as markdown heading
                    formatted_lines.append(f"## {line}")
                    formatted_lines.append("")  # Add blank line after heading
                else:
                    # Regular paragraph text
                    formatted_lines.append(line)
            
            # Join lines with proper spacing
            markdown_content.append('\n'.join(formatted_lines))
            markdown_content.append("\n\n")
    
    doc.close()
    
    # Write to markdown file
    print(f"Writing markdown file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_content))
    
    print(f"\n=== Conversion Complete ===")
    print(f"Markdown file saved to: {output_file}")
    print(f"Total pages processed: {total_pages}")
    
except ImportError:
    print("PyMuPDF not found. Trying alternative method with pdfplumber...")
    try:
        import pdfplumber
        
        print("Using pdfplumber for PDF extraction...")
        
        markdown_content = []
        
        with pdfplumber.open(input_pdf) as pdf:
            print(f"PDF opened successfully. Total pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}/{len(pdf.pages)}...")
                
                # Extract text
                text = page.extract_text()
                
                # Add page break for multi-page documents (except first page)
                if page_num > 0:
                    markdown_content.append("\n\n---\n\n")
                
                # Add the text content
                if text:
                    markdown_content.append(text)
        
        # Write to markdown file
        print(f"Writing markdown file...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
        
        print(f"\n=== Conversion Complete ===")
        print(f"Markdown file saved to: {output_file}")
        
    except ImportError:
        print("Error: Neither PyMuPDF nor pdfplumber is installed.")
        print("Please install one of them:")
        print("  pip install pymupdf")
        print("  or")
        print("  pip install pdfplumber")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing PDF with pdfplumber: {e}")
        sys.exit(1)
        
except Exception as e:
    print(f"Error processing PDF: {e}")
    sys.exit(1)

