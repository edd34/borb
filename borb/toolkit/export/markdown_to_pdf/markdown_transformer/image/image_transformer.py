#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This implementation of BaseMarkdownTransformer handles images
"""
import re
import typing
from decimal import Decimal

import requests
from PIL import Image as PILImage  # type: ignore [import]

from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.page_layout.browser_layout import BrowserLayout
from borb.pdf.page.page import Page
from borb.toolkit.export.markdown_to_pdf.markdown_transformer.base_markdown_transformer import (
    BaseMarkdownTransformer,
    MarkdownTransformerState,
)


class ImageTransformer(BaseMarkdownTransformer):
    """
    This implementation of BaseMarkdownTransformer handles images
    """

    @staticmethod
    def _get_image_default_margins():
        pil_image = PILImage.new("RGB", (16, 16))
        borb_image = Image(pil_image, width=Decimal(10), height=Decimal(10))
        return (
            borb_image.get_margin_top(),
            borb_image.get_margin_right(),
            borb_image.get_margin_bottom(),
            borb_image.get_margin_left(),
        )

    def _can_transform(self, context: MarkdownTransformerState) -> bool:
        if context.get_markdown_string()[context.tell()] != "!":
            return False
        markdown_str: str = context.get_markdown_string()[
            context.tell() : context.get_markdown_string().find(
                "\n", context.tell() + 1
            )
        ]
        return re.match("!\[[^]]+\]\([^)]+\)", markdown_str) is not None

    def _transform(self, context: MarkdownTransformerState) -> None:

        # get markdown string of current char -> next line
        markdown_str: str = context.get_markdown_string()[
            context.tell() : context.get_markdown_string().find(
                "\n", context.tell() + 1
            )
        ]
        assert len(markdown_str) > 0

        # match against regex
        match: re.Match = re.match("!\[[^]]+\]\((?P<url>[^)]+)\)", markdown_str)
        assert match is not None

        # extract (named group) url
        url: str = match["url"]
        assert len(url) > 0

        # open raw image
        image = PILImage.open(
            requests.get(
                url,
                stream=True,
            ).raw
        )

        # get width and height
        w: int = image.width
        h: int = image.height

        # determine max available width/height
        margins: typing.Tuple[
            Decimal, Decimal, Decimal, Decimal
        ] = ImageTransformer._get_image_default_margins()
        W: int = 128
        H: int = 128

        # Page
        parent_element = context.get_parent_layout_element()
        if isinstance(parent_element, Page):
            W = int(parent_element.get_page_info().get_width() * Decimal(0.8))
            H = int(parent_element.get_page_info().get_height() * Decimal(0.8))

        # BrowserLayout
        if isinstance(parent_element, BrowserLayout):
            W = (
                int(
                    parent_element.get_page().get_page_info().get_width()
                    - parent_element._horizontal_margin * Decimal(2)
                )
                - 1
            )
            H = (
                int(
                    parent_element.get_page().get_page_info().get_height()
                    - parent_element._vertical_margin * Decimal(2)
                )
                - 1
            )

        # TODO: Table

        # margin
        W = W - int(margins[1]) - int(margins[3]) - 1
        H = H - int(margins[0]) - int(margins[2]) - 1

        # rescale
        r: float = min(W / w, H / h)
        w = int(w * r)
        h = int(h * r)

        # create and add Image
        borb_image: Image = Image(image, width=Decimal(w), height=Decimal(h))
        parent_element.add(borb_image)

        # add remote go to annotation
        try:
            parent_element.get_page().append_remote_go_to_annotation(
                borb_image.get_bounding_box(), url
            )
        except:
            pass

        # seek
        context.seek(context.get_markdown_string().find("\n", context.tell()) + 1)
