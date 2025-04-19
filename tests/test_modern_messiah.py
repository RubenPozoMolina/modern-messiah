import pytest

from mm.modern_messiah import ModernMessiah

configuration_files = [
    "tests/data/modern_messiah/config_test_local_epub.yaml",
    "tests/data/modern_messiah/config_test_local_mobi_exclude.yaml"
]

class TestModernMessiah:

    @pytest.mark.parametrize("config_file", configuration_files)
    def test_modern_messiah(self, config_file):
        modern_messiah = ModernMessiah(config_file)
        modern_messiah.write_book()
        del modern_messiah
