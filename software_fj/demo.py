
from .gestor import GestorSoftwareFJ
from .excepciones import ErrorSistema
from .registro import configurar_registro


def ejecutar_demostracion() -> None:
    """Ejecuta 32 operaciones, incluidos errores, sin detenerse."""
    sistema = GestorSoftwareFJ(configurar_registro("logs"))
    exitos = 0
    fallos_controlados = 0
    operaciones = 0

    def paso(nombre, funcion):
        nonlocal exitos, fallos_controlados, operaciones
        operaciones += 1
        try:
            resultado = funcion()
        except ErrorSistema as exc:
            fallos_controlados += 1
            print(f"{operaciones:02d}. ERROR CONTROLADO | {nombre}: {exc}")
        except Exception as exc:
            fallos_controlados += 1
            sistema.logger.exception("Fallo inesperado durante la simulación")
            print(f"{operaciones:02d}. ERROR INESPERADO | {nombre}: {exc}")
        else:
            exitos += 1
            detalle = resultado.describir() if hasattr(resultado, "describir") else "OK"
            print(f"{operaciones:02d}. CORRECTO         | {nombre}: {detalle}")
        finally:
            sistema.logger.info("Paso de simulación %02d terminado: %s", operaciones, nombre)

    print("Software FJ - demostración de programación orientada a objetos")
    print("Datos de ejemplo ficticios. El sistema no utiliza base de datos.\n")
    paso("Registrar cliente válido", lambda: sistema.registrar_cliente("10000001", "Ana Ruiz", "ana@example.com", "3001234567"))
    paso("Rechazar correo inválido", lambda: sistema.registrar_cliente("10000002", "Luis Mora", "correo-invalido", "3001234568"))
    paso("Registrar segundo cliente", lambda: sistema.registrar_cliente("10000003", "Luis Mora", "luis@example.com", "3001234568"))
    paso("Rechazar documento duplicado", lambda: sistema.registrar_cliente("10000001", "Ana Torres", "otro@example.com", "3001234570"))
    paso("Registrar sala", lambda: sistema.registrar_sala("S001", "Sala de reuniones", 50000, 12))
    paso("Rechazar sala sin capacidad", lambda: sistema.registrar_sala("S002", "Sala fallida", 50000, 0))
    paso("Registrar equipo", lambda: sistema.registrar_equipo("E001", "Proyector HD", 30000, "Audiovisual"))
    paso("Rechazar tarifa negativa", lambda: sistema.registrar_equipo("E002", "Equipo fallido", -9000, "Audio"))
    paso("Registrar asesoría", lambda: sistema.registrar_asesoria("A001", "Consultoría técnica", 80000, "Redes"))
    paso("Rechazar especialidad vacía", lambda: sistema.registrar_asesoria("A002", "Consultoría fallida", 80000, ""))
    paso("Crear reserva de sala", lambda: sistema.crear_reserva("10000001", "S001", 2))
    paso("Confirmar reserva sala", lambda: sistema.confirmar_reserva(1))
    paso("Crear segunda reserva de sala", lambda: sistema.crear_reserva("10000003", "S001", 3))
    paso("Rechazar confirmación por sala ocupada", lambda: sistema.confirmar_reserva(2))
    paso("Cancelar primera reserva", lambda: sistema.cancelar_reserva(1))
    paso("Confirmar segunda reserva", lambda: sistema.confirmar_reserva(2, descuento=10))
    paso("Procesar segunda reserva", lambda: sistema.procesar_reserva(2))
    paso("Rechazar procesamiento duplicado", lambda: sistema.procesar_reserva(2))
    paso("Crear reserva de equipo", lambda: sistema.crear_reserva("10000001", "E001", 4))
    paso("Confirmar con descuento e IVA de ejemplo", lambda: sistema.confirmar_reserva(3, descuento=10, impuesto=19))
    paso("Procesar alquiler de equipo", lambda: sistema.procesar_reserva(3))
    paso("Crear reserva de asesoría", lambda: sistema.crear_reserva("10000003", "A001", 2))
    paso("Confirmar asesoría", lambda: sistema.confirmar_reserva(4))
    paso("Cancelar asesoría", lambda: sistema.cancelar_reserva(4))
    paso("Rechazar servicio inexistente", lambda: sistema.crear_reserva("10000001", "F999", 2))
    paso("Rechazar duración no permitida", lambda: sistema.crear_reserva("10000001", "A001", 30))
    paso("Deshabilitar sala", lambda: sistema.establecer_disponibilidad("S001", False))
    paso("Rechazar sala no disponible", lambda: sistema.crear_reserva("10000001", "S001", 2))
    paso("Habilitar sala", lambda: sistema.establecer_disponibilidad("S001", True))
    paso("Crear nueva reserva de sala", lambda: sistema.crear_reserva("10000001", "S001", 1))
    paso("Rechazar descuento excesivo", lambda: sistema.confirmar_reserva(5, descuento=200))
    paso("Confirmar después de error corregido", lambda: sistema.confirmar_reserva(5, descuento=5))

    print("\n--- RESUMEN ---")
    print(f"Total de operaciones: {operaciones}")
    print(f"Operaciones correctas: {exitos}")
    print(f"Errores controlados: {fallos_controlados}")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas registradas: {len(sistema.reservas)}")
    print("Se registraron los eventos y errores en logs/eventos.log")


if __name__ == "__main__":
    ejecutar_demostracion()
