import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from FileExporter import ExporterCLI

class TestExporterCLI(unittest.TestCase):

    def setUp(self):
        self.df_mock = pd.DataFrame({
            'col1': [1, 2],
            'col2': ['a', 'b']
        })
        self.menu_state = {"exportacion_completada": False}
        self.exporter = ExporterCLI(self.df_mock, self.menu_state)

    @patch('builtins.input', side_effect=["1", "archivo_test"])
    @patch('pandas.DataFrame.to_csv')
    def test_exportar_csv_exitoso(self, mock_to_csv, mock_input):
        self.exporter.exportar_datos()
        mock_to_csv.assert_called_once_with("archivo_test.csv", index=False)
        self.assertTrue(self.menu_state["exportacion_completada"])

    @patch('builtins.input', side_effect=["2", "archivo_excel"])
    @patch('pandas.DataFrame.to_excel')
    def test_exportar_excel_exitoso(self, mock_to_excel, mock_input):
        self.exporter.exportar_datos()
        mock_to_excel.assert_called_once_with("archivo_excel.xlsx", index=False)
        self.assertTrue(self.menu_state["exportacion_completada"])

    @patch('builtins.input', side_effect=["3"])
    def test_cancelar_exportacion_por_menu(self, mock_input):
        formato = self.exporter.pedir_formato()
        self.assertIsNone(formato)

    @patch('builtins.input', side_effect=["1", ""])
    def test_cancelar_por_nombre_vacio(self, mock_input):
        self.exporter.exportar_datos()
        self.assertFalse(self.menu_state["exportacion_completada"])

    @patch('builtins.input', side_effect=["9", "3"])
    def test_formato_invalido_y_luego_cancelar(self, mock_input):
        formato = self.exporter.pedir_formato()
        self.assertIsNone(formato)

    @patch('builtins.input', side_effect=["1", "archivo_test"])
    @patch('pandas.DataFrame.to_csv', side_effect=Exception("Error ficticio"))
    def test_error_durante_exportacion(self, mock_to_csv, mock_input):
        self.exporter.exportar_datos()
        self.assertFalse(self.menu_state["exportacion_completada"])

if __name__ == '__main__':
    unittest.main()
