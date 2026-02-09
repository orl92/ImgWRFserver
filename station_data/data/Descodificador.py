# station_data/data/Descodificador.py
from datetime import date, datetime, time, timedelta, timezone

from dateutil import tz
import numpy as np

from station_data.data.FM12 import FM12
from station_data.data.Tablas import Tablas


class Descodificador:
    def __init__(self, obs):
        self.__obs = obs
        self.__fm12 = FM12()
        self.funcion()

    @property
    def obs(self):
        return self.__obs

    @property
    def sesion1(self):
        return self.obs.get('sesion1')

    @property
    def sesion2(self):
        return self.obs.get('sesion2')

    @property
    def fm12(self):
        return self.__fm12

    def funcion(self):
        if not self.sesion1:
            return

        # Parsear la sesión 1
        parts = self.sesion1.split()

        if not parts:
            return

        # El primer elemento es IIiii (estación)
        station_code = parts[0]
        if len(station_code) >= 5:
            self.fm12.II = station_code[:2]
            self.fm12.iii = station_code[2:5]
        elif len(station_code) >= 2:
            self.fm12.II = station_code[:2]
            self.fm12.iii = station_code[2:] if len(station_code) > 2 else "000"

        # Índice para recorrer las partes
        idx = 1

        # iR iX h VV (grupo IrIxixhVV)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5:
                self.fm12.iR = group[0]
                self.fm12.iX = group[1]
                self.fm12.h = group[2]
                self.fm12.VV = group[3:5]
            idx += 1

        # N ddff (grupo Nddff)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5:
                self.fm12.N = group[0]
                self.fm12.dd = group[1:3]
                self.fm12.ff = group[3:5]
            idx += 1

        # 1SnTTT (Temperatura)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5 and group[0] == '1':
                self.fm12._1Sn = group[1]
                self.fm12.TTT = group[2:5]
            idx += 1

        # 2SnTdTdTd (Temperatura punto de rocío)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5 and group[0] == '2':
                self.fm12._2Sn = group[1]
                self.fm12.TdTdTd = group[2:5]
            idx += 1

        # 3PPPP (Presión estación)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5 and group[0] == '3':
                self.fm12._3PPPP = group[1:5]
            idx += 1

        # 4PPPP (Presión nivel del mar)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5 and group[0] == '4':
                self.fm12._4PPPP = group[1:5]
            idx += 1

        # 5appp (Tendencia barométrica)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 4 and group[0] == '5':
                self.fm12._5a = group[1]
                self.fm12.ppp = group[2:5]
            idx += 1

        # 6RRRtR (Precipitación)
        if idx < len(parts):
            group = parts[idx]
            if len(group) >= 5 and group[0] == '6':
                self.fm12._6RRR = group[1:4]
                self.fm12.tR = group[4] if len(group) > 4 else None
            idx += 1

        # 7wwW1W2 (Tiempo presente y pasado)
        # if idx < len(parts):
        for i in range(len(parts[3:])):
            group = parts[3:][i]
            if len(group) >= 5 and group[0] == '7':
                self.fm12._7WW = group[1:3]
                if len(group) >= 5:
                    self.fm12.W1 = group[3]
                    self.fm12.W2 = group[4]
                break

        # 8NhCLCMCH (Nubes)
        # if idx <= len(parts):
        group = parts[-1]
        if len(group) >= 5 and group[0] == '8':
            self.fm12._8Nh = group[1]
            self.fm12.CL = group[2] if len(group) > 2 else None
            self.fm12.CM = group[3] if len(group) > 3 else None
            self.fm12.CH = group[4] if len(group) > 4 else None

        # Parsear la sesión 2 si existe
        if self.sesion2:
            parts2 = self.sesion2.split()

            for i, group in enumerate(parts2):
                # Temperatura máxima (grupo 1SnTxTxTx)
                if len(group) >= 5 and group[:2] == '10':
                    self.fm12._1Sn_Tx = group[1]
                    self.fm12.TxTxTx = group[2:]

                # Temperatura mínima (grupo 2SnTnTnTn)
                elif len(group) >= 4 and group[:2] == '20':
                    self.fm12._2Sn_Tn = group[1]
                    self.fm12.TnTnTn = group[2:]

                # Precipitación 24h (grupo 7R24R24R24R24)
                elif len(group) >= 5 and group[0] == '7' and group[1:].isdigit() and len(group[1:]) == 4:
                    self.fm12._7R24R24R24R24 = group[1:]

    # Humedad relativa
    def get_rh(self):
        try:
            temp = self.get_temp()
            td = self.get_td()

            if temp is None or td is None:
                return None

            # Fórmula de Magnus para humedad relativa
            es = 6.112 * np.exp((17.67 * temp) / (temp + 243.5))
            e = 6.112 * np.exp((17.67 * td) / (td + 243.5))
            rh = 100 * (e / es)
            return int(round(rh))
        except Exception:
            return None

    # Número de la estación
    def get_estacion(self):
        try:
            return int(f'{self.fm12.II}{self.fm12.iii}')
        except Exception:
            return None

    # Horario de la observación
    def get_horario(self):
        try:
            day = int(self.obs.get('day', datetime.utcnow().day))
            hour_obs = int(self.obs.get('hour', 0))

            now = datetime.utcnow()
            h = datetime(year=now.year, month=now.month, day=day, hour=hour_obs)
            h = h.replace(tzinfo=tz.tzutc())
            return h.strftime('%I:%M %p')
        except Exception:
            # Si falla, usar hora actual
            now = datetime.utcnow()
            now = now.replace(tzinfo=tz.tzutc())
            return now.strftime('%I:%M %p')

    # Día de la observación
    def get_dia(self):
        try:
            day = int(self.obs.get('day', datetime.utcnow().day))
            hour_obs = int(self.obs.get('hour', 0))

            now = datetime.utcnow()
            d = datetime(year=now.year, month=now.month, day=day, hour=hour_obs)
            d = d.replace(tzinfo=tz.tzutc())
            return d.astimezone(tz.gettz('America/Havana')).strftime('%d/%m/%Y')
        except Exception:
            # Si falla, usar fecha actual
            now = datetime.utcnow()
            now = now.replace(tzinfo=tz.tzutc())
            return now.astimezone(tz.gettz('America/Havana')).strftime('%d/%m/%Y')

    # Temperatura
    def get_temp(self):
        try:
            if self.fm12._1Sn == '0':
                return int(self.fm12.TTT) / 10
            elif self.fm12._1Sn == '1':
                return (int(self.fm12.TTT) / 10) * -1
            else:
                return None
        except Exception:
            return None

    # Temperatura de punto de rocío
    def get_td(self):
        try:
            if self.fm12._2Sn == '0':
                return int(self.fm12.TdTdTd) / 10
            elif self.fm12._2Sn == '1':
                return (int(self.fm12.TdTdTd) / 10) * -1
            else:
                return None
        except Exception:
            return None

    # Direccion del viento
    def get_ddViento(self):
        try:
            return Tablas().dd.get(self.fm12.dd, None)
        except Exception:
            return None

    def get_ddViento2(self):
        try:
            return Tablas().dd2.get(self.fm12.dd, None)
        except Exception:
            return None

    # Velicidad del viento
    def get_ffViento(self):
        try:
            return self.fm12.ff
        except Exception:
            return None

    # Precipitación en la observación
    def get_precipitacion(self):
        try:
            if not self.fm12._6RRR:
                return 0.0

            if self.fm12._6RRR == '990':
                return 0.1  # Traza

            # Si comienza con '99', es decimal
            if self.fm12._6RRR.startswith('99'):
                return float(self.fm12._6RRR[2]) / 10
            else:
                return float(self.fm12._6RRR) / 10
        except Exception:
            return 0.0

    # Temperatura Maxima
    def get_tempTx(self):
        try:
            if not self.fm12.TxTxTx or self.fm12.TxTxTx == '--':
                return None

            if self.fm12._1Sn_Tx == '0':
                return float(self.fm12.TxTxTx) / 10
            elif self.fm12._1Sn_Tx == '1':
                return (float(self.fm12.TxTxTx) / 10) * -1
            else:
                return None
        except Exception:
            return None

    # Temperatura Minima
    def get_tempTn(self):
        try:
            if not self.fm12.TnTnTn or self.fm12.TnTnTn == '--':
                return None

            if self.fm12._2Sn_Tn == '0':
                return float(self.fm12.TnTnTn) / 10
            elif self.fm12._2Sn_Tn == '1':
                return (float(self.fm12.TnTnTn) / 10) * -1
            else:
                return None
        except Exception:
            return None

    # Lluvia en 24h
    def get_precipitacion24(self):
        try:
            if not self.fm12._7R24R24R24R24:
                return 0.0

            if self.fm12._7R24R24R24R24 == '9999':
                return 0.1  # Traza

            return float(self.fm12._7R24R24R24R24) / 10
        except Exception:
            return 0.0

    # Total de cielo cubierto
    def get_estado_cielo(self):
        try:
            nh = self.fm12._8Nh

            if nh == '0':
                return 'Despejado'
            if nh in ['1', '2', '3']:
                return 'Poco nublado'
            if nh in ['4', '5']:
                return 'Parcialmente nublado'
            if nh in ['6', '7', '8']:
                return 'Nublado'
            if nh == '/':
                return 'No observado'

            return None
        except Exception:
            return None

    def get_cielo_cubierto(self):
        try:
            if self.fm12._8Nh and self.fm12._8Nh != '/':
                return int(self.fm12._8Nh)
            return None
        except Exception:
            return None

    # Tiempo presente (ww)
    def get_ww(self):
        """Devuelve el código ww (tiempo presente)"""
        try:
            return self.fm12._7WW
        except Exception:
            return None

    def get_ww_descripcion(self):
        """Devuelve la descripción del tiempo presente"""
        try:
            ww_code = self.get_ww()
            if ww_code:
                return Tablas().ww.get(ww_code, "Código desconocido")
            return None
        except Exception:
            return None

    # Tiempo pasado 1 (W1)
    def get_W1(self):
        """Devuelve el código W1 (tiempo pasado 1 - última hora)"""
        try:
            return self.fm12.W1
        except Exception:
            return None

    def get_W1_descripcion(self):
        """Devuelve la descripción del tiempo pasado 1"""
        try:
            w1_code = self.get_W1()
            if w1_code:
                return Tablas().W1.get(w1_code, "Código desconocido")
            return None
        except Exception:
            return None

    # Tiempo pasado 2 (W2)
    def get_W2(self):
        """Devuelve el código W2 (tiempo pasado 2 - últimas 6 horas)"""
        try:
            return self.fm12.W2
        except Exception:
            return None

    def get_W2_descripcion(self):
        """Devuelve la descripción del tiempo pasado 2"""
        try:
            w2_code = self.get_W2()
            if w2_code:
                return Tablas().W2.get(w2_code, "Código desconocido")
            return None
        except Exception:
            return None

    # Método combinado para obtener todos los datos de tiempo
    def get_tiempo_completo(self):
        """Devuelve todos los datos de tiempo en un diccionario"""
        return {
            'tiempo_presente_codigo': self.get_ww(),
            'tiempo_presente_descripcion': self.get_ww_descripcion(),
            'tiempo_pasado1_codigo': self.get_W1(),
            'tiempo_pasado1_descripcion': self.get_W1_descripcion(),
            'tiempo_pasado2_codigo': self.get_W2(),
            'tiempo_pasado2_descripcion': self.get_W2_descripcion(),
        }

    # Visibilidad
    def get_visibilidad_codigo(self):
        """Devuelve el código de visibilidad (VV)"""
        try:
            return self.fm12.VV
        except Exception:
            return None

    def get_visibilidad_km(self):
        """Devuelve la visibilidad en kilómetros"""
        try:
            vv_code = self.get_visibilidad_codigo()
            if vv_code:
                tablas = Tablas()
                valor = tablas.VV.get(vv_code)

                # Manejar casos especiales
                if valor == "> 55":
                    return 55.1  # Valor por encima de 55 km
                elif isinstance(valor, (int, float)):
                    return float(valor)
                else:
                    # Si es string como "> 70", extraer número
                    if isinstance(valor, str) and valor.startswith('>'):
                        try:
                            return float(valor.replace('>', '').strip()) + 0.1
                        except:
                            return None
            return None
        except Exception:
            return None

    def get_visibilidad_descripcion(self):
        """Devuelve una descripción cualitativa de la visibilidad"""
        try:
            visibilidad = self.get_visibilidad_km()
            if visibilidad is None:
                return "No disponible"

            if visibilidad < 0.1:
                return "Muy mala (< 0.1 km)"
            elif visibilidad < 1.0:
                return f"Mala ({visibilidad:.1f} km)"
            elif visibilidad < 4.0:
                return f"Moderada ({visibilidad:.1f} km)"
            elif visibilidad < 10.0:
                return f"Buena ({visibilidad:.1f} km)"
            elif visibilidad < 20.0:
                return f"Muy buena ({visibilidad:.1f} km)"
            else:
                return f"Excelente ({visibilidad:.1f} km)"
        except Exception:
            return "No disponible"