# Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto individual desarrollado para el curso Programación (213023) de la UNAD, basado en el ejercicio 1 del anexo de prácticas simuladas. Empresa ficticia: Software FJ.

## Requisitos

- Python 3.11 o posterior.
- No necesita instalar librerías ni usar una base de datos.

## Ejecución

Desde la carpeta principal del proyecto:

```bash
python main.py
```

En Windows también puede utilizar `py main.py`.

## Menú interactivo

Para registrar clientes y administrar servicios o reservas mediante un menú en consola:

```bash
python menu.py
```

Puede ingresar opciones, efectuar altas, confirmar/cancelar/procesar reservas y listar objetos. No se utiliza base de datos ni se guardan clientes, servicios o reservas al cerrar.

## Pruebas automáticas

```bash
python -m unittest discover -s tests -v
```

## Archivos

- `software_fj/entidades.py`: clase abstracta `Entidad` y clase `Cliente` con encapsulación.
- `software_fj/servicios.py`: clase abstracta `Servicio` y las implementaciones `Sala`, `Equipo` y `Asesoria`.
- `software_fj/reservas.py`: reserva y transiciones de estado.
- `software_fj/gestor.py`: altas, consultas, validaciones y bloqueo de servicios confirmados.
- `software_fj/excepciones.py`: errores de negocio personalizados.
- `software_fj/registro.py`: eventos y errores en `logs/eventos.log`.
- `software_fj/demo.py`: 32 operaciones con datos ficticios, correctas y fallidas.
- `tests/`: pruebas unitarias con biblioteca estándar.
- `evidencias/resultado_simulacion.txt`: salida real de la demostración, generada mediante redirección de consola.
- `evidencias/resultado_pruebas.txt`: ejecución real de las pruebas automáticas.
- `menu.py`: interfaz de consola opcional.


## Arquitectura y decisiones

- La información de clientes, servicios y reservas se mantiene solo en **memoria** con diccionarios y objetos. Se pierde al cerrar la ejecución, tal como requiere el ejercicio sin persistencia de datos.
- Los únicos archivos que escribe la aplicación son los registros de eventos y errores (logs). El archivo `evidencias/resultado_simulacion.txt` se genera fuera de la aplicación con la redirección de la consola.
- La abstracción se representa con `Entidad` y `Servicio`. Se implementan herencia, polimorfismo y sobreescritura en los tres servicios.
- Python no permite la sobrecarga tradicional por múltiples definiciones del mismo método. Se muestran firmas con `typing.overload` y se implementan argumentos opcionales para calcular costo normal, con descuento y/o impuesto.
- Se utilizan `try/except/else` en el decorador `auditar`, `try/except` en las validaciones, `try/except` con encadenamiento (`raise ... from ...`) al buscar registros y manejar errores numéricos, y `try/except/finally` en las simulaciones y pruebas automáticas.
- Una reserva confirmada bloquea su servicio; al procesarse o cancelarse, se libera. Los servicios deshabilitados no pueden confirmarse.
- Las duraciones máximas establecidas para la demostración son 24 horas para salas, 168 para equipos y 8 para asesorías. Son decisiones de implementación, no cifras exigidas por el enunciado.
- El impuesto de ejemplo de 19 % en una operación es un dato de prueba configurable, no una inferencia de obligaciones tributarias de Software FJ.

