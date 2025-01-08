Here’s how you can use the provided Bash script:

Step 1: Save the script

Save the script in a file, for example, convert.sh, and make it executable:

chmod +x convert.sh

Step 2: Install Dependencies

Ensure the required tools are installed:

	1.	LibreOffice (for Word to PDF conversion):
Install it with:

sudo apt install libreoffice  # For Debian-based systems


	2.	Pandoc (for Word to Markdown and Markdown to Word):
Install it with:

sudo apt install pandoc  # For Debian-based systems


	3.	ImageMagick (for Word to JPG conversion):
Install it with:

sudo apt install imagemagick  # For Debian-based systems



Step 3: Run the script

Use the script with the following commands:

	1.	Convert Word to PDF:

./convert.sh word2pdf your_word_file.docx

The output will be in the ./output/pdf directory.

	2.	Convert Word to JPG:

./convert.sh word2jpg your_word_file.docx

The output will be in the ./output/jpg directory.

	3.	Convert Word to Markdown:

./convert.sh word2markdown your_word_file.docx

The output will be in the ./output/markdown directory.

	4.	Convert Markdown to Word:

./convert.sh markdown2word your_markdown_file.md

The output will be in the ./output/word directory.

Notes:

	•	Replace your_word_file.docx and your_markdown_file.md with the full path to the actual file you want to convert.
	•	Output files will be placed in their respective directories (output/pdf, output/jpg, etc.). These directories are automatically created if they don’t exist.