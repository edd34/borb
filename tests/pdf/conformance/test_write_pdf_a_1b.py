import unittest
from pathlib import Path

from borb.io.read.types import Dictionary, Name, String
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from tests.test_util import compare_visually_to_ground_truth


class TestWritePDFA1B(unittest.TestCase):
    """
    This test creates a PDF with a few PDF graphics in it
    """

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        # find output dir
        p: Path = Path(__file__).parent
        while "output" not in [x.stem for x in p.iterdir() if x.is_dir()]:
            p = p.parent
        p = p / "output"
        self.output_dir = Path(p, Path(__file__).stem.replace(".py", ""))
        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def test_write_pdf_a_1b(self):

        # create empty Document
        pdf = Document()

        # create empty Page
        page = Page()

        # add Page to Document
        pdf.append_page(page)

        # create PageLayout
        layout: PageLayout = SingleColumnLayout(page)

        # add Paragraph
        layout.add(Paragraph("Hello World!"))

        info_dictionary: Dictionary = Dictionary()
        info_dictionary[Name("Title")] = String("Lorem Ipsum (T)")
        info_dictionary[Name("Subject")] = String("Lorem Ipsum (S)")
        info_dictionary[Name("Creator")] = String("Joris Schellekens (C)")
        info_dictionary[Name("Author")] = String("Joris Schellekens (A)")
        info_dictionary[Name("Keywords")] = String("Lorem Ipsum Dolor Sit Amet")
        pdf["XRef"]["Trailer"][Name("Info")] = info_dictionary

        # attempt to store PDF
        out_file = self.output_dir / "output_001.pdf"
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf, "PDF/A-1b")

    def test_re_open_pdfa_1_b(self):

        # attempt to re-open PDF
        out_file = self.output_dir / "output_001.pdf"
        with open(out_file, "rb") as in_file_handle:
            pdf = PDF.loads(in_file_handle)

        # assert XMP meta data
        xmp = pdf.get_xmp_document_info()
        assert xmp.get_title() == "Lorem Ipsum (T)"
        assert xmp.get_creator() == "Joris Schellekens (C)"
        assert xmp.get_author() == "Joris Schellekens (A)"
        assert xmp.get_subject() == "Lorem Ipsum (S)"
        assert xmp.get_keywords() == "Lorem Ipsum Dolor Sit Amet"

    def test_re_save_pdf_a_1_b(self):

        # attempt to re-open PDF
        out_file = self.output_dir / "output_001.pdf"
        with open(out_file, "rb") as in_file_handle:
            pdf = PDF.loads(in_file_handle)

        # attempt to store PDF
        out_file = self.output_dir / "output_002.pdf"
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf, "PDF/A-1b")

        # attempt to re-open PDF
        with open(out_file, "rb") as in_file_handle:
            pdf = PDF.loads(in_file_handle)

        # assert XMP meta data
        xmp = pdf.get_xmp_document_info()
        assert xmp.get_title() == "Lorem Ipsum (T)"
        assert xmp.get_creator() == "Joris Schellekens (C)"
        assert xmp.get_author() == "Joris Schellekens (A)"
        assert xmp.get_subject() == "Lorem Ipsum (S)"
        assert xmp.get_keywords() == "Lorem Ipsum Dolor Sit Amet"

        compare_visually_to_ground_truth(out_file)
