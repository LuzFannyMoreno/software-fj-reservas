"""Entidad abstracta y cliente con datos privados y validaciones."""
from abc import ABC, abstractmethod
import re

from .excepciones import ErrorValidacion


def _texto_no_vacio(valor: object, campo: str) -> str:
    """Comprueba que el valor sea una cadena con contenido."""
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(f"{campo} es obligatorio y debe ser texto.")
    return valor.strip()


class Entidad(ABC):
    """Entidad general con identificador inmutable y descripción abstracta."""

    def __init__(self, identificador: str) -> None:
        self._identificador = _texto_no_vacio(identificador, "Identificador")

    @property
    def identificador(self) -> str:
        """Devuelve el identificador de la entidad."""
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        """Construye una representación legible de la entidad."""


class Cliente(Entidad):
    """Cliente con acceso controlado a sus datos personales."""

    def __init__(self, documento: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(documento)
        if not re.fullmatch(r"\d{6,12}", self.identificador):
            raise ErrorValidacion("Documento: deben ser entre 6 y 12 dígitos.")
        self.__nombre = self._validar_nombre(nombre)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    @staticmethod
    def _validar_nombre(valor: str) -> str:
        nombre = _texto_no_vacio(valor, "Nombre")
        if len(nombre) < 3 or not all(c.isalpha() or c in " '-" for c in nombre):
            raise ErrorValidacion("Nombre: use al menos 3 caracteres alfabéticos.")
        return nombre

    @staticmethod
    def _validar_correo(valor: str) -> str:
        correo = _texto_no_vacio(valor, "Correo").lower()
        if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", correo):
            raise ErrorValidacion("Correo electrónico no válido.")
        return correo

    @staticmethod
    def _validar_telefono(valor: str) -> str:
        telefono = _texto_no_vacio(valor, "Teléfono")
        if not re.fullmatch(r"\+?\d{7,15}", telefono):
            raise ErrorValidacion("Teléfono: entre 7 y 15 dígitos; + opcional.")
        return telefono

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def cambiar_correo(self, nuevo_correo: str) -> None:
        """Cambia el correo después de validarlo."""
        self.__correo = self._validar_correo(nuevo_correo)

    def describir(self) -> str:
        """No expone teléfono ni correo en los listados generales."""
        return f"Cliente {self.identificador}: {self.nombre}"
