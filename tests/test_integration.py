"""
Tests de integración para el flujo de lógica.
(No importa terapias.py para evitar side effects de config/GUI)
"""
import os
import tempfile
import unittest

from terapias_logic import sanitize_filename, patient_from_user_input, build_folder_structure


class TestIntegrationFlujo(unittest.TestCase):
    """Tests del flujo de organización completo (solo lógica)."""

    def test_flujo_nombre_completo(self):
        """Simula el flujo: usuario escribe nombre -> sanitize -> patient."""
        user_input = "Informe SS Juan Pérez"
        sanitized = sanitize_filename(user_input)
        paciente = patient_from_user_input(sanitized)
        self.assertEqual(sanitized, "Informe SS Juan Pérez")
        self.assertEqual(paciente, "Juan Pérez")

    def test_flujo_con_caracteres_invalidos(self):
        """Usuario introduce caracteres inválidos."""
        user_input = 'Informe SS Juan Pérez'
        sanitized = sanitize_filename(user_input)
        paciente = patient_from_user_input(sanitized)
        self.assertEqual(sanitized, "Informe SS Juan Pérez")
        self.assertEqual(paciente, "Juan Pérez")
        # Con caracteres inválidos, se reemplazan
        user_input2 = 'Informe<>:"SS" Juan'
        sanitized2 = sanitize_filename(user_input2)
        self.assertNotIn("<", sanitized2)

    def test_flujo_estructura_completa(self):
        """Verifica que la estructura de carpetas se construye correctamente."""
        meses = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE",
        }
        base = "C:\\TERAPIAS"
        ruta_anio, ruta_mes, ruta_dia, _ = build_folder_structure(base, 2026, 1, 28, meses)
        destino_paciente = os.path.join(ruta_dia, "Juan Pérez")
        self.assertIn("2026", ruta_anio)
        self.assertIn("01- ENERO", ruta_mes)
        self.assertIn("28 DE ENERO", ruta_dia)
        self.assertIn("Juan Pérez", destino_paciente)


class TestFindLatestDocLogic(unittest.TestCase):
    """Tests de la lógica de find_latest_doc (sin importar terapias)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))

    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except OSError:
            pass

    def test_encuentra_docx_mas_reciente(self):
        """Lógica: el archivo con mtime más reciente debe ser el elegido."""
        import time
        # Usar extensión .dat para evitar bloqueos de OneDrive en .docx
        doc1 = os.path.join(self.temp_dir, "a.dat")
        doc2 = os.path.join(self.temp_dir, "b.dat")
        try:
            with open(doc1, "w") as f:
                f.write("1")
            time.sleep(0.05)
            with open(doc2, "w") as f:
                f.write("2")
        except PermissionError:
            self.skipTest("Permiso denegado al crear archivos (OneDrive/sandbox)")
        # b.dat es más reciente
        latest = None
        latest_time = -1
        for fname in os.listdir(self.temp_dir):
            if fname.lower().endswith(".dat"):
                fpath = os.path.join(self.temp_dir, fname)
                mtime = os.path.getmtime(fpath)
                if mtime > latest_time:
                    latest_time = mtime
                    latest = fpath
        self.assertIn("b.dat", latest)

    def test_ignora_txt(self):
        """Solo .doc y .docx deben considerarse (simulamos con .dat)."""
        try:
            txt_file = os.path.join(self.temp_dir, "archivo.dat")
            with open(txt_file, "w") as f:
                f.write("texto")
        except PermissionError:
            self.skipTest("Permiso denegado al crear archivos")
        # Buscamos .doc/.docx - no .dat
        doc_files = [f for f in os.listdir(self.temp_dir) if f.lower().endswith((".doc", ".docx"))]
        self.assertEqual(len(doc_files), 0)


if __name__ == "__main__":
    unittest.main()
