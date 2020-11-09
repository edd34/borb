from typing import Optional, List

from ptext.object.pdf_high_level_object import PDFHighLevelObject, EventListener
from ptext.primitive.pdf_name import PDFName
from ptext.primitive.pdf_object import PDFObject
from ptext.tranform.base_transformer import BaseTransformer, TransformerContext


class DefaultNameTransformer(BaseTransformer):
    def can_be_transformed(self, object: PDFObject) -> bool:
        return isinstance(object, PDFName)

    def transform(
        self,
        object_to_transform: PDFObject,
        parent_object: PDFObject,
        context: Optional[TransformerContext] = None,
        event_listeners: List[EventListener] = [],
    ) -> PDFHighLevelObject:
        return object_to_transform
