import pandas as pd
import os

class ExporterCLI:
    def __init__(self, df_procesado, menu_state):
        self.df_procesado = df_procesado
        self.menu_state = menu_state

    def exportar_datos(self):
        print("\n=====================")
        print(" Exportación de datos")
        print("=====================")

        if not self.menu_state.get("visualizacion_completada", False):
            print("⚠️ La visualización no ha sido completada. No se puede exportar.")
            return

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
