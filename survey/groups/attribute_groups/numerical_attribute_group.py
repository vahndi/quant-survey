from typing import Dict, List, Optional

from survey.custom_types import NumericalAttribute
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin


class NumericalAttributeGroup(AttributeContainerMixin, object):

    def __init__(self, attributes: Dict[str, NumericalAttribute] = None):

        self._questions: List[NumericalAttribute] = [
            a for a in attributes.values()
        ]
        self._item_dict: Dict[str, NumericalAttribute] = attributes
        for property_name, attribute in attributes.items():
            try:
                setattr(self, property_name, attribute)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Attribute: {attribute}')

    def question(self, name: str) -> Optional[NumericalAttribute]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().attribute(name=name)

    def to_list(self) -> List[NumericalAttribute]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._attributes

    @property
    def items(self) -> List[NumericalAttribute]:
        return self._attributes

    def __getitem__(self, item) -> NumericalAttribute:
        """
        Return the attribute with the given key.
        """
        return self._item_dict[item]
