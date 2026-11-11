
import os
import subprocess
import tempfile
import fitz
import pytesseract
from PIL import Image
import io

# -----------------------------------
# GITHUB REPOSITORY DETAILS
# -----------------------------------

REPO_URL = "https://github.com/kanhaiyalalbalai/docs.git"

# Enter the PDF filename/path inside your repository
PDF_FILE = "1 (1) 2.pdf"

# Output text file in the same repository
OUTPUT_FILE = "extracted_text.txt"

BRANCH = "main"


def run(command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)


# -----------------------------------
# CLONE GITHUB REPOSITORY
# -----------------------------------

with tempfile.TemporaryDirectory() as temp_dir:

    repo_dir = os.path.join(temp_dir, "docs")

    print("Cloning GitHub repository...")

    run(["git", "clone", "--branch", BRANCH, REPO_URL, repo_dir])

    pdf_path = os.path.join(repo_dir, PDF_FILE)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found in repository: {PDF_FILE}"
        )

    # -----------------------------------
    # OPEN PDF
    # -----------------------------------

    doc = fitz.open(pdf_path)

    output_path = os.path.join(repo_dir, OUTPUT_FILE)

    total_pages = len(doc)

    print(f"Total pages: {total_pages}")

    # -----------------------------------
    # EXTRACT TEXT PAGE BY PAGE
    # -----------------------------------

    with open(output_path, "w", encoding="utf-8") as output:

        for i, page in enumerate(doc):

            page_number = i + 1

            print(f"Reading page {page_number}/{total_pages}")

            text = page.get_text("text")

            # OCR for scanned or nearly blank text pages
            if len(text.strip()) < 30:

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(3, 3),
                    alpha=False
                )

                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                )

            output.write("\n")
            output.write("=" * 70 + "\n")
            output.write(f"PAGE NUMBER: {page_number}\n")
            output.write("=" * 70 + "\n\n")
            output.write(text)
            output.write("\n")

    doc.close()

    print("PDF conversion completed.")

    # -----------------------------------
    # SAVE BACK TO GITHUB
    # -----------------------------------

    run(["git", "add", OUTPUT_FILE], cwd=repo_dir)

    run([
        "git", "commit",
        "-m", "Add complete page-wise PDF text extraction"
    ], cwd=repo_dir)

    run(["git", "push", "origin", BRANCH], cwd=repo_dir)

    print("Successfully uploaded extracted text to GitHub!")
    print(f"Repository: {REPO_URL}")
    print(f"Output file: {OUTPUT_FILE}")
