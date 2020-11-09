from ptext.primitive.pdf_object import PDFObject


class PDFCanvasOperatorName(PDFObject):

    NAMES = [
        "b",
        "B",
        "b*",
        "B*",
        "BDC",
        "BI",
        "BMC",
        "BT",
        "BX",
        "c",
        "cm",
        "cs",
        "CS",
        "d",
        "d0",
        "d1",
        "Do",
        "DP",
        "EI",
        "EMC",
        "ET",
        "EX",
        "f",
        "F",
        "f*",
        "g",
        "G",
        "gs",
        "h",
        "i",
        "ID",
        "j",
        "J",
        "k",
        "K",
        "l",
        "m",
        "M",
        "MP",
        "n",
        "q",
        "Q",
        "re",
        "RG",
        "rg",
        "ri",
        "s",
        "S",
        "sc",
        "SC",
        "SCN",
        "scn",
        "sh",
        "T*",
        "Tc",
        "Td",
        "Tf",
        "Tj",
        "TJ",
        "TL",
        "Tm",
        "Tr",
        "Ts",
        "Tw",
        "Tz",
        "v",
        "w",
        "W",
        "W*",
        "y",
        "''",
        '"',
    ]

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def get_text(self):
        return self.text

    def __str__(self):
        return self.text
