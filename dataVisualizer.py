import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from DataManager import DataManager
import itertools
import math

class VisualizerCLI:
    def __init__(self, df_original: pd.DataFrame, df_procesado: pd.DataFrame, original_features: list[str], processed_features: list[str], data_manager: DataManager):
        
        self.df_original = df_original
        self.df_procesado = df_procesado
        self.visualizacion_completada = False
        self.original_features = original_features
        self.processed_features = processed_features
        self.data_manager = data_manager
        self.og_categorical_features = []
        self.new_categorical_features = []
        self.og_numerical_features = []
        self.one_hot_features = []
        self.new_numerical_features = []

        for feature in self.original_features:
            
            if self.data_manager.is_categorical(feature, True):
                self.og_categorical_features.append(feature)
            elif self.data_manager.is_normalizable(feature, True):
                self.og_numerical_features.append(feature)

        for feature in self.processed_features:
            if feature in self.data_manager.one_hot_features:
                self.one_hot_features.append(feature)
            elif feature in self.og_categorical_features:
                self.new_categorical_features.append(feature)
            elif feature in self.og_numerical_features:
                self.new_numerical_features.append(feature)
        

    def mostrar_menu(self):
        while True:
            print("\n=============================")
            print("Visualización de Datos")
            print("=============================")
            print("Seleccione qué tipo de visualización desea generar:")
            print("  [1] Resumen estadístico de las variables seleccionadas")
            print("  [2] Histogramas de variables numéricas")
            print("  [3] Gráficos de dispersión antes y después de la normalización")
            print("  [4] Heatmap de correlación de variables numéricas")
            print("  [5] Volver al menú principal")
            try:
                opcion = input("Seleccione una opción: ").strip()
                if opcion == "1":
                    self.mostrar_resumen_estadistico()
                    self.visualizacion_completada = True
                    break
                elif opcion == "2":
                    self.mostrar_histogramas_variables_numericas()
                    self.visualizacion_completada = True
                    break
                elif opcion == "3":
                    self.graficos_dispersion()
                    self.visualizacion_completada = True
                    break
                elif opcion == "4":
                    self.generar_heatmap()
                    self.visualizacion_completada = True
                    break
                elif opcion == "5":
                    if self.visualizacion_completada == True:
                        print("\n[✓] Visualización completada.")
                        break
                    else:
                        print("\n Regresando al menú principal...")
                        break
                else:
                    print("Opción no válida. Inténtelo de nuevo.")
                    continue
            except:
                print("Opción no válida. Inténtelo de nuevo.")
                continue

    def mostrar_resumen_estadistico(self):
            
        print("\nResumen estadístico de las variables seleccionadas (antes del preprocesado):")
        print("\n================================================================")
        print("Resumen estadístico de variables categóricas (ANTES del preprocesado):")
        print("================================================================")

        resumen_categorico = []
        for feature in self.og_categorical_features:
            frecuencia = self.df_original[feature].value_counts()
            proporciones = self.df_original[feature].value_counts(normalize=True)
            moda = self.df_original[feature].mode()[0]
            num_unicas = self.df_original[feature].nunique()
            nulos = self.df_original[feature].isnull().sum()
            for categoria in frecuencia.index:
                resumen_categorico.append({
                    "Variable": feature,
                    "Categoría": categoria,
                    "Frecuencia": frecuencia[categoria],
                    "Proporción (%)": proporciones[categoria] * 100,
                    "Moda": moda,
                    "Número de categorías únicas": num_unicas,
                    "Número de valores nulos": nulos
                })

        resumen_df = pd.DataFrame(resumen_categorico)
        print(resumen_df.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables numéricas (ANTES del preprocesado):")
        print("================================================================")

        resumen_numerico = []
        for feature in self.og_numerical_features:
            media = self.df_original[feature].mean()
            mediana = self.df_original[feature].median()
            desviacion = self.df_original[feature].std()
            minimo = self.df_original[feature].min()
            maximo = self.df_original[feature].max()
            nulos = self.df_original[feature].isnull().sum()
            resumen_numerico.append({
                "Variable": feature,
                "Media": media,
                "Mediana": mediana,
                "Desviación estándar": desviacion,
                "Mínimo": minimo,
                "Máximo": maximo,
                "0.25 ": self.df_original[feature].quantile(0.25),
                "0.50": self.df_original[feature].quantile(0.50),
                "0.75": self.df_original[feature].quantile(0.75),
                "Número de valores nulos": nulos
            })
        resumen_df_numerico = pd.DataFrame(resumen_numerico)
        print(resumen_df_numerico.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables categóricas (DESPUÉS del preprocesado):")
        print("================================================================")
        
        resumen_categorico_procesado = []
        lista_columnas = []
        if len(self.one_hot_features) > 0:
            lista_columnas = self.one_hot_features
        else:
            lista_columnas = self.new_categorical_features

        for feature in lista_columnas:
            frecuencia = self.df_procesado[feature].value_counts()
            proporciones = self.df_procesado[feature].value_counts(normalize=True)
            moda_serie = self.df_procesado[feature].mode()
            moda = moda_serie[0] if not moda_serie.empty else None  # o "Sin moda"
            num_unicas = self.df_procesado[feature].nunique()
            nulos = self.df_procesado[feature].isnull().sum()
            for categoria in frecuencia.index:
                resumen_categorico_procesado.append({
                    "Variable": feature,
                    "Categoría": categoria,
                    "Frecuencia": frecuencia[categoria],
                    "Proporción (%)": proporciones[categoria] * 100,
                    "Moda": moda,
                    "Número de categorías únicas": num_unicas,
                    "Número de valores nulos": nulos
                })
        resumen_df_procesado = pd.DataFrame(resumen_categorico_procesado)
        print(resumen_df_procesado.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables numéricas (DESPUÉS del preprocesado):")
        print("================================================================")

        resumen_numerico_procesado = []
        for feature in self.new_numerical_features:
            media = self.df_procesado[feature].mean()
            mediana = self.df_procesado[feature].median()
            desviacion = self.df_procesado[feature].std()
            minimo = self.df_procesado[feature].min()
            maximo = self.df_procesado[feature].max()
            nulos = self.df_procesado[feature].isnull().sum()
            resumen_numerico_procesado.append({
                "Variable": feature,
                "Media": media,
                "Mediana": mediana,
                "Desviación estándar": desviacion,
                "Mínimo": minimo,
                "Máximo": maximo,
                "0.25 ": self.df_procesado[feature].quantile(0.25),
                "0.50": self.df_procesado[feature].quantile(0.50),
                "0.75": self.df_procesado[feature].quantile(0.75),
                "Número de valores nulos": nulos
            })
        
        resumen_df_numerico_procesado = pd.DataFrame(resumen_numerico_procesado) 
        print(resumen_df_numerico_procesado.to_string(index=False))
        print("\n================================================================")

        


    def mostrar_histogramas_variables_numericas(self):
        print("\n=======================================")
        print("Histograma de variables numéricas (ANTES del preprocesado):")
        print("=======================================")
        for col in self.og_numerical_features:
            plt.figure(figsize=(6, 4))
            sns.histplot(self.df_original[col].dropna(), bins=30, kde=True, color='skyblue')
            plt.title(f'Histograma de {col} (Original)')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        print("\n=======================================")
        print("Histograma de variables numéricas (DESPUÉS del preprocesado):")
        print("=======================================")
        for col in self.new_numerical_features:
            plt.figure(figsize=(6, 4))
            sns.histplot(self.df_procesado[col].dropna(), bins=30, kde=True, color='lightgreen')
            plt.title(f'Histograma de {col} (Procesado)')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def graficos_dispersion(self):

        print("\n=======================================")
        print("Gráficos de dispersión para todas las combinaciones 2 a 2")
        print("=======================================")
        combinaciones = list(itertools.combinations(self.og_numerical_features, 2))
        for var_x, var_y in combinaciones:
            if var_x not in self.df_procesado.columns or var_y not in self.df_procesado.columns:
                continue  # Ignora combinaciones donde alguna variable no esté en el DataFrame procesado
            # Gráfico antes del preprocesado
            plt.figure(figsize=(6, 5))
            sns.scatterplot(data=self.df_original, x=var_x, y=var_y, color="blue", alpha=0.6)
            plt.title(f'Dispersión de {var_x} vs {var_y} (Antes del preprocesado)')
            plt.xlabel(var_x)
            plt.ylabel(var_y)
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            # Gráfico después del preprocesado
            plt.figure(figsize=(6, 5))
            sns.scatterplot(data=self.df_procesado, x=var_x, y=var_y, color="green", alpha=0.6)
            plt.title(f'Dispersión de {var_x} vs {var_y} (Después del preprocesado)')
            plt.xlabel(var_x)
            plt.ylabel(var_y)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

   


    def obtener_prefijo_base(self, col):
        # Por ejemplo, toma todo hasta el primer guion bajo
        # Ajusta si tu naming es distinto
        return col.split('_')[0]

    def generar_heatmap(self, min_freq=20):

        print("\n=======================================")
        print("Heatmaps de correlación y frecuencia")
        print("=======================================")

        heatmaps = []
        titulos = []

        # Correlación variables numéricas (antes y después)
        if len(self.og_numerical_features) >= 2:
            corr_matrix = self.df_original[self.og_numerical_features].corr()
            heatmaps.append(corr_matrix)
            titulos.append("Correlación variables numéricas (Antes)")

        if len(self.new_numerical_features) >= 2:
            corr_matrix_proc = self.df_procesado[self.new_numerical_features].corr()
            heatmaps.append(corr_matrix_proc)
            titulos.append("Correlación variables numéricas (Después)")

        # Frecuencias variables categóricas originales (filtrar categorías con pocas muestras)
        if len(self.og_categorical_features) >= 2:
            for var1, var2 in itertools.combinations(self.og_categorical_features, 2):
                freq_var1 = self.df_original[var1].value_counts()
                freq_var2 = self.df_original[var2].value_counts()
                cats_var1 = freq_var1[freq_var1 >= min_freq].index
                cats_var2 = freq_var2[freq_var2 >= min_freq].index

                df_filtered = self.df_original[
                    self.df_original[var1].isin(cats_var1) & self.df_original[var2].isin(cats_var2)
                ]

                if df_filtered.empty:
                    continue

                cross_tab = pd.crosstab(df_filtered[var1], df_filtered[var2])
                if (cross_tab == 0).mean().mean() > 0.7:
                    continue

                heatmaps.append(cross_tab)
                titulos.append(f'Frecuencia cruzada: {var1} vs {var2} (Antes)')

        # Frecuencias variables categóricas procesadas (filtrado + no comparar mismas categorías)
        columnas_categoricas_proc = self.one_hot_features if self.one_hot_features else self.new_categorical_features
        if len(columnas_categoricas_proc) >= 2:
            for var1, var2 in itertools.combinations(columnas_categoricas_proc, 2):
                # Saltar si mismo prefijo base (misma variable codificada)
                if self.obtener_prefijo_base(var1) == self.obtener_prefijo_base(var2):
                    continue

                freq_var1 = self.df_procesado[var1].value_counts()
                freq_var2 = self.df_procesado[var2].value_counts()
                cats_var1 = freq_var1[freq_var1 >= min_freq].index
                cats_var2 = freq_var2[freq_var2 >= min_freq].index

                df_filtered = self.df_procesado[
                    self.df_procesado[var1].isin(cats_var1) & self.df_procesado[var2].isin(cats_var2)
                ]

                if df_filtered.empty:
                    continue

                cross_tab = pd.crosstab(df_filtered[var1], df_filtered[var2])
                if (cross_tab == 0).mean().mean() > 0.7:
                    continue

                heatmaps.append(cross_tab)
                titulos.append(f'Frecuencia cruzada: {var1} vs {var2} (Después)')

        # Mostrar en páginas de 6 como antes
        max_por_pagina = 6
        total = len(heatmaps)
        paginas = math.ceil(total / max_por_pagina)
        filas, columnas = 2, 3

        for p in range(paginas):
            start = p * max_por_pagina
            end = min(start + max_por_pagina, total)
            cantidad = end - start

            fig, axes = plt.subplots(filas, columnas, figsize=(6 * columnas, 5 * filas))
            axes = axes.flatten()

            for i in range(max_por_pagina):
                ax = axes[i]
                if start + i < end:
                    idx = start + i
                    sns.heatmap(
                        heatmaps[idx],
                        annot=True if heatmaps[idx].shape[0] < 20 and heatmaps[idx].shape[1] < 20 else False,
                        cmap='coolwarm' if 'Correlación' in titulos[idx] else 'Blues',
                        center=0 if 'Correlación' in titulos[idx] else None,
                        ax=ax,
                        cbar=True
                    )
                    ax.set_title(titulos[idx], fontsize=10, pad=12)
                    ax.set_xlabel('')
                    ax.set_ylabel('')
                else:
                    ax.axis('off')

            plt.tight_layout()
            plt.show()



        
        

    def visualizacion_completa(self):
        return self.visualizacion_completada
