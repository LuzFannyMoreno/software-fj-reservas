"""Servicios abstractos, polimorfismo, sobreescritura y cálculo monetario."""
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import overload

from .entidades import Entidad, _texto_no_vacio
from .excepciones import CalculoInvalido, ErrorValidacion, ReservaInvalida, ServicioNoDisponible


CENTAVO = Decimal("0.01")


def _decimal(valor: object, campo: str, error=ErrorValidacion) -> Decimal:
    """Convierte números finitos a Decimal y rechaza tipos no numéricos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise error(f"{campo} debe ser numérico.")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation as exc:
        raise error(f"{campo} debe ser numérico.") from exc
    if not numero.is_finite():
        raise error(f"{campo} debe ser un número finito.")
    return numero


class Servicio(Entidad, ABC):
    """Servicio abstracto con tarifa, disponibilidad y cálculo reutilizable."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: object) -> None:
        super().__init__(codigo)
        self._nombre = _texto_no_vacio(nombre, "Nombre del servicio")
        self._tarifa_hora = _decimal(tarifa_hora, "Tarifa")
        if self._tarifa_hora <= 0:
            raise ErrorValidacion("Tarifa: debe ser mayor que cero.")
        self._disponible = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> Decimal:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool) -> None:
        if not isinstance(disponible, bool):
            raise ErrorValidacion("La disponibilidad debe ser verdadero o falso.")
        self._disponible = disponible

    @staticmethod
    def _validar_horas(horas: int, maximo: int) -> None:
        if type(horas) is not int or not 1 <= horas <= maximo:
            raise ReservaInvalida(f"Duración: número entero entre 1 y {maximo} horas.")

    @abstractmethod
    def validar_parametros(self, horas: int) -> None:
        """Valida la duración para el tipo de servicio concreto."""

    @abstractmethod
    def describir(self) -> str:
        """Describe las propiedades de cada servicio concreto."""

    @overload
    def calcular_costo(self, horas: int) -> Decimal: ...

    @overload
    def calcular_costo(self, horas: int, *, descuento: object) -> Decimal: ...

    @overload
    def calcular_costo(self, horas: int, *, descuento: object, impuesto: object) -> Decimal: ...

    def calcular_costo(
        self, horas: int, *, descuento: object = 0, impuesto: object = 0
    ) -> Decimal:
        """Aplica porcentaje de descuento y luego porcentaje de impuesto.

        Se admiten diversas firmas mediante argumentos opcionales y @overload.
        Los porcentajes se expresan de 0 a 100, no como fracciones.
        """
        self.validar_parametros(horas)
        if not self.disponible:
            raise ServicioNoDisponible(f"Servicio {self.identificador} deshabilitado.")
        porcentaje_desc = _decimal(descuento, "Descuento", CalculoInvalido)
        porcentaje_imp = _decimal(impuesto, "Impuesto", CalculoInvalido)
        if not 0 <= porcentaje_desc <= 100:
            raise CalculoInvalido("Descuento: debe estar entre 0 y 100.")
        if not 0 <= porcentaje_imp <= 100:
            raise CalculoInvalido("Impuesto: debe estar entre 0 y 100.")
        try:
            subtotal = self.tarifa_hora * horas
            descontado = subtotal * (Decimal("100") - porcentaje_desc) / Decimal("100")
            total = descontado * (Decimal("100") + porcentaje_imp) / Decimal("100")
            return total.quantize(CENTAVO, rounding=ROUND_HALF_UP)
        except (InvalidOperation, OverflowError) as exc:
            raise CalculoInvalido("No se pudo calcular el importe del servicio.") from exc


class Sala(Servicio):
    """Servicio de alquiler de sala (hasta 24 horas por reserva)."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: object, capacidad: int) -> None:
        super().__init__(codigo, nombre, tarifa_hora)
        if type(capacidad) is not int or not 1 <= capacidad <= 100:
            raise ErrorValidacion("Capacidad de sala: entero entre 1 y 100.")
        self.__capacidad = capacidad

    def validar_parametros(self, horas: int) -> None:
        self._validar_horas(horas, 24)

    def calcular_costo(self, horas: int, *, descuento: object = 0, impuesto: object = 0) -> Decimal:
        return super().calcular_costo(horas, descuento=descuento, impuesto=impuesto)

    def describir(self) -> str:
        return f"Sala {self.identificador}: {self.nombre}, capacidad {self.__capacidad}"


class Equipo(Servicio):
    """Servicio de alquiler de equipo (hasta 168 horas por reserva)."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: object, categoria: str) -> None:
        super().__init__(codigo, nombre, tarifa_hora)
        self.__categoria = _texto_no_vacio(categoria, "Categoría de equipo")

    def validar_parametros(self, horas: int) -> None:
        self._validar_horas(horas, 168)

    def calcular_costo(self, horas: int, *, descuento: object = 0, impuesto: object = 0) -> Decimal:
        return super().calcular_costo(horas, descuento=descuento, impuesto=impuesto)

    def describir(self) -> str:
        return f"Equipo {self.identificador}: {self.nombre}, tipo {self.__categoria}"


class Asesoria(Servicio):
    """Servicio de asesoría especializada (hasta 8 horas por reserva)."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: object, especialidad: str) -> None:
        super().__init__(codigo, nombre, tarifa_hora)
        self.__especialidad = _texto_no_vacio(especialidad, "Especialidad de asesoría")

    def validar_parametros(self, horas: int) -> None:
        self._validar_horas(horas, 8)

    def calcular_costo(self, horas: int, *, descuento: object = 0, impuesto: object = 0) -> Decimal:
        return super().calcular_costo(horas, descuento=descuento, impuesto=impuesto)

    def describir(self) -> str:
        return f"Asesoría {self.identificador}: {self.nombre}, área {self.__especialidad}"
