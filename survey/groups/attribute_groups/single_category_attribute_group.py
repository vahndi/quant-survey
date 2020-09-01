from pandas import Series, DataFrame
from typing import Dict, List, Optional, Union

from survey.attributes import SingleCategoryAttribute
from survey.mixins.categorical_group_mixin import CategoricalGroupMixin
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin
from survey.mixins.containers.single_category_stack_mixin import \
    SingleCategoryStackMixin
from survey.mixins.containers.single_type_attribute_container_mixin import \
    SingleTypeAttributeContainerMixin
from survey.mixins.single_category_group.single_category_group_comparison_mixin import \
    SingleCategoryGroupComparisonMixin
from survey.mixins.single_category_group.single_category_group_pt_mixin import \
    SingleCategoryGroupPTMixin
from survey.mixins.single_category_group.single_category_group_significance_mixin import \
    SingleCategoryGroupSignificanceMixin
from survey.utils.type_detection import all_are


class SingleCategoryAttributeGroup(AttributeContainerMixin,
                                   SingleCategoryStackMixin,
                                   SingleCategoryGroupSignificanceMixin,
                                   SingleCategoryGroupComparisonMixin,
                                   SingleCategoryGroupPTMixin,
                                   SingleTypeAttributeContainerMixin,
                                   CategoricalGroupMixin,
                                   object):

    def __init__(self, attributes: Dict[str, SingleCategoryAttribute] = None):

        if not all_are(attributes.values(), SingleCategoryAttribute):
            raise TypeError('Not all attributes are SingleCategoryAttribute.')
        self._attributes: List[SingleCategoryAttribute] = [
            a for a in attributes.values()
        ]
        self._set_categories()
        self._item_dict: Dict[str, SingleCategoryAttribute] = attributes
        for property_name, attribute in attributes.items():
            try:
                setattr(self, property_name, attribute)
            except:
                print(f'Warning - could not set dynamic property '
                      f'for Attribute: {attribute}')

    @property
    def item_dict(self) -> Dict[str, SingleCategoryAttribute]:
        return self._item_dict

    @property
    def items(self) -> List[SingleCategoryAttribute]:
        return self._attributes

    def attribute(self, name: str) -> Optional[SingleCategoryAttribute]:
        """
        Return the Attribute with the given name.

        :param name: Name of the attribute to return.
        """
        return super().attribute(name=name)

    def to_list(self) -> List[SingleCategoryAttribute]:
        """
        Return all the Attributes asked in the Survey.
        """
        return self._attributes

    def counts(self, by: str = 'key',
               values: Optional[Union[str, List[str]]] = None,
               name_map: Optional[Dict[str, str]] = None) -> Series:
        """
        Count the number of matching values for each attribute in the group.

        :param by: What to use as the index for the returned counts. One of
                   ['key', 'attribute'].
        :param values: A response value or list of values to match. Leave as
                       None to count all responses.
        :param name_map: Optional dict to replace keys or attribute names with
                         new names.
        """
        counts = []
        if by == 'key':
            for key, attribute in self._item_dict.items():
                counts.append({
                    'name': name_map[key] if name_map else key,
                    'count': attribute.count(values)
                })
        elif by == 'attribute':
            for attribute in self._attributes:
                counts.append({
                    'name': (
                        name_map[attribute.name] if name_map
                        else attribute.name
                    ),
                    'count': attribute.count(values)
                })
        else:
            raise ValueError("'by' must be one of ['key', 'attribute']")

        return DataFrame(counts).set_index('name')['count']

    def count(self) -> int:
        """
        Count the total number of attribute values  in the group.
        """
        return self.counts().sum()

    def __getitem__(self, item) -> SingleCategoryAttribute:
        """
        Return the attribute with the given key.
        """
        return self._item_dict[item]

    def __setitem__(self, index, value: SingleCategoryAttribute):
        """
        Add a new attribute to the group.

        :param index: The accessor key for the attribute.
        :param value: The attribute.
        """
        if not isinstance(value, SingleCategoryAttribute):
            raise TypeError('Item to set is not a SingleCategoryAttribute')
        self._item_dict[index] = value
        try:
            setattr(self, index, value)
        except:
            print(f'Warning - could not set dynamic property '
                  f'for Attribute: {index}')
        self._attributes.append(value)
