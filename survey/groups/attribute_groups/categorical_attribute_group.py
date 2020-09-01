from typing import Dict, List, Optional

from survey.custom_types import CategoricalAttribute
from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin


class CategoricalAttributeGroup(
    AttributeContainerMixin,
    CategoricalGroupMixin,
    object
):

    def __init__(self, attributes: Dict[str, CategoricalAttribute] = None):

        self._attributes: List[CategoricalAttribute] = [
            a for a in attributes.values()
        ]
        self._item_dict: Dict[str, CategoricalAttribute] = attributes
        self._set_categories()
        for property_name, question in attributes.items():
            try:
                setattr(self, property_name, question)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Question: {question}')

    def question(self, name: str) -> Optional[CategoricalAttribute]:
        """
        Return the Question with the given name.

        :param name: Name of the question to return.
        """
        return super().attribute(name=name)

    def to_list(self) -> List[CategoricalAttribute]:
        """
        Return all the Questions asked in the Survey.
        """
        return self._attributes

    @property
    def items(self) -> List[CategoricalAttribute]:
        return self._attributes

    def __getitem__(self, item) -> CategoricalAttribute:
        """
        Return the attribute with the given key.
        """
        return self._item_dict[item]
