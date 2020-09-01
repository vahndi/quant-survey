from typing import Dict, List, Optional

from survey.attributes import PositiveMeasureAttribute
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin
from survey.mixins.containers.single_type_attribute_container_mixin import \
    SingleTypeAttributeContainerMixin
from survey.utils.type_detection import all_are


class PositiveMeasureAttributeGroup(AttributeContainerMixin,
                                    SingleTypeAttributeContainerMixin,
                                    object):

    def __init__(self, attributes: Dict[str, PositiveMeasureAttribute] = None):

        if not all_are(attributes.values(), PositiveMeasureAttribute):
            raise TypeError('Not all attributes are PositiveMeasureAttribute.')
        self._attributes: List[PositiveMeasureAttribute] = [
            a for a in attributes.values()
        ]
        self._item_dict: Dict[str, PositiveMeasureAttribute] = attributes
        for property_name, attribute in attributes.items():
            try:
                setattr(self, property_name, attribute)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Attribute: {attribute}')

    def attribute(self, name: str) -> Optional[PositiveMeasureAttribute]:
        """
        Return the Attribute with the given name.

        :param name: Name of the attribute to return.
        """
        return super().attribute(name=name)

    def to_list(self) -> List[PositiveMeasureAttribute]:
        """
        Return all the Attributes asked in the Survey.
        """
        return self._attributes

    @property
    def items(self) -> List[PositiveMeasureAttribute]:
        return self._attributes

    def __getitem__(self, item) -> PositiveMeasureAttribute:
        """
        Return the attribute with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: PositiveMeasureAttribute):
        """
        Add a new attribute to the group.

        :param index: The accessor key for the attribute.
        :param value: The attribute.
        """
        if not isinstance(value, PositiveMeasureAttribute):
            raise TypeError('Item to set is not a PositiveMeasureAttribute')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._attributes.append(value)
