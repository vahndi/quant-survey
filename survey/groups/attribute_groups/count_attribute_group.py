from typing import Dict, List, Optional

from survey.attributes import CountAttribute
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin
from survey.mixins.containers.single_type_attribute_container_mixin import \
    SingleTypeAttributeContainerMixin
from survey.utils.type_detection import all_are


class CountAttributeGroup(AttributeContainerMixin,
                          SingleTypeAttributeContainerMixin,
                          object):

    def __init__(self, attributes: Dict[str, CountAttribute] = None):

        if not all_are(attributes.values(), CountAttribute):
            raise TypeError('Not all attributes are CountAttributes.')
        self._attributes: List[CountAttribute] = [
            a for a in attributes.values()
        ]
        self._item_dict: Dict[str, CountAttribute] = attributes
        for property_name, attribute in attributes.items():
            try:
                setattr(self, property_name, attribute)
            except:
                print(f'Warning - could not set dynamic property'
                      f' for Attribute: {attribute}')

    def attribute(self, name: str) -> Optional[CountAttribute]:
        """
        Return the Attribute with the given name.

        :param name: Name of the attribute to return.
        """
        return super().attribute(name=name)

    def to_list(self) -> List[CountAttribute]:
        """
        Return all the Attributes asked in the Survey.
        """
        return self._attributes

    @property
    def items(self) -> List[CountAttribute]:
        return self._attributes

    def __getitem__(self, item) -> CountAttribute:
        """
        Return the attribute with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: CountAttribute):
        """
        Add a new attribute to the group.

        :param index: The accessor key for the attribute.
        :param value: The attribute.
        """
        if not isinstance(value, CountAttribute):
            raise TypeError('Item to set is not a CountAttribute')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property'
                  f' for Question: {index}')
        self._attributes.append(value)
