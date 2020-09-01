from typing import List, Dict


class Metadata(object):

    name: str
    text: str

    @staticmethod
    def text_to_name(metadatas: List['Metadata']) -> Dict[str, str]:
        """
        Create a dictionary mapping the text of each metadata instance to its
        name.

        :param metadatas: List of Metadata instances.
        """
        return {
            meta.text: meta.name
            for meta in metadatas
        }
