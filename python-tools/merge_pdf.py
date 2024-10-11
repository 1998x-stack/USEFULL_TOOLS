import PyPDF2
import os

def merge_pdfs(input_dir, output_file):
    """
    Merge PDF files in the input directory into a single PDF.

    :param input_dir: The directory containing PDF files to merge.
    :param output_file: The path to the output merged PDF file.
    """
    # Create a PDF merger object
    pdf_merger = PyPDF2.PdfMerger()

    # List all PDF files in the input directory
    pdf_files = [file for file in os.listdir(input_dir) if file.endswith(".pdf")]

    # Sort the PDF files to merge them in a specific order if needed
    pdf_files.sort()

    # Loop through the PDF files and append them to the merger
    for pdf_file in pdf_files:
        pdf_merger.append(os.path.join(input_dir, pdf_file))

    # Write the merged PDF to the output file
    with open(output_file, "wb") as output:
        pdf_merger.write(output)

    print(f"Merged {len(pdf_files)} PDFs into {output_file}")

if __name__ == "__main__":
    input_directory = "/Users/mx/Downloads/极客时间/商业知识故事类"  # Replace with the directory containing your PDFs
    output_file = "merged.pdf"   # Replace with the desired output file path
    merge_pdfs(input_directory, output_file)