from copy import copy


class NamedMixin(object):

    name: str
    text: str

    def _set_name_and_text(self, name: str, text: str):

        self.name = name
        self.text = text

    def rename(self, name: str) -> 'NamedMixin':

        clone = copy(self)
        clone.name = name
        return clone
