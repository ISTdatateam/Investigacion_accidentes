from pathlib import Path
import pandas as pd


def inicializar_csv():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Empresas
    pd.DataFrame(columns=[
        'rut', 'nombre', 'direccion', 'giro', 'fecha_registro'
    ]).to_csv(data_dir / "empresas.csv", index=False)

    # Centros de trabajo
    pd.DataFrame(columns=[
        'cuv', 'rut_empresa', 'nombre_centro', 'tipo_calle',
        'nombre_calle', 'numero', 'resto_direccion', 'comuna'
    ]).to_csv(data_dir / "centros_trabajo.csv", index=False)

    # Accidentes
    pd.DataFrame(columns=[
        'id', 'cuv_centro', 'fecha', 'hora', 'direccion', 'descripcion'
    ]).to_csv(data_dir / "accidentes.csv", index=False)

    # Trabajadores
    pd.DataFrame(columns=[
        'id', 'accidente_id', 'ap_paterno', 'ap_materno', 'nombres',
        'origen_doc', 'id_doc', 'fecha_nacimiento', 'sexo'
    ]).to_csv(data_dir / "trabajadores.csv", index=False)

    # Causas
    pd.DataFrame(columns=[
        'accidente_id', 'ubicacion', 'codigo', 'glosa'
    ]).to_csv(data_dir / "causas.csv", index=False)


if __name__ == "__main__":
    inicializar_csv()
    print("Archivos CSV iniciales creados exitosamente!")