# Qué sustituir en GitHub y cómo usarlo

Este paquete es una **versión nueva completa** del repositorio. No mezcles artefactos antiguos con código nuevo: los modelos se entrenaron y evaluaron otra vez y sus ficheros nuevos están en artefactos/ (sin segunda carpeta interior).

| En GitHub | Acción concreta | Razón |
|---|---|---|
| entrenar.py | Sustituir | Datos limpios, separación por ASSETID, baselines, bandas calibradas, test, pruebas espacial/temporal, ablación y simulación de entradas de la app |
| app.py | Sustituir | Carga exactamente los nuevos modelos/metadatos, distingue test 2018 y proyección posterior, presenta MAE de la interfaz |
| modelado.py | Añadir en la raíz | Limpieza, variables y métricas compartidas |
| geografia.py | Añadir en la raíz | Lectura de R y asignación de distritos |
| actualizar_indice.py | Sustituir | Importación de niveles documentados desde CSV, sin aplicar automáticamente índices autonómicos como si fueran niveles distritales |
| indice.json | Sustituir | Mantiene los niveles heredados con aviso explícito de que necesitan revisión; puedes quitarlo para desactivar la proyección |
| requirements.txt | Sustituir | Versiones compatibles y reproducibles |
| LEEME.md, data/README.md | Sustituir/añadir | Método, instrucciones, fuente y licencia |
| notebooks/TFM_analisis_y_validacion.ipynb | Añadir | Notebook único del experimento final, listo para ejecutarse en Colab y exportarse a HTML |
| tests/test_contrato.py | Añadir | Comprueba que ni PRICE ni PERIOD entran al modelo, la calibración y la carga de modelos |
| artefactos/* | Sustituir TODO el contenido anterior por los 19 archivos nuevos | Nueve modelos, tres metadatos, tres muestras de ofertas, tres análisis de error y resumen.json coherentes entre sí |
| artefactos/artefactos/ | **Borrar** si sigue existiendo | Contiene modelos y estadísticas del diseño antiguo; su presencia puede servir predicciones equivocadas |
| config.toml en la raíz | Borrar si está sin usar | La configuración activa de Streamlit está en .streamlit/config.toml |
| .devcontainer/devcontainer.json | Sustituir | Python 3.12 y arranque sencillo |

## Colab y entrega UCM

1. En GitHub, sube el proyecto conservando rutas y nombres del ZIP. Los archivos de modelo .ubj van directamente en artefactos/.
2. Conserva data(2).zip aparte como fuente de reproducción. **No es necesario subir los .rda a GitHub**; al abrir el notebook en Colab, sube juntos el ZIP del nuevo proyecto y data(2).zip. La primera celda prepara los archivos.
3. Ejecuta el notebook desde la primera celda hasta la última y exporta el resultado a HTML. No presentes el notebook anterior con 47.841 anuncios Q4 como si describiera este motor de tres ciudades.
4. Inserta/adapta SECCIONES_PARA_MEMORIA.md en tu documento Word original; este no se recibió con los adjuntos de este turno. Mantén el cuerpo en 20 caras como máximo, y pon notebook y código como anexos.
5. Cambia las cifras de tu memoria por las de artefactos/resumen.json. Las de los antiguos .ubj o del notebook anterior NO son comparables.
6. Revisa los niveles del indice.json con fuente, enlace y fecha por distrito antes de referirte a ellos como mercado actual. Para actualizar, prepara un CSV con columnas ciudad,distrito,eur_m2,fecha,fuente,url, con una fila _ciudad por cada ciudad incluida, y ejecuta python actualizar_indice.py niveles.csv. Las bandas y MAE de 2018 siguen sin estar validadas después de esta operación.
7. Verifica python -m unittest discover -s tests y python -m streamlit run app.py. Comprueba que el enlace de GitHub/Drive sea visible a los tutores.

## Qué herramientas académicas se utilizaron

Python 3.12 para ejecución; rdata para leer los objetos de R; pandas y NumPy para limpieza y atributos; Shapely para asignar distritos a coordenadas; scikit-learn para separar por ASSETID, referencias y métricas; XGBoost para tres regresiones cuantílicas y contribuciones SHAP nativas; Streamlit para una demostración que consume los artefactos guardados; matplotlib en el notebook para resultados. Se emplearon además pruebas de contrato con unittest. **No se ha ejecutado Colab ni subido nada a tu GitHub**: el notebook y los archivos están preparados para que lo hagas desde tu cuenta.
