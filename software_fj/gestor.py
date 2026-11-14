"""Gestor de clientes, servicios y reservas mantenidos solo en memoria."""
from functools import wraps
import logging
from typing import Callable, TypeVar, ParamSpec

from .entidades import Cliente
from .excepciones import (
    ErrorSistema, RegistroDuplicado, RegistroNoEncontrado,
    ServicioNoDisponible,
)
from .registro import configurar_registro
from .reservas import Reserva
from .servicios import Sala, Equipo, Asesoria, Servicio

P = ParamSpec("P")
R = TypeVar("R")


def auditar(operacion: Callable[P, R]) -> Callable[P, R]:
    """Registra eventos exitosos y errores antes de propagarlos al llamador."""
    @wraps(operacion)
    def envoltura(*args: P.args, **kwargs: P.kwargs) -> R:
        gestor = args[0]
        try:
            resultado = operacion(*args, **kwargs)
        except ErrorSistema as exc:
            gestor.logger.error("%s rechazado: %s", operacion.__name__, exc)
            raise
        except Exception:
            gestor.logger.exception("Error inesperado en %s", operacion.__name__)
            raise
        else:
            gestor.logger.info("Operación completada: %s", operacion.__name__)
            return resultado
    return envoltura


class GestorSoftwareFJ:
    """Coordina operaciones, evita duplicados y reservas simultáneas."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger if logger is not None else configurar_registro()
        self.__clientes: dict[str, Cliente] = {}
        self.__servicios: dict[str, Servicio] = {}
        self.__reservas: dict[int, Reserva] = {}
        self.__reservas_activas: dict[str, int] = {}
        self.__siguiente_numero = 1

    @auditar
    def registrar_cliente(self, documento: str, nombre: str, correo: str, telefono: str) -> Cliente:
        cliente = Cliente(documento, nombre, correo, telefono)
        if cliente.identificador in self.__clientes:
            raise RegistroDuplicado("Ya existe un cliente con ese documento.")
        self.__clientes[cliente.identificador] = cliente
        return cliente

    @auditar
    def registrar_sala(self, codigo: str, nombre: str, tarifa: object, capacidad: int) -> Sala:
        sala = Sala(codigo, nombre, tarifa, capacidad)
        self._guardar_servicio(sala)
        return sala

    @auditar
    def registrar_equipo(self, codigo: str, nombre: str, tarifa: object, categoria: str) -> Equipo:
        equipo = Equipo(codigo, nombre, tarifa, categoria)
        self._guardar_servicio(equipo)
        return equipo

    @auditar
    def registrar_asesoria(self, codigo: str, nombre: str, tarifa: object, especialidad: str) -> Asesoria:
        asesoria = Asesoria(codigo, nombre, tarifa, especialidad)
        self._guardar_servicio(asesoria)
        return asesoria

    def _guardar_servicio(self, servicio: Servicio) -> None:
        if servicio.identificador in self.__servicios:
            raise RegistroDuplicado("Ya existe un servicio con ese código.")
        self.__servicios[servicio.identificador] = servicio

    def _buscar_cliente(self, documento: str) -> Cliente:
        try:
            return self.__clientes[documento]
        except (KeyError, TypeError) as exc:
            raise RegistroNoEncontrado("Cliente no encontrado.") from exc

    def _buscar_servicio(self, codigo: str) -> Servicio:
        try:
            return self.__servicios[codigo]
        except (KeyError, TypeError) as exc:
            raise RegistroNoEncontrado("Servicio no encontrado.") from exc

    def _buscar_reserva(self, numero: int) -> Reserva:
        try:
            return self.__reservas[numero]
        except (KeyError, TypeError) as exc:
            raise RegistroNoEncontrado("Reserva no encontrada.") from exc

    @auditar
    def crear_reserva(self, documento: str, codigo: str, horas: int) -> Reserva:
        cliente = self._buscar_cliente(documento)
        servicio = self._buscar_servicio(codigo)
        if not servicio.disponible:
            raise ServicioNoDisponible("No se pueden reservar servicios deshabilitados.")
        reserva = Reserva(self.__siguiente_numero, cliente, servicio, horas)
        self.__reservas[reserva.numero] = reserva
        self.__siguiente_numero += 1
        return reserva

    @auditar
    def confirmar_reserva(self, numero: int, *, descuento: object = 0, impuesto: object = 0) -> Reserva:
        reserva = self._buscar_reserva(numero)
        # El estado se verifica antes de modificar el bloqueo y el importe.
        if reserva.estado != "creada":
            from .excepciones import EstadoReservaInvalido
            raise EstadoReservaInvalido("Solo se puede confirmar una reserva creada.")
        codigo = reserva.servicio.identificador
        if codigo in self.__reservas_activas:
            raise ServicioNoDisponible("Servicio ocupado por otra reserva confirmada.")
        # El cálculo valida disponibilidad, duración, impuestos y descuentos.
        total = reserva.servicio.calcular_costo(
            reserva.horas, descuento=descuento, impuesto=impuesto
        )
        reserva.confirmar(total)
        self.__reservas_activas[codigo] = numero
        return reserva

    @auditar
    def cancelar_reserva(self, numero: int) -> Reserva:
        reserva = self._buscar_reserva(numero)
        reserva.cancelar()
        codigo = reserva.servicio.identificador
        if self.__reservas_activas.get(codigo) == numero:
            del self.__reservas_activas[codigo]
        return reserva

    @auditar
    def procesar_reserva(self, numero: int) -> Reserva:
        reserva = self._buscar_reserva(numero)
        reserva.procesar()
        codigo = reserva.servicio.identificador
        if self.__reservas_activas.get(codigo) == numero:
            del self.__reservas_activas[codigo]
        return reserva

    @auditar
    def establecer_disponibilidad(self, codigo: str, disponible: bool) -> Servicio:
        servicio = self._buscar_servicio(codigo)
        if codigo in self.__reservas_activas and not disponible:
            raise ServicioNoDisponible("No se puede deshabilitar un servicio reservado.")
        servicio.cambiar_disponibilidad(disponible)
        return servicio

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self.__clientes.values())

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self.__servicios.values())

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self.__reservas.values())
