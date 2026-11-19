from abc import ABC, abstractmethod
from pathlib import Path
import logging

"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación - Fase 4

El programa permite registrar clientes, administrar servicios y crear,
confirmar, cancelar y procesar reservas. También valida los datos y guarda
los eventos y errores en un archivo de registro.
"""

# El archivo de registro queda en la misma carpeta de este programa.
RUTA_REGISTRO = Path(__file__).with_name("software_fj.log")

logging.basicConfig(
    filename=str(RUTA_REGISTRO),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# EXCEPCIONES PERSONALIZADAS

class ErrorSistema(Exception):
    """Excepción general del sistema."""
    pass


class DatosInvalidosError(ErrorSistema):
    pass


class ServicioNoDisponibleError(ErrorSistema):
    pass


class ReservaError(ErrorSistema):
    pass


class OperacionNoPermitidaError(ErrorSistema):
    pass


# CLASE ABSTRACTA GENERAL

class Entidad(ABC):

    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatosInvalidosError("El identificador es obligatorio.")

        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        pass


# CLASE CLIENTE

class Cliente(Entidad):

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not isinstance(nombre, str) or len(nombre.strip()) < 2:
            raise DatosInvalidosError(
                "El nombre debe tener al menos 2 caracteres."
            )

        if (
            not isinstance(correo, str)
            or correo.count("@") != 1
            or "." not in correo.split("@")[-1]
            or correo.startswith("@")
            or correo.endswith("@")
        ):
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


# CLASE ABSTRACTA SERVICIO

class Servicio(Entidad, ABC):

    def __init__(self, identificador, nombre, tarifa_base):
        super().__init__(identificador)

        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del servicio es obligatorio."
            )

        if (
            isinstance(tarifa_base, bool)
            or not isinstance(tarifa_base, (int, float))
            or tarifa_base <= 0
        ):
            raise DatosInvalidosError(
                "La tarifa debe ser mayor que cero."
            )

        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise DatosInvalidosError(
                "La disponibilidad debe ser True o False."
            )

        self._disponible = estado
        logging.info(
            "Disponibilidad del servicio %s cambiada a %s.",
            self.identificador,
            estado
        )

    # El método permite calcular el costo normal o incluir descuento e
    # impuesto mediante parámetros opcionales.
    def calcular_costo(self, duracion, descuento=0, impuesto=0):

        if (
            isinstance(duracion, bool)
            or not isinstance(duracion, (int, float))
            or duracion <= 0
        ):
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        if not 0 <= descuento <= 100:
            raise DatosInvalidosError(
                "El descuento debe estar entre 0 y 100."
            )

        if not 0 <= impuesto <= 100:
            raise DatosInvalidosError(
                "El impuesto debe estar entre 0 y 100."
            )

        subtotal = self._tarifa_base * duracion
        valor_descuento = subtotal * (descuento / 100)
        subtotal_con_descuento = subtotal - valor_descuento
        total = subtotal_con_descuento * (1 + impuesto / 100)

        return round(total, 2)

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    def mostrar_informacion(self):
        estado = "Disponible" if self._disponible else "No disponible"

        return (
            f"{self._nombre} | "
            f"ID: {self.identificador} | "
            f"Tarifa base: ${self._tarifa_base:,.2f} | "
            f"{estado}"
        )


# SERVICIO DE RESERVA DE SALAS

class ReservaSala(Servicio):

    def __init__(self, identificador, tarifa_hora, capacidad):
        super().__init__(
            identificador,
            "Reserva de sala",
            tarifa_hora
        )

        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise DatosInvalidosError(
                "La capacidad debe ser un entero positivo."
            )

        self.capacidad = capacidad

    def validar_parametros(self, duracion):
        if duracion > 12:
            raise DatosInvalidosError(
                "La sala no se puede reservar por más de 12 horas."
            )
        return True

    def describir_servicio(self):
        return (
            f"Sala para reuniones con capacidad "
            f"para {self.capacidad} personas."
        )


# SERVICIO DE ALQUILER DE EQUIPOS

class AlquilerEquipo(Servicio):

    def __init__(self, identificador, tarifa_dia, tipo_equipo):
        super().__init__(
            identificador,
            "Alquiler de equipos",
            tarifa_dia
        )

        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise DatosInvalidosError(
                "Debe indicar el tipo de equipo."
            )

        self.tipo_equipo = tipo_equipo.strip()

    def validar_parametros(self, duracion):
        if duracion > 30:
            raise DatosInvalidosError(
                "El alquiler no puede superar 30 días."
            )
        return True

    def describir_servicio(self):
        return f"Alquiler de equipo: {self.tipo_equipo}."


# SERVICIO DE ASESORÍAS ESPECIALIZADAS

class Asesoria(Servicio):

    def __init__(self, identificador, tarifa_hora, especialidad):
        super().__init__(
            identificador,
            "Asesoría especializada",
            tarifa_hora
        )

        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatosInvalidosError(
                "Debe indicar la especialidad."
            )

        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion):
        if duracion > 8:
            raise DatosInvalidosError(
                "La asesoría no puede superar 8 horas."
            )
        return True

    def describir_servicio(self):
        return f"Asesoría profesional en {self.especialidad}."


# CLASE RESERVA

class Reserva(Entidad):

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError(
                "La reserva debe tener un cliente válido."
            )

        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError(
                "La reserva debe tener un servicio válido."
            )

        servicio.validar_parametros(duracion)

        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio seleccionado no está disponible."
            )

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.costo = servicio.calcular_costo(duracion)

    def confirmar(self):
        if self.estado != "Pendiente":
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio dejó de estar disponible."
            )

        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        if self.estado == "Cancelada":
            error = OperacionNoPermitidaError(
                "La reserva ya está cancelada."
            )
            logging.error(
                "No se pudo cancelar la reserva %s: %s",
                self.identificador,
                error
            )
            raise error

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self):
        try:
            if self.estado != "Confirmada":
                raise ReservaError(
                    "La reserva debe estar confirmada para procesarse."
                )

            logging.info(
                "Reserva %s procesada correctamente.",
                self.identificador
            )

            return (
                f"Reserva {self.identificador} procesada. "
                f"Total: ${self.costo:,.2f}"
            )

        except ReservaError as error:
            logging.error(
                "No se pudo procesar la reserva %s: %s",
                self.identificador,
                error
            )
            raise

        finally:
            logging.info(
                "Finalizó el intento de procesamiento de la reserva %s.",
                self.identificador
            )

    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificador} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} | "
            f"Estado: {self.estado} | "
            f"Total: ${self.costo:,.2f}"
        )


# SISTEMA PRINCIPAL SOFTWARE FJ

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        try:
            if not isinstance(cliente, Cliente):
                raise DatosInvalidosError(
                    "El dato recibido no corresponde a un cliente."
                )

            if any(
                c.identificador == cliente.identificador
                for c in self.clientes
            ):
                raise DatosInvalidosError(
                    "Ya existe un cliente con ese identificador."
                )

            self.clientes.append(cliente)
            logging.info(
                "Cliente registrado: %s",
                cliente.identificador
            )
            print("Cliente registrado correctamente.")
            return True

        except ErrorSistema as error:
            logging.error("Error al registrar cliente: %s", error)
            print(f"No se pudo registrar el cliente: {error}")
            return False

    def registrar_servicio(self, servicio):
        try:
            if not isinstance(servicio, Servicio):
                raise DatosInvalidosError(
                    "El objeto recibido no es un servicio válido."
                )

            if any(
                s.identificador == servicio.identificador
                for s in self.servicios
            ):
                raise DatosInvalidosError(
                    "Ya existe un servicio con ese identificador."
                )

            self.servicios.append(servicio)
            logging.info(
                "Servicio registrado: %s",
                servicio.identificador
            )
            print("Servicio registrado correctamente.")
            return True

        except ErrorSistema as error:
            logging.error("Error al registrar servicio: %s", error)
            print(f"No se pudo registrar el servicio: {error}")
            return False

    def crear_reserva(self, identificador, cliente, servicio, duracion):
        try:
            # Primero se revisa el identificador para evitar crear
            # una reserva que ya existe.
            if any(
                r.identificador == identificador
                for r in self.reservas
            ):
                raise ReservaError(
                    "Ya existe una reserva con ese identificador."
                )

            reserva = Reserva(
                identificador,
                cliente,
                servicio,
                duracion
            )

            self.reservas.append(reserva)
            logging.info("Reserva %s creada.", identificador)
            print("Reserva creada correctamente.")
            return reserva

        except ErrorSistema as error:
            logging.error(
                "Error al crear reserva %s: %s",
                identificador,
                error
            )
            print(f"No se pudo crear la reserva: {error}")
            return None

        except Exception as error:
            logging.exception(
                "Error inesperado al crear una reserva."
            )
            raise ReservaError(
                "Ocurrió un error inesperado al crear la reserva."
            ) from error

    def listar_clientes(self):
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def listar_servicios(self):
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())
            print(servicio.describir_servicio())

    def listar_reservas(self):
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# PRUEBAS DE FUNCIONAMIENTO DEL SISTEMA

def ejecutar_pruebas():

    sistema = SistemaSoftwareFJ()

    print("\n========== SISTEMA SOFTWARE FJ ==========\n")

    # Prueba 1: registrar un cliente válido.
    cliente1 = Cliente(
        "C001",
        "Laura Gómez",
        "laura@gmail.com",
        "3001234567"
    )
    sistema.registrar_cliente(cliente1)

    # Prueba 2: registrar otro cliente válido.
    cliente2 = Cliente(
        "C002",
        "Carlos Pérez",
        "carlos@gmail.com",
        "3107654321"
    )
    sistema.registrar_cliente(cliente2)

    # Prueba 3: intentar registrar un cliente con correo inválido.
    try:
        cliente_invalido = Cliente(
            "C003",
            "Ana Ruiz",
            "correo-invalido",
            "3001112233"
        )
        sistema.registrar_cliente(cliente_invalido)

    except DatosInvalidosError as error:
        logging.error("Registro inválido de cliente: %s", error)
        print(f"Error controlado de cliente: {error}")

    # Prueba 4: registrar una sala.
    sala = ReservaSala("S001", 50000, 12)
    sistema.registrar_servicio(sala)

    # Prueba 5: registrar un equipo.
    equipo = AlquilerEquipo("E001", 80000, "Video beam")
    sistema.registrar_servicio(equipo)

    # Prueba 6: registrar una asesoría.
    asesoria = Asesoria(
        "A001",
        60000,
        "desarrollo de software"
    )
    sistema.registrar_servicio(asesoria)

    # Prueba 7: intentar crear un servicio con tarifa negativa.
    try:
        servicio_invalido = ReservaSala("S002", -10000, 10)
        sistema.registrar_servicio(servicio_invalido)

    except DatosInvalidosError as error:
        logging.error("Creación inválida de servicio: %s", error)
        print(f"Error controlado de servicio: {error}")

    # Prueba 8: intentar crear una reserva con duración cero.
    sistema.crear_reserva("R005", cliente1, equipo, 0)

    # Prueba 9: crear una reserva correcta.
    reserva1 = sistema.crear_reserva(
        "R001",
        cliente1,
        sala,
        2
    )

    # Prueba 10: confirmar y procesar la reserva.
    if reserva1:
        try:
            reserva1.confirmar()
            print(reserva1.procesar())
        except ErrorSistema as error:
            print(f"No se pudo procesar: {error}")

    # Prueba 11: intentar repetir el identificador R001.
    sistema.crear_reserva("R001", cliente2, equipo, 1)

    # Prueba 12: crear una reserva para alquiler de equipo.
    reserva2 = sistema.crear_reserva(
        "R002",
        cliente2,
        equipo,
        3
    )

    # Prueba 13: intentar una asesoría que supera el límite de horas.
    sistema.crear_reserva(
        "R003",
        cliente1,
        asesoria,
        15
    )

    # Prueba 14: intentar reservar un servicio no disponible.
    sala.cambiar_disponibilidad(False)
    sistema.crear_reserva(
        "R004",
        cliente2,
        sala,
        1
    )

    # Prueba 15: cancelar una reserva.
    if reserva2:
        try:
            reserva2.cancelar()
            print("La reserva R002 fue cancelada.")
        except ErrorSistema as error:
            logging.error("Error al cancelar reserva: %s", error)
            print(f"No se pudo cancelar: {error}")

    # Prueba 16: intentar procesar una reserva cancelada.
    if reserva2:
        try:
            print(reserva2.procesar())
        except ReservaError as error:
            print(f"Procesamiento controlado: {error}")

    # Prueba 17: calcular un costo con descuento e impuesto.
    try:
        total_especial = equipo.calcular_costo(
            2,
            descuento=10,
            impuesto=19
        )
        print(
            f"Costo de 2 días con descuento e impuesto: "
            f"${total_especial:,.2f}"
        )
    except DatosInvalidosError as error:
        print(f"Error en el cálculo: {error}")

    # Ejemplo de try, except, else y finally.
    try:
        duracion_prueba = 2

        if duracion_prueba <= 0:
            raise DatosInvalidosError(
                "La duración debe ser positiva."
            )

    except DatosInvalidosError as error:
        logging.error("Validación de duración: %s", error)

    else:
        print("Validación adicional: la duración es correcta.")

    finally:
        print("Finalizó la validación adicional.")

    # Mostrar los resultados de las pruebas.
    print("\n========== CLIENTES REGISTRADOS ==========")
    sistema.listar_clientes()

    print("\n========== SERVICIOS REGISTRADOS ==========")
    sistema.listar_servicios()

    print("\n========== RESERVAS REGISTRADAS ==========")
    sistema.listar_reservas()

    print("\nEl programa terminó correctamente.")
    print(
        "Los eventos y errores quedaron registrados "
        f"en el archivo: {RUTA_REGISTRO}"
    )


if __name__ == "__main__":
    ejecutar_pruebas()
