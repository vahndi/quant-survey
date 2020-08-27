from typing import List


class GroupContainerMixin(object):

    _groups: dict

    @property
    def group_names(self) -> List[str]:

        return list(self._groups.keys())
