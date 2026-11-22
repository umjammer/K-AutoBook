# --- coding: utf-8 ---
"""
ebookjapan configuration
"""

from config import SubConfigWithCookie


class SubConfig(SubConfigWithCookie):
    """
    configuration information
    """

    def __init__(self):
        """
        constructs configuration
        """
        super().__init__()

        self.blank_check_excludes = set()
        """
        black page checking excludes pages, negative number or zero means (total - 1 + negative_number)
        """
        self.blank_check_giveup = 11
        """
        black page checking give up times
        11 is larger than retry times, means never give up, means retry error stop downloading.
        """

    def update(self, data):
        """
        updates configuration
        @param data data for update
        """
        super().update(data)

        if 'blank_check_excludes' in data:
            self.blank_check_excludes = eval(data['blank_check_excludes'])
        if 'blank_check_giveup' in data:
            self.blank_check_giveup = data['blank_check_giveup']
