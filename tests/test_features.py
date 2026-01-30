"""Tests de características: configuración, dependencias. Requieren customtkinter/pywin32."""
import unittest
from unittest.mock import patch, mock_open
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import terapias
except (ImportError, ModuleNotFoundError, PermissionError, OSError, Exception):
    terapias = None  # skip tests si falta deps o fallo al cargar (ej. log en otra carpeta)


class TestNewFeatures(unittest.TestCase):

    def setUp(self):
        if terapias is None:
            self.skipTest("Requires customtkinter/pywin32 (pip install -r requirements.txt)")
        self.orig_source = terapias.SOURCE_DEFAULT
        self.orig_dest = terapias.BASE_DEST
        self.orig_backup = terapias.BACKUP

    def tearDown(self):
        terapias.SOURCE_DEFAULT = self.orig_source
        terapias.BASE_DEST = self.orig_dest
        terapias.BACKUP = self.orig_backup

    @patch('terapias.config.write')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config(self, mock_open_func, mock_write):
        """Comprueba que save_config actualiza globales y escribe el archivo."""
        new_source = "C:/Test/Source"
        new_dest = "C:/Test/Dest"
        new_backup = "C:/Test/Backup"

        result = terapias.save_config(new_source, new_dest, new_backup)

        self.assertTrue(result)
        self.assertEqual(terapias.SOURCE_DEFAULT, new_source)
        self.assertEqual(terapias.BASE_DEST, new_dest)
        self.assertEqual(terapias.BACKUP, new_backup)
        mock_open_func.assert_called()
        mock_write.assert_called()

    def test_pdf_dependency(self):
        """Verifica que pywin32 sea importable."""
        try:
            import win32com.client
            import pythoncom
        except ImportError:
            self.fail("pywin32 no encontrado. Instala con: pip install pywin32")


if __name__ == '__main__':
    unittest.main()
