import pandas as pd
import os

class ExporterCLI:
    """
    Clase encargada de gestionar la exportación de un DataFrame procesado
    a formatos como CSV o Excel, dentro de una aplicación CLI.

    Atributos:
        df_procesado (pd.DataFrame): El DataFrame ya procesado listo para exportar.
        menu_state (dict): Diccionario que guarda el estado del flujo de trabajo del menú.
    """

    def __init__(self, df_procesado, menu_state):
        """
        Inicializa la clase ExporterCLI con el DataFrame y el estado del menú.

        Args:
            df_procesado (pd.DataFrame): DataFrame que contiene los datos preprocesados.
            menu_state (dict): Diccionario con los estados del flujo del menú.
        """
        self.df_procesado = df_procesado
        self.menu_state = menu_state

    def exportar_datos(self):
        """
        Inicia el proceso de exportación de datos si la visualización fue completada.

        Solicita al usuario el formato de exportación y el nombre del archivo, luego 
        guarda el DataFrame en el formato seleccionado.

        Modifica:
            self.menu_state["exportacion_completada"]: Se establece en True si la exportación fue exitosa.
        """
        print("\n=====================")
        print(" Exportación de datos")
        print("=====================")

        formato = self.pedir_formato()
        if not formato:
            print("❌ Formato no válido. Cancelando exportación.")
            return

        nombre_archivo = input("Ingrese el nombre del archivo (sin extensión): ").strip()
        if not nombre_archivo:
            print("❌ Nombre de archivo vacío. Cancelando exportación.")
            return

        ruta = f"{nombre_archivo}.{formato}"

        try:
            if formato == "csv": 
                self.df_procesado.to_csv(ruta, index=False)
            elif formato == "xlsx":
                self.df_procesado.to_excel(ruta, index=False)

            print(f"✅ Archivo exportado exitosamente como '{ruta}'")
            self.menu_state["exportacion_completada"] = True

        except Exception as e:
            print(f"❌ Error al exportar: {e}")

    def pedir_formato(self):
        """
        Solicita al usuario que seleccione el formato de exportación.

        Returns:
            str or None: 'csv' o 'xlsx' si se selecciona un formato válido,
                         None si se cancela la operación.
        """
        while True:
            print("\nSeleccione el formato de exportación:")
            print("[1] CSV")
            print("[2] Excel (.xlsx)")
            print("[3] Volver al menú principal")

            opcion = input("Seleccione una opción: ").strip()
            if opcion == "1":
                return "csv"
            elif opcion == "2":
                return "xlsx"
            elif opcion == "3":
                print("Volviendo al menú principal...")
                return None
            else:
                print("Opción no válida")
                continue
