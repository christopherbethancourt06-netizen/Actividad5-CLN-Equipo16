"""Configuración de las pruebas de la Unidad 5 (CLN) sobre el código REAL de Eventos Nova.

Las pruebas usan las capas existentes del proyecto (dominio, servicios de aplicación, composición en memoria y composición
persistente con PostgreSQL). No sustituyen ninguna clase del PIA: solo los puertos externos se reemplazan por dobles de prueba.
Ejecutar desde la raíz del repositorio:  python -m pytest tests_u5 -v"""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
for ruta in (os.path.join(RAIZ, 'src'), os.path.join(RAIZ, 'tests')):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)
