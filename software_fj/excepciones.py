"""Excepciones específicas del sistema de clientes, servicios y reservas."""


class ErrorSistema(Exception):
    """Clase base para errores controlados del sistema."""


class ErrorValidacion(ErrorSistema):
    """Los datos recibidos no cumplen las reglas del negocio."""


class RegistroDuplicado(ErrorSistema):
    """Ya existe un cliente o servicio con el identificador informado."""


class RegistroNoEncontrado(ErrorSistema):
    """No existe el registro solicitado."""


class ServicioNoDisponible(ErrorSistema):
    """El servicio no se encuentra disponible para reservar."""


class ReservaInvalida(ErrorSistema):
    """La reserva no puede crearse con los datos recibidos."""


class EstadoReservaInvalido(ErrorSistema):
    """Se intenta realizar una transición de estado no permitida."""


class CalculoInvalido(ErrorSistema):
    """No es posible calcular el valor a cobrar con esos parámetros."""
