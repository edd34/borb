import xml.etree.ElementTree as ET
from typing import Optional, Tuple

from ptext.object.canvas.event.begin_page_event import BeginPageEvent
from ptext.object.canvas.event.end_page_event import EndPageEvent
from ptext.object.canvas.event.image_render_event import ImageRenderEvent
from ptext.object.canvas.event.text_render_event import TextRenderEvent
from ptext.object.page.page_size import PageSize
from ptext.object.pdf_high_level_object import EventListener, Event


class SVGExport(EventListener):
    def __init__(
        self,
        include_document_information: bool = False,
        default_page_size: Optional[Tuple[float, float]] = PageSize.A4_PORTRAIT.value,
    ):
        self.svg_element_per_page = {}

        # global settings
        self.include_document_information = include_document_information
        self.default_page_size = default_page_size

        # page being rendered
        self.current_page_width = None
        self.current_page_height = None
        self.current_page_svg_element = None
        self.current_page = -1

    def event_occurred(self, event: Event) -> None:
        if isinstance(event, BeginPageEvent):
            self.begin_page(event.get_page())
        if isinstance(event, EndPageEvent):
            self.end_page(event.get_page())
        if isinstance(event, TextRenderEvent):
            self.render_text(event)
        if isinstance(event, ImageRenderEvent):
            self.render_image(event)

    def begin_page(self, page: "Page"):

        # get page nr
        self.current_page += 1

        # get page size
        page_size = page.get_page_info().get_size()
        if page_size is None and self.default_page_size is None:
            return
        if page_size is None:
            page_size = self.default_page_size

        self.current_page_width = page_size[0]
        self.current_page_height = page_size[1]

        # init svg image
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        svg_element = ET.Element("svg")
        svg_element.set(
            "viewbox", "0 0 %d %d" % (self.current_page_width, self.current_page_height)
        )

        # meta properties
        if self.include_document_information:
            document_info = page.get_document().get_document_info()
            for method, name in [
                (document_info.get_title, "dc:title"),
                (document_info.get_author, "dc:author"),
                (document_info.get_creator, "dc:creator"),
                (document_info.get_producer, "dc:producer"),
            ]:
                if method() is not None:
                    e = ET.Element("desc")
                    e.set("property", name)
                    e.text = method().get_text()
                    svg_element.append(e)

        # white background
        rct_element = ET.Element("rect")
        rct_element.set("width", str(self.current_page_width))
        rct_element.set("height", str(self.current_page_height))
        rct_element.set("style", "fill:rgb(255, 255, 255);")
        svg_element.append(rct_element)
        self.current_page_svg_element = svg_element

    def end_page(self, page: "Page"):

        # store
        self.svg_element_per_page[self.current_page] = self.current_page_svg_element

        # reset
        self.current_page_width = None
        self.current_page_height = None
        self.current_page_svg_element = None

    def get_svg(self, page_number: int) -> ET.Element:
        return self.svg_element_per_page[page_number]

    def render_text(self, text_render_info: "TextRenderInfo"):

        if len(text_render_info.get_text().replace(" ", "")) == 0:
            return

        # color
        r = int(text_render_info.font_color.to_rgb().red * 255)
        g = int(text_render_info.font_color.to_rgb().green * 255)
        b = int(text_render_info.font_color.to_rgb().blue * 255)

        # font size
        fs = text_render_info.get_font_size()

        # COORDINATE TRANSFORM:
        # In PDF coordinate space the origin is at the bottom left of the page,
        # for SVG images, the origin is the top left.
        bl = text_render_info.get_baseline()
        x = int(bl.x0)
        y = int(self.current_page_height - bl.y0)

        # build text element
        text_element = ET.Element("text")
        if text_render_info.get_font_family() is not None:
            text_element.set("font-family", text_render_info.get_font_family())
        text_element.set("x", str(x))
        text_element.set("y", str(y))
        text_element.set(
            "style", "fill=rgb(%d, %d, %d); font-size=%d px;" % (r, g, b, fs)
        )
        text_element.text = text_render_info.get_text()

        # append to page
        self.current_page_svg_element.append(text_element)

    def render_image(self, event: ImageRenderEvent):

        # build img element
        img_element = ET.Element("g")

        w = int(event.get_width())
        h = int(event.get_height())
        img_scaled = event.get_image().image.resize((w, h))

        # COORDINATE TRANSFORM:
        # In PDF coordinate space the origin is at the bottom left of the page,
        # for SVG images, the origin is the top left.
        x = int(event.get_x())
        y = int(self.current_page_height - event.get_y() - event.get_height())

        # set pixels
        for i in range(0, w):
            for j in range(0, h):
                c = event.get_rgb(i, j)
                pixel_element = ET.Element("rect")
                pixel_element.set("style", "fill:rgb(%d, %d, %d);" % c)
                pixel_element.set("x", str(x + i))
                pixel_element.set("y", str(y + j))
                pixel_element.set("width", "1")
                pixel_element.set("height", "1")
                img_element.append(pixel_element)

        self.current_page_svg_element.append(img_element)
