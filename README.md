# Sistema-Integral-de-Gesti-n-de-Clientes-Servicios-y-Reservas
sistema integral orientado a objetos 
Primera parte, importaciones, excepciones y clases cliente. 

"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación - Fase 4
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging

# Configuración del archivo de registros
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Excepciones personalizadas

class ErrorSistema(Exception):
    pass

class DatosInvalidosError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaError(ErrorSistema):
    pass

class OperacionNoPermitidaError(ErrorSistema):
    pass


# Clase abstracta general

class Entidad(ABC):

    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatosInvalidosError(
                "El identificador es obligatorio."
            )

        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        pass


# Clase Cliente

class Cliente(Entidad):

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not isinstance(nombre, str) or len(nombre.strip()) < 2:
            raise DatosInvalidosError(
                "El nombre debe tener al menos 2 caracteres."
            )

        if not isinstance(correo, str) or "@" not in correo or "." not in correo:
            raise DatosInvalidosError(
                "El correo electrónico no tiene un formato válido."
            )

        if not str(telefono).isdigit() or len(str(telefono)) < 7:
            raise DatosInvalidosError(
                "El teléfono debe contener mínimo 7 números."
            )

        self.__nombre = nombre.strip()
        self.__correo = correo.strip().lower()
        self.__telefono = str(telefono)

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | "
            f"ID: {self.identificador} | "
            f"Correo: {self.__correo} | "
            f"Teléfono: {self.__telefono}"
        )
