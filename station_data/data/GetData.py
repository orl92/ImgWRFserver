# station_data/data/GetData.py
from station_data.data.Descodificador import Descodificador
from station_data.data.OpenFileObs import OpenFileObs
from datetime import datetime


class GetData:
    def __init__(self):
        self.__numbers_stations = [78350, 78351, 78352, 78353, 78354, 78355]

    @property
    def _numbers_stations(self):
        return self.__numbers_stations

    def get_station(self, hour: str, station_number: int):
        try:
            # Crear objeto OpenFileObs
            open_obs = OpenFileObs(station_number, hour)

            # Obtener datos de la estación
            obs_data = open_obs.station()

            # Verificar si tenemos datos válidos
            if not obs_data.get('sesion1'):
                return {
                    'estacion': station_number,
                    'status': 'error',
                    'message': 'No hay sesión1 en los datos',
                    'data': None
                }

            # Crear decodificador
            d = Descodificador(obs_data)

            # Obtener día de la observación
            dia_str = d.get_dia()
            if not dia_str:
                return {
                    'estacion': station_number,
                    'status': 'error',
                    'message': 'No se pudo obtener fecha',
                    'data': None
                }

            # Verificar que el día sea correcto (primeros 2 dígitos)
            try:
                day_obs = int(dia_str.split('/')[0])
                day_now = datetime.utcnow().day

                # Permitir diferencia de ±1 día por diferencias de zona horaria
                if abs(day_obs - day_now) <= 1:
                    # Extraer todos los datos
                    estacion = int(d.get_estacion() or station_number)
                    temperatura = d.get_temp()
                    temp_max = d.get_tempTx()
                    temp_min = d.get_tempTn()
                    humedad = d.get_rh()
                    viento_vel = d.get_ffViento()
                    viento_dir = d.get_ddViento()
                    dd = d.get_ddViento2()
                    precip_3h = d.get_precipitacion()
                    precip_24h = d.get_precipitacion24()
                    cielo_estado = d.get_estado_cielo()
                    cielo_cubierto = d.get_cielo_cubierto()

                    # Obtener datos de tiempo
                    tiempo_completo = d.get_tiempo_completo()

                    # Obtener datos adicionales
                    punto_rocio = d.get_td()
                    presion_estacion = self._get_presion_estacion(d)
                    presion_nivel_mar = self._get_presion_nivel_mar(d)
                    visibilidad_km = d.get_visibilidad_km()
                    visibilidad_codigo = d.get_visibilidad_codigo()
                    visibilidad_descripcion = d.get_visibilidad_descripcion()

                    # Calcular velocidad del viento en km/h
                    velocidad_viento_kmh = None
                    if viento_vel:
                        try:
                            velocidad_viento_kmh = float(viento_vel) * 3.6
                        except (ValueError, TypeError):
                            velocidad_viento_kmh = None

                    return {
                        'estacion': estacion,
                        'dia': dia_str,
                        'hora': d.get_horario(),
                        'estado del cielo': cielo_estado,
                        'cielo cubierto': cielo_cubierto,
                        'temperatura': temperatura,
                        'temperatura maxima': temp_max,
                        'temperatura minima': temp_min,
                        'punto_rocio': punto_rocio,
                        'humedad relativa': humedad,
                        'velocidad del viento': velocidad_viento_kmh,
                        'direccion del viento': viento_dir,
                        'dd': dd,
                        'precipitacion en 3 horas': precip_3h,
                        'precipitacion en 24 horas': precip_24h,
                        'presion_estacion': presion_estacion,
                        'presion_nivel_mar': presion_nivel_mar,
                        'visibilidad_codigo': visibilidad_codigo,
                        'visibilidad_km': visibilidad_km,
                        'visibilidad_descripcion': visibilidad_descripcion,

                        # Nuevos campos de tiempo
                        'tiempo_presente_codigo': tiempo_completo.get('tiempo_presente_codigo'),
                        'tiempo_presente_descripcion': tiempo_completo.get('tiempo_presente_descripcion'),
                        'tiempo_pasado1_codigo': tiempo_completo.get('tiempo_pasado1_codigo'),
                        'tiempo_pasado1_descripcion': tiempo_completo.get('tiempo_pasado1_descripcion'),
                        'tiempo_pasado2_codigo': tiempo_completo.get('tiempo_pasado2_codigo'),
                        'tiempo_pasado2_descripcion': tiempo_completo.get('tiempo_pasado2_descripcion'),

                        'status': 'success',
                        'message': 'Datos obtenidos correctamente',
                        'raw_data': obs_data
                    }
                else:
                    return {
                        'estacion': station_number,
                        'status': 'error',
                        'message': f'Día no coincide ({day_obs} vs {day_now})',
                        'data': None
                    }

            except Exception as e:
                return {
                    'estacion': station_number,
                    'status': 'error',
                    'message': f'Error en validación de fecha: {e}',
                    'data': None
                }

        except Exception as e:
            return {
                'estacion': station_number,
                'status': 'error',
                'message': str(e),
                'data': None
            }

    def _get_presion_estacion(self, decodificador):
        """Obtener presión a nivel de estación"""
        try:
            # 3PPPP en décimas de hPa, omitiendo el dígito del millar
            if hasattr(decodificador.fm12, '_3PPPP') and decodificador.fm12._3PPPP:
                presion = float(decodificador.fm12._3PPPP) / 10
                # Ajustar si el valor es menor que 1000 (se omite el dígito del millar)
                if presion < 500:
                    presion += 1000
                return presion
        except:
            pass
        return None

    def _get_presion_nivel_mar(self, decodificador):
        """Obtener presión a nivel del mar"""
        try:
            # 4PPPP en décimas de hPa, omitiendo el dígito del millar
            if hasattr(decodificador.fm12, '_4PPPP') and decodificador.fm12._4PPPP:
                presion = float(decodificador.fm12._4PPPP) / 10
                # Ajustar si el valor es menor que 1000 (se omite el dígito del millar)
                if presion < 500:
                    presion += 1000
                return presion
        except:
            pass
        return None

    def get_all_stations(self, hour):
        _dict = {}

        for i in self._numbers_stations:
            _dict[f'{i}'] = self.get_station(hour, i)
        return _dict