from typing import Dict

from survey.attributes import RespondentAttribute


class SingleTypeAttributeContainerMixin(object):

    _item_dict: Dict[str, RespondentAttribute]

    def where(self, **kwargs):
        """
        Return a new AttributeContainerMixin with questions containing only the
        responses for users where the filtering conditions are met.
        See FilterableMixin.where() for further documentation.
        """
        constructor = type(self)
        return constructor(attributes={
            name: attribute.where(**kwargs)
            for name, attribute in self._item_dict.items()
        })
