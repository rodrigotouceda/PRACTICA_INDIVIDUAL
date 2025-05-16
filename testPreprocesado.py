import unittest
import pandas as pd
import numpy as np
from DataManager import DataManager

class PruebasDataManager(unittest.TestCase):
    def setUp(self):
        """Configura un DataFrame de prueba antes de cada test"""
        self.df = pd.DataFrame({
            'A': [1, 2, None, 4, 100],
            'B': ['x', 'y', 'x', 'z', None],
            'C': [10, 20, 20, 40, 50]
        })
        self.gestor = DataManager(self.df)

    def test_seleccion_columnas_valida(self):
        """Verifica que se seleccionen correctamente columnas válidas"""
        entradas, salida = self.gestor.seleccionar_columnas("0,2", "1")
        self.assertEqual(entradas, ['A', 'C'])
        self.assertEqual(salida, 'B')

    def test_seleccion_columnas_invalidas(self):
        """Verifica que se detecten correctamente selecciones inválidas de columnas"""
        X, y = self.gestor.seleccionar_columnas("0,1", "1")
        self.assertIsNone(X)
        self.assertIsNone(y)

        X, y = self.gestor.seleccionar_columnas("0,10", "2")
        self.assertIsNone(X)
        self.assertIsNone(y)

        X, y = self.gestor.seleccionar_columnas("0,0", "1")
        self.assertIsNone(X)
        self.assertIsNone(y)

    def test_deteccion_valores_faltantes(self):
        """Verifica si se detectan correctamente valores faltantes en una columna"""
        self.assertTrue(self.gestor.tiene_valores_faltantes("A"))
        self.assertIn("A", self.gestor.missing_values_columns)

    def test_manejo_faltantes_media(self):
        """Verifica que se rellenen los NaN con la media"""
        self.gestor.features = ['A']
        self.gestor.missing_values_columns = ['A']
        df_resultado = self.gestor.manejar_valores_faltantes(['A'], 2)
        self.assertFalse(df_resultado['A'].isnull().any())

    def test_manejo_faltantes_mediana(self):
        """Verifica que se rellenen los NaN con la mediana"""
        df_resultado = self.gestor.manejar_valores_faltantes(['A'], 3)
        self.assertFalse(df_resultado['A'].isnull().any())

    def test_manejo_faltantes_moda(self):
        """Verifica que se rellenen los NaN con la moda"""
        df_resultado = self.gestor.manejar_valores_faltantes(['B'], 4)
        self.assertFalse(df_resultado['B'].isnull().any())

    def test_manejo_faltantes_constante(self):
        """Verifica que se rellenen los NaN con un valor constante introducido"""
        import builtins
        input_original = builtins.input
        builtins.input = lambda _: 999
        df_resultado = self.gestor.manejar_valores_faltantes(['A'], 5)
        builtins.input = input_original
        self.assertIn(999, df_resultado['A'].values)

    def test_deteccion_categorica(self):
        """Verifica si una columna es detectada como categórica"""
        es_cat = self.gestor.es_categorica("B")
        self.assertTrue(es_cat)
        self.assertIn("B", self.gestor.categoric_columns)

    def test_codificacion_label(self):
        """Verifica que la codificación label transforme correctamente los valores"""
        self.gestor.features = ['B']
        self.gestor.categoric_columns = ['B']
        df_codificado = self.gestor.a_categorica(['B'], 2)
        self.assertTrue(pd.api.types.is_integer_dtype(df_codificado['B']))

    def test_codificacion_one_hot(self):
        """Verifica que la codificación one-hot genere nuevas columnas correctamente"""
        self.gestor.features = ['B']
        self.gestor.categoric_columns = ['B']
        df_codificado = self.gestor.a_categorica(['B'], 1)
        columnas = [col for col in df_codificado.columns if col.startswith('B_')]
        self.assertGreater(len(columnas), 0)

    def test_normalizacion_min_max(self):
        """Verifica que Min-Max Scaling funcione correctamente"""
        self.gestor.features = ['C']
        self.gestor.normalizable_columns = ['C']
        df_escalado = self.gestor.normalizar_min_max(['C'])
        self.assertAlmostEqual(df_escalado['C'].min(), 0.0, places=5)
        self.assertAlmostEqual(df_escalado['C'].max(), 1.0, places=5)

    def test_normalizacion_z_score(self):
        """Verifica que Z-score Normalization funcione correctamente"""
        self.gestor.features = ['C']
        self.gestor.normalizable_columns = ['C']
        df_escalado = self.gestor.normalizar_z_score(['C'])
        self.assertAlmostEqual(df_escalado['C'].mean(), 0, places=1)
        self.assertAlmostEqual(df_escalado['C'].std(ddof=0), 1, places=1)

    def test_deteccion_outliers(self):
        """Verifica si se detectan valores atípicos (outliers)"""
        self.gestor.features = ['A']
        self.gestor.new_features = ['A']
        self.gestor.es_normalizable('A')
        tiene = self.gestor.tiene_outliers('A')
        self.assertTrue(tiene)
        self.assertIn('A', self.gestor.outlier_columns)

    def test_eliminacion_outliers(self):
        """Verifica que se eliminen correctamente los outliers"""
        self.gestor.features = ['A']
        self.gestor.new_features = ['A']
        self.gestor.es_normalizable('A')
        self.gestor.tiene_outliers('A')
        df_sin = self.gestor.eliminar_atipicos(['A'])
        self.assertLess(df_sin['A'].max(), 100)

    def test_reemplazo_outliers_por_mediana(self):
        """Verifica que los outliers se reemplacen correctamente por la mediana"""
        self.gestor.features = ['A']
        self.gestor.new_features = ['A']
        self.gestor.es_normalizable('A')
        self.gestor.tiene_outliers('A')
        df_reemplazo = self.gestor.reemplazar_atipicos_mediana(['A'])
        self.assertLessEqual(df_reemplazo['A'].max(), 4)

    def test_es_normalizable_en_datos_actuales(self):
        """Verifica si una columna del DataFrame original es normalizable"""
        es_normalizable = self.gestor.es_normalizable("C", og_df=True)
        self.assertTrue(es_normalizable)
        self.assertIn("C", self.gestor.original_normalizable_columns)

    def test_es_categorica_en_datos_actuales(self):
        """Verifica si una columna actual es categórica"""
        es_cat = self.gestor.es_categorica("B", og_df=False)
        self.assertTrue(es_cat)
        self.assertIn("B", self.gestor.categoric_columns)

    def test_actualizacion_new_features(self):
        """Verifica que new_features se actualice correctamente tras One-Hot Encoding"""
        self.gestor.features = ['B', 'C']
        self.gestor.categoric_columns = ['B']
        df_codificado = self.gestor.a_categorica(['B'], 1)
        self.assertIn('C', self.gestor.new_features)
        self.assertTrue(any(col.startswith('B_') for col in self.gestor.new_features))


if __name__ == '__main__':
    unittest.main()