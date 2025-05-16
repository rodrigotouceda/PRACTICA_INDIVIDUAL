import unittest
import pandas as pd
from unittest.mock import MagicMock
from dataVisualizer import VisualizerCLI

class TestVisualizerCLI(unittest.TestCase):

    def setUp(self):
        # Datos de prueba
        data_original = {
            'categoria': ['A', 'B', 'A', 'C', 'B'],
            'numero': [1, 2, 3, 4, 5]
        }
        data_procesado = {
            'categoria': ['A', 'B', 'C', 'A', 'B'],
            'numero': [0.1, 0.4, 0.7, 0.2, 0.5]
        }
        self.df_original = pd.DataFrame(data_original)
        self.df_procesado = pd.DataFrame(data_procesado)

        self.original_features = ['categoria', 'numero']
        self.processed_features = ['categoria', 'numero']

        # Mock de DataManager
        self.data_manager = MagicMock()
        self.data_manager.es_categorica.side_effect = lambda col, _: col == 'categoria'
        self.data_manager.es_normalizable.side_effect = lambda col, _: col == 'numero'
        self.data_manager.one_hot_features = []  # simula que no hay one-hot

        # Inicializar clase
        self.visualizer = VisualizerCLI(
            self.df_original,
            self.df_procesado,
            self.original_features,
            self.processed_features,
            self.data_manager
        )

    def test_atributos_iniciales(self):
        self.assertEqual(self.visualizer.og_categorical_features, ['categoria'])
        self.assertEqual(self.visualizer.og_numerical_features, ['numero'])
        self.assertEqual(self.visualizer.new_categorical_features, ['categoria'])
        self.assertEqual(self.visualizer.new_numerical_features, ['numero'])
        self.assertEqual(self.visualizer.one_hot_features, [])

    def test_mostrar_resumen_estadistico(self):
        try:
            self.visualizer.mostrar_resumen_estadistico()
        except Exception as e:
            self.fail(f"mostrar_resumen_estadistico() lanzó una excepción: {e}")

    def test_obtener_prefijo_base(self):
        self.assertEqual(self.visualizer.obtener_prefijo_base('sexo_M'), 'sexo')
        self.assertEqual(self.visualizer.obtener_prefijo_base('edad'), 'edad')

    def test_visualizacion_completada_flag(self):
        self.assertFalse(self.visualizer.visualizacion_completada)
        # Simulamos visualización manual
        self.visualizer.visualizacion_completada = True
        self.assertTrue(self.visualizer.visualizacion_completada)

if __name__ == '__main__':
    unittest.main()
