"""Pruebas de clientes, servicios, reservas, excepciones y registros."""
import logging
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from software_fj.entidades import Cliente, Entidad
from software_fj.excepciones import (
    CalculoInvalido, ErrorValidacion, EstadoReservaInvalido,
    RegistroDuplicado, RegistroNoEncontrado, ReservaInvalida,
    ServicioNoDisponible,
)
from software_fj.gestor import GestorSoftwareFJ
from software_fj.registro import configurar_registro
from software_fj.servicios import Asesoria, Equipo, Sala, Servicio


class PruebasSoftwareFJ(unittest.TestCase):
    """Usa un directorio de logs aislado para cada prueba."""

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / 'logs'
        self.logger = configurar_registro(self.ruta)
        self.gestor = GestorSoftwareFJ(self.logger)
        self.gestor.registrar_cliente('10000001', 'Ana Ruiz', 'ana@example.com', '3001234567')
        self.gestor.registrar_cliente('10000002', 'Luis Mora', 'luis@example.com', '3001234568')
        self.gestor.registrar_sala('S001', 'Sala de juntas', 50000, 12)
        self.gestor.registrar_equipo('E001', 'Portátil', 30000, 'Cómputo')
        self.gestor.registrar_asesoria('A001', 'Soporte', 80000, 'Redes')

    def tearDown(self):
        # finally asegura cierre del recurso incluso si falla un manejador.
        try:
            for manejador in self.logger.handlers[:]:
                self.logger.removeHandler(manejador)
                manejador.close()
        finally:
            self.temporal.cleanup()

    def test_clases_abstractas_no_son_instanciables(self):
        with self.assertRaises(TypeError):
            Entidad('1')
        with self.assertRaises(TypeError):
            Servicio('S002', 'Abstracto', 100)

    def test_cliente_valido_y_encapsulado(self):
        cliente = self.gestor.clientes[0]
        self.assertEqual(cliente.nombre, 'Ana Ruiz')
        self.assertFalse(hasattr(cliente, '__correo'))
        self.assertEqual(cliente.correo, 'ana@example.com')

    def test_cliente_rechaza_correo_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente('10000009', 'Ana Ruiz', 'sin-arroba', '3001234567')

    def test_cliente_rechaza_documento_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente('ABC', 'Ana Ruiz', 'ana@example.com', '3001234567')

    def test_cliente_rechaza_telefono_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente('10000009', 'Ana Ruiz', 'ana@example.com', 'x')

    def test_cliente_rechaza_nombre_invalido(self):
        with self.assertRaises(ErrorValidacion):
            Cliente('10000009', 'A', 'ana@example.com', '3001234567')

    def test_cambio_correo_valido(self):
        cliente = self.gestor.clientes[0]
        cliente.cambiar_correo('NUEVO@EXAMPLE.COM')
        self.assertEqual(cliente.correo, 'nuevo@example.com')

    def test_registro_duplicado(self):
        with self.assertRaises(RegistroDuplicado):
            self.gestor.registrar_cliente('10000001', 'Otro Nombre', 'otro@example.com', '3001234567')

    def test_servicio_duplicado(self):
        with self.assertRaises(RegistroDuplicado):
            self.gestor.registrar_sala('S001', 'Otra sala', 30000, 3)

    def test_parametros_invalidos_en_servicio(self):
        with self.assertRaises(ErrorValidacion):
            self.gestor.registrar_sala('S002', 'Sala', 1000, 0)
        with self.assertRaises(ErrorValidacion):
            self.gestor.registrar_equipo('E002', 'Portátil', -1, 'Cómputo')
        with self.assertRaises(ErrorValidacion):
            self.gestor.registrar_asesoria('A002', 'Soporte', 80000, '')

    def test_servicios_polimorficos(self):
        descripciones = [servicio.describir() for servicio in self.gestor.servicios]
        self.assertTrue(descripciones[0].startswith('Sala'))
        self.assertTrue(descripciones[1].startswith('Equipo'))
        self.assertTrue(descripciones[2].startswith('Asesoría'))
        self.assertTrue(all(isinstance(s, Servicio) for s in self.gestor.servicios))

    def test_calculo_normal(self):
        sala = self.gestor.servicios[0]
        self.assertEqual(sala.calcular_costo(2), Decimal('100000.00'))

    def test_calculo_descuento_e_impuesto(self):
        sala = self.gestor.servicios[0]
        self.assertEqual(sala.calcular_costo(2, descuento=10, impuesto=19), Decimal('107100.00'))

    def test_descuento_fuera_de_rango(self):
        with self.assertRaises(CalculoInvalido):
            self.gestor.servicios[0].calcular_costo(2, descuento=101)

    def test_impuesto_fuera_de_rango(self):
        with self.assertRaises(CalculoInvalido):
            self.gestor.servicios[0].calcular_costo(2, impuesto=-2)

    def test_cadena_de_excepcion_decimal(self):
        with self.assertRaises(CalculoInvalido) as contexto:
            self.gestor.servicios[0].calcular_costo(2, descuento='abc')
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_rechaza_horas_invalidas(self):
        with self.assertRaises(ReservaInvalida):
            self.gestor.crear_reserva('10000001', 'A001', 9)
        with self.assertRaises(ReservaInvalida):
            self.gestor.crear_reserva('10000001', 'E001', True)

    def test_rechaza_cliente_inexistente(self):
        with self.assertRaises(RegistroNoEncontrado) as contexto:
            self.gestor.crear_reserva('00000000', 'S001', 2)
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_rechaza_servicio_inexistente(self):
        with self.assertRaises(RegistroNoEncontrado):
            self.gestor.crear_reserva('10000001', 'X000', 2)

    def test_confirmar_reserva(self):
        reserva = self.gestor.crear_reserva('10000001', 'S001', 2)
        confirmada = self.gestor.confirmar_reserva(reserva.numero)
        self.assertEqual(confirmada.estado, 'confirmada')
        self.assertEqual(confirmada.total, Decimal('100000.00'))

    def test_bloqueo_de_servicio_confirmado(self):
        r1 = self.gestor.crear_reserva('10000001', 'S001', 2)
        r2 = self.gestor.crear_reserva('10000002', 'S001', 3)
        self.gestor.confirmar_reserva(r1.numero)
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.confirmar_reserva(r2.numero)

    def test_liberar_servicio_tras_cancelacion(self):
        r1 = self.gestor.crear_reserva('10000001', 'S001', 2)
        r2 = self.gestor.crear_reserva('10000002', 'S001', 3)
        self.gestor.confirmar_reserva(r1.numero)
        self.gestor.cancelar_reserva(r1.numero)
        self.gestor.confirmar_reserva(r2.numero)
        self.assertEqual(r2.estado, 'confirmada')

    def test_procesar_reserva(self):
        r = self.gestor.crear_reserva('10000001', 'A001', 1)
        self.gestor.confirmar_reserva(r.numero)
        self.gestor.procesar_reserva(r.numero)
        self.assertEqual(r.estado, 'procesada')

    def test_rechaza_procesamiento_dos_veces(self):
        r = self.gestor.crear_reserva('10000001', 'S001', 2)
        self.gestor.confirmar_reserva(r.numero)
        self.gestor.procesar_reserva(r.numero)
        with self.assertRaises(EstadoReservaInvalido):
            self.gestor.procesar_reserva(r.numero)

    def test_rechaza_cancelacion_de_procesada(self):
        r = self.gestor.crear_reserva('10000001', 'S001', 2)
        self.gestor.confirmar_reserva(r.numero)
        self.gestor.procesar_reserva(r.numero)
        with self.assertRaises(EstadoReservaInvalido):
            self.gestor.cancelar_reserva(r.numero)

    def test_servicio_deshabilitado(self):
        self.gestor.establecer_disponibilidad('S001', False)
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.crear_reserva('10000001', 'S001', 2)

    def test_no_deshabilitar_servicio_ocupado(self):
        r = self.gestor.crear_reserva('10000001', 'S001', 2)
        self.gestor.confirmar_reserva(r.numero)
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.establecer_disponibilidad('S001', False)

    def test_log_registra_exito_y_error(self):
        with self.assertRaises(RegistroDuplicado):
            self.gestor.registrar_cliente('10000001', 'Ana Ruiz', 'ana@example.com', '3001234567')
        for manejador in self.logger.handlers:
            manejador.flush()
        texto = (self.ruta / 'eventos.log').read_text(encoding='utf-8')
        self.assertIn('Operación completada', texto)
        self.assertIn('registrar_cliente rechazado', texto)

    def test_no_persiste_clientes_ni_reservas(self):
        otro = GestorSoftwareFJ(self.logger)
        self.assertEqual(len(otro.clientes), 0)
        self.assertEqual(len(otro.reservas), 0)

    def test_efecto_de_confirmacion_fallida_no_altera_estado(self):
        r = self.gestor.crear_reserva('10000001', 'S001', 2)
        with self.assertRaises(CalculoInvalido):
            self.gestor.confirmar_reserva(r.numero, descuento=300)
        self.assertEqual(r.estado, 'creada')
        self.gestor.confirmar_reserva(r.numero)
        self.assertEqual(r.estado, 'confirmada')


if __name__ == '__main__':
    unittest.main()
