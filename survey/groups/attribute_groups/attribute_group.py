from collections import OrderedDict
from typing import Dict, Union, List, Optional, Set, Iterator

from pandas import Series

from survey.attributes import CountAttribute
from survey.attributes import RespondentAttribute, SingleCategoryAttribute
from survey.attributes import PositiveMeasureAttribute
from survey.custom_types import CategoricalAttribute, NumericalAttribute, \
    CategoricalAttributeTypes, NumericalAttributeTypes
from survey.groups.attribute_groups.categorical_attribute_group import \
    CategoricalAttributeGroup
from survey.groups.attribute_groups.count_attribute_group import \
    CountAttributeGroup
from survey.groups.attribute_groups.numerical_attribute_group import \
    NumericalAttributeGroup
from survey.groups.attribute_groups.positive_measure_attribute_group import \
    PositiveMeasureAttributeGroup
from survey.groups.attribute_groups.single_category_attribute_group import \
    SingleCategoryAttributeGroup
from survey.mixins.containers.attribute_container_mixin import \
    AttributeContainerMixin
from survey.mixins.containers.item_container_mixin import ItemContainerMixin
from survey.respondents import Respondent
from survey.utils.type_detection import all_are


class AttributeGroup(ItemContainerMixin, AttributeContainerMixin, object):
    """
    A group of Attributes and / or AttributeGroups.
    """
    def __init__(
            self,
            items: Dict[
                str, Union[RespondentAttribute, 'AttributeGroup']
            ] = None
    ):
        """
        Create a new AttributeGroup.

        :param items: Mapping of names to Attributes or Groups.
        """
        self._attributes = [a for a in items.values()
                            if isinstance(a, RespondentAttribute)]
        self._groups = {name: group for name, group in items.items()
                        if isinstance(group, AttributeContainerMixin)}
        self._item_dict: Dict[
            str, Union[RespondentAttribute, 'AttributeGroup']
        ] = items
        for property_name, attribute in items.items():
            try:
                setattr(self, property_name, attribute)
            except:
                print(f'Warning - could not set dynamic property for '
                      f'Attribute: {attribute}')

    @property
    def attribute_names(self) -> List[str]:
        """
        Return the name of each Attribute in the Survey.
        """
        return [attribute.name for attribute in self._attributes]

    @property
    def attribute_types(self) -> Set[type]:
        """
        Return a list of unique question types in the Survey.
        """
        return set([type(attribute) for attribute in self._attributes])

    def attribute_values(self, attribute: Union[RespondentAttribute, str],
                         respondents: List[Respondent] = None,
                         drop_na: bool = True) -> Series:
        """
        Return the value of the Attribute for each Respondent in the Survey.

        :param attribute: The attribute to return values for.
        :param respondents: Optional list of Respondents to filter responses to.
        :param drop_na: Whether to drop null responses.
        """
        attribute_name = (
            attribute.name if isinstance(attribute, RespondentAttribute)
            else attribute
        )
        values = self.data[attribute_name]
        if respondents is not None:
            values = values.loc[[r.respondent_id for r in respondents]]
        if drop_na:
            values = values.dropna()

        return values

    def new_attribute_group(self, names: List[str]) -> AttributeContainerMixin:
        """
        Return a new AttributeGroup from named items of the Group.

        :param names: Names of items to return in the QuestionGroup.
        """
        group_items = {}
        for name in names:
            item = self._find_item(name)
            if (
                    not isinstance(item, RespondentAttribute) and
                    not isinstance(item, AttributeContainerMixin)
            ):
                raise TypeError(
                    f'Item {item} is not an Attribute or AttributeGroup.'
                )
            group_items[name] = item
        attributes = list(group_items.values())
        if all_are(attributes, CountAttribute):
            return CountAttributeGroup(group_items)
        elif all_are(attributes, PositiveMeasureAttribute):
            return PositiveMeasureAttributeGroup(group_items)
        elif all_are(attributes, SingleCategoryAttribute):
            return SingleCategoryAttributeGroup(attributes)
        else:
            return AttributeGroup(items=group_items)

    def create_attribute_group(self, group_name: str, item_names: List[str]):
        """
        Create and add to the Group a new AttributeGroup from the named items
        of the Group.

        :param group_name: The name for the new group.
        :param item_names: Names of the items to use in the group.
        """
        group = self.new_attribute_group(names=item_names)
        self._groups[group_name] = group
        self._item_dict[group_name] = group
        try:
            setattr(self, group_name, group)
        except:
            print(f'Warning - could not set dynamic group for {group}')

    def add_attribute_group(self, group_name, group: 'AttributeGroup'):
        """
        Add a new Group to the AttributeGroup.

        :param group_name: Name for the Group.
        :param group: The Group to add.
        """
        if group_name in self._groups.keys():
            raise ValueError(f'Group {group_name} already exists!')
        self._groups[group_name] = group
        try:
            setattr(self, group_name, group)
        except:
            print(f'Warning - could not set dynamic group for {group}')

    @property
    def attribute_groups(self) -> Dict[str, 'AttributeGroup']:
        """
        Return the dictionary of groups on the Group.
        """
        return self._groups

    # region get all attributes of a given type

    @property
    def categorical_attributes(self) -> 'AttributeGroup':
        """
        Return a list of all the Categorical Attributes in the Survey.
        """
        return AttributeGroup(OrderedDict([
            (attribute.name, attribute) for attribute in self._attributes
            if type(attribute) in CategoricalAttributeTypes
        ]))

    @property
    def numerical_attributes(self) -> 'AttributeGroup':
        """
        Return a list of all the Numerical Respondent Attributes in the Survey.
        """
        return AttributeGroup(OrderedDict([
            (attribute.name, attribute) for attribute in self._attributes
            if type(attribute) in NumericalAttributeTypes
        ]))

    @property
    def count_attributes(self) -> 'AttributeGroup':
        """
        Return a list of all the Count Attributes in the Survey.
        """
        return AttributeGroup(OrderedDict([
            (attribute.name, attribute) for attribute in self._attributes
            if isinstance(attribute, CountAttribute)
        ]))

    @property
    def positive_measure_attributes(self) -> 'AttributeGroup':
        """
        Return a list of all the Positive Measure Attributes in the Survey.
        """
        return AttributeGroup(OrderedDict([
            (attribute.name, attribute) for attribute in self._attributes
            if isinstance(attribute, PositiveMeasureAttribute)
        ]))

    @property
    def single_category_attributes(self) -> SingleCategoryAttributeGroup:
        """
        Return a list of all the Categorical Attributes in the Survey.
        """
        return SingleCategoryAttributeGroup(OrderedDict([
            (attribute.name, attribute) for attribute in self._attributes
            if isinstance(attribute, SingleCategoryAttribute)
        ]))

    # endregion

    # region get attribute of a given type by name

    def categorical_attribute(
            self, name: str
    ) -> Optional[CategoricalAttribute]:
        """
        Return the Categorical Attribute with the given name.
        """
        try:
            return self.categorical_attributes[name]
        except KeyError:
            return None

    def single_category_attribute(
            self, name: str
    ) -> Optional[SingleCategoryAttribute]:
        """
        Return the Categorical Attribute with the given name.
        """
        try:
            return self.single_category_attributes[name]
        except KeyError:
            return None

    def positive_measure_attribute(
            self, name: str
    ) -> Optional[PositiveMeasureAttribute]:
        """
        Return the Categorical Attribute with the given name.
        """
        try:
            return self.positive_measure_attributes[name]
        except KeyError:
            return None

    def count_attribute(
            self, name: str
    ) -> Optional[CountAttribute]:
        """
        Return the Categorical Attribute with the given name.
        """
        try:
            return self.count_attributes[name]
        except KeyError:
            return None

    def numerical_attribute(
            self, name: str
    ) -> Optional[NumericalAttribute]:
        """
        Return the Numerical Attribute with the given name.
        """
        try:
            return self.numerical_attributes[name]
        except IndexError:
            return None

    # endregion

    # region attribute names by type

    def categorical_attribute_names(self) -> List[str]:
        """
        Return the name of each Categorical Attribute in the Survey.
        """
        return [attribute.name for attribute in
                self.categorical_attributes.to_list()]

    @property
    def count_attribute_names(self) -> List[str]:
        """
        Return the name of each CountAttribute in the Survey.
        """
        return [attribute.name for attribute in
                self.count_attributes.to_list()]

    @property
    def positive_measure_question_names(self) -> List[str]:
        """
        Return the name of each PositiveMeasureAttribute in the Survey.
        """
        return [attribute.name for attribute in
                self.positive_measure_attributes.to_list()]

    @property
    def single_category_question_names(self) -> List[str]:
        """
        Return the name of each SingleChoiceAttribute in the Survey.
        """
        return [attribute.name for attribute in
                self.single_category_attributes.to_list()]

    # endregion

    # region get existing groups of a given type by name

    def categorical_group(
            self, group_name: str
    ) -> Optional[CategoricalAttributeGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], CategoricalAttributeGroup)
        ):
            return self._groups[group_name]

    def count_group(self, group_name: str) -> Optional[CountAttributeGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], CountAttributeGroup)
        ):
            return self._groups[group_name]

    def numerical_group(
            self, group_name: str
    ) -> Optional[NumericalAttributeGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name], NumericalAttributeGroup)
        ):
            return self._groups[group_name]

    def positive_measure_group(
            self, group_name: str
    ) -> Optional[PositiveMeasureAttributeGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name],
                           PositiveMeasureAttributeGroup)
        ):
            return self._groups[group_name]

    def single_category_group(
            self, group_name: str
    ) -> Optional[SingleCategoryAttributeGroup]:

        if (
                group_name in self._groups.keys() and
                isinstance(self._groups[group_name],
                           SingleCategoryAttributeGroup)
        ):
            return self._groups[group_name]

    # endregion

    def attribute_combination_counts(self) -> Series:
        """
        Return the count of each unique combination of attributes of Survey
        Respondents.
        """
        return (
            self.data[self.attribute_names]
                .groupby(self.attribute_names)
                .size().reset_index()
                .rename(columns={0: 'count'})
        )

    def drop(self, items: Union[str, List[str]]) -> 'AttributeGroup':

        if isinstance(items, str):
            items = [items]
        return AttributeGroup(OrderedDict([
            (attribute_name, attribute)
            for attribute_name, attribute in self._item_dict.items()
            if attribute_name not in items
        ]))

    def where(self, **kwargs) -> 'AttributeGroup':
        """
        Return a new AttributeGroup with questions containing only the responses
        for users where the filtering conditions are met. See
        FilterableMixin.where() for further documentation.
        """
        return AttributeGroup({
            name: group.where(**kwargs)
            for name, group in self._item_dict.items()
        })

    def _items(self) -> List[Union[RespondentAttribute, 'AttributeGroup']]:

        return (
            [a for a in self._attributes] +
            [g for g in self._groups]
        )

    def __getitem__(self, item):

        return self._item_dict[item]

    def __iter__(self) -> Iterator['RespondentAttribute']:

        return self._items().__iter__()