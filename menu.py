"""Interfaz de consola opcional para utilizar el sistema de forma interactiva.

Los datos permanecen en memoria; solo los eventos y errores se guardan en logs.
"""
from software_fj.excepciones import ErrorSistema, ErrorValidacion
from software_fj.gestor import GestorSoftwareFJ
from software_fj.registro import configurar_registro


def entero(mensaje: str) -> int:
    """Lee un entero e informa por qué una entrada no es válida."""
    valor = input(mensaje).strip()
    try:
        return int(valor)
    except ValueError as exc:
        raise ErrorValidacion('Debe escribir un número entero.') from exc


def listar(coleccion, etiqueta: str) -> None:
    """Muestra los registros disponibles sin revelar datos privados."""
    print(f'\n{etiqueta}:')
    if not coleccion:
        print('  No hay registros.')
    for elemento in coleccion:
        print(' -', elemento.describir())


def ejecutar_menu() -> None:
    """Procesa las operaciones y continúa después de errores de validación."""
    sistema = GestorSoftwareFJ(configurar_registro())
    opciones = '''
Software FJ | Clientes, servicios y reservas
 1. Registrar cliente
 2. Registrar servicio de sala
 3. Registrar servicio de equipo
 4. Registrar servicio de asesoría
 5. Crear reserva
 6. Confirmar reserva
 7. Cancelar reserva
 8. Procesar reserva
 9. Cambiar disponibilidad de un servicio
10. Listar clientes, servicios y reservas
 0. Salir
'''
    while True:
        print(opciones)
        try:
            opcion = input('Seleccione una opción: ').strip()
            if opcion == '0':
                print('Programa finalizado.')
                break
            if opcion == '1':
                sistema.registrar_cliente(input('Documento: '), input('Nombre: '),
                                         input('Correo: '), input('Teléfono: '))
            elif opcion in ('2', '3', '4'):
                codigo = input('Código: ')
                nombre = input('Nombre del servicio: ')
                tarifa = input('Tarifa por hora: ')
                if opcion == '2':
                    sistema.registrar_sala(codigo, nombre, tarifa, entero('Capacidad: '))
                elif opcion == '3':
                    sistema.registrar_equipo(codigo, nombre, tarifa, input('Categoría: '))
                else:
                    sistema.registrar_asesoria(codigo, nombre, tarifa, input('Especialidad: '))
            elif opcion == '5':
                reserva = sistema.crear_reserva(input('Documento del cliente: '),
                                                input('Código del servicio: '),
                                                entero('Duración en horas: '))
                print('Reserva registrada:', reserva.describir())
            elif opcion == '6':
                numero = entero('Número de reserva: ')
                descuento = input('Descuento porcentual (0 si no aplica): ')
                impuesto = input('Impuesto porcentual (0 si no aplica): ')
                reserva = sistema.confirmar_reserva(numero, descuento=descuento, impuesto=impuesto)
                print('Reserva confirmada:', reserva.describir())
            elif opcion == '7':
                sistema.cancelar_reserva(entero('Número de reserva: '))
            elif opcion == '8':
                sistema.procesar_reserva(entero('Número de reserva: '))
            elif opcion == '9':
                codigo = input('Código del servicio: ')
                disponible = input('¿Disponible? (s/n): ').strip().lower()
                if disponible not in ('s', 'n'):
                    raise ErrorValidacion('Responda s o n.')
                sistema.establecer_disponibilidad(codigo, disponible == 's')
            elif opcion == '10':
                listar(sistema.clientes, 'Clientes')
                listar(sistema.servicios, 'Servicios')
                listar(sistema.reservas, 'Reservas')
                continue
            else:
                print('Opción no reconocida.')
                continue
            print('Operación realizada.')
        except ErrorSistema as exc:
            # El gestor audita las reglas de negocio; el menú controla entradas.
            sistema.logger.warning('Entrada u operación rechazada: %s', exc)
            print('No se completó la operación:', exc)
        except (KeyboardInterrupt, EOFError):
            print('\nPrograma finalizado por el usuario.')
            break
        except Exception:
            # El error queda registrado sin mostrar una traza al usuario final.
            sistema.logger.exception('Error inesperado en el menú')
            print('Se presentó un error inesperado. Puede continuar.')


if __name__ == '__main__':
    ejecutar_menu()
