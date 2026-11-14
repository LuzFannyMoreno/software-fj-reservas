"""Reserva: relaciones entre cliente/servicio y control de estados."""
from decimal import Decimal

from .entidades import Cliente
from .excepciones import EstadoReservaInvalido, ErrorValidacion
from .servicios import Servicio


class Reserva:
    """Reserva con transiciones permitidas: creada -> confirmada -> procesada.

    Una reserva creada o confirmada también puede cancelarse.
    """

    def __init__(self, numero: int, cliente: Cliente, servicio: Servicio, horas: int) -> None:
        if type(numero) is not int or numero < 1:
            raise ErrorValidacion("Número de reserva incorrecto.")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva requiere cliente y servicio válidos.")
        servicio.validar_parametros(horas)
        self.__numero = numero
        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__estado = "creada"
        self.__total: Decimal | None = None

    @property
    def numero(self) -> int:
        return self.__numero

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def horas(self) -> int:
        return self.__horas

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def total(self) -> Decimal | None:
        return self.__total

    def confirmar(self, total: Decimal) -> None:
        """Confirma la reserva con un importe calculado y validado."""
        if self.estado != "creada":
            raise EstadoReservaInvalido("Solo se puede confirmar una reserva creada.")
        if not isinstance(total, Decimal) or not total.is_finite() or total < 0:
            raise ErrorValidacion("El total de reserva no es válido.")
        self.__total = total
        self.__estado = "confirmada"

    def procesar(self) -> None:
        """Marca la prestación del servicio como finalizada."""
        if self.estado != "confirmada":
            raise EstadoReservaInvalido("Solo se puede procesar una reserva confirmada.")
        self.__estado = "procesada"

    def cancelar(self) -> None:
        """Impide cancelar reservas ya procesadas o canceladas."""
        if self.estado not in ("creada", "confirmada"):
            raise EstadoReservaInvalido("No se puede cancelar en el estado actual.")
        self.__estado = "cancelada"

    def describir(self) -> str:
        total = "pendiente" if self.total is None else f"${self.total:,.2f}"
        return (f"Reserva {self.numero} | Cliente {self.cliente.identificador} | "
                f"Servicio {self.servicio.identificador} | {self.horas} h | "
                f"{self.estado} | Total: {total}")
