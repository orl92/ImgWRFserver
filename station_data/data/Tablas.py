class Tablas:
    def __init__(self):
        self.__iW = {
            "0": "(m/s)",
            "1": "(m/s)",
            "2": "(nudos)",
            "3": "(nudos)",
        }

        self.__iR = {
            "0": "Incluido en seccion 1 y 2",
            "1": "Incluido seccion 1",
            "2": "Incluido seccion 2",
            "3": "Omitido (La cantidad de precipitación = 0)",
            "4": "Omitido (No se dispone de datos de precipitación)",
        }

        self.__iX = {
            "1": "Dotada de personal, Incluido",
            "2": "Dotada de personal, Omitido (nada importante)",
            "3": "Dotada de personal, Omitido (ninguna observación, datos no disponibles)",
            "4": "Automático, Incluido",
            "5": "Automático, Omitido (ningún fenómeno importante por señalar)",
            "6": "Automático, Omitido (ninguna observación, datos no disponibles)",
        }

        self.__h = {
            "0": "0 - 49",
            "1": "50 - 99",
            "2": "100 - 199",
            "3": "200 - 299",
            "4": "300 - 599",
            "5": "600 - 999",
            "6": "1000 - 1499",
            "7": "1500 - 1999",
            "8": "2000 - 2499",
            "9": "2500 o más o no hay nubes"
        }

        self.__VV = {
            "00": 0.0, "01": 0.1, "02": 0.2, "03": 0.3, "04": 0.4, "05": 0.5, "06": 0.6, "07": 0.7,
            "08": 0.8, "09": 0.9, "10": 1, "11": 1.1, "12": 1.2, "13": 1.3, "14": 1.4, "15": 1.5, "16": 1.6, "17": 1.7,
            "18": 1.8, "19": 1.9, "20": 2, "21": 2.1, "22": 2.2, "23": 2.3, "24": 2.4, "25": 2.5, "26": 2.6, "27": 2.7,
            "28": 2.8, "29": 2.9, "30": 3, "31": 3.1, "32": 3.2, "33": 3.3, "34": 3.4, "35": 3.5, "36": 3.6, "37": 3.7,
            "38": 3.8, "39": 3.9, "40": 4, "41": 4.1, "42": 4.2, "43": 4.3, "44": 4.4, "45": 4.5, "46": 4.6, "47": 4.7,
            "48": 4.8, "49": 4.9, "50": 3., "56": 6, "57": 7, "58": 8, "59": 9, "60": 10, "61": 11, "62": 12, "63": 13,
            "64": 14, "65": 15, "66": 16, "67": 17, "68": 18, "69": 19, "70": 20, "71": 21, "72": 22, "73": 23,
            "74": 24, "75": 25, "76": 26, "77": 27, "78": 28, "79": 29, "80": 30, "81": 35, "82": 40, "83": 45,
            "84": 50, "85": 55, "86": 60, "87": 65, "88": 70, "89": "> 70",
        }

        self.__dd = {
            "00": "calma", "01": "N", "02": "NNE", "03": "NE", "04": "ENE", "05": "E", "06": "NE ¼ E", "07": "ENE",
            "08": "E ¼ NE", "09": "E", "10": "E ¼ SE", "11": "ESE", "12": "SE ¼ E", "13": "SE", "14": "SE",
            "15": "SE ¼ S", "16": "SSE", "17": "S ¼ SE", "18": "S", "19": "S ¼ SW", "20": "SSW", "21": "SW ¼ S",
            "22": "SW", "23": "SW", "24": "SW ¼ S", "25": "WSW", "26": "W ¼ SW", "27": "W", "28": "W ¼ NW", "29": "WNW",
            "30": "NW ¼ W", "31": "NW", "32": "NW", "33": "NW ¼ N", "34": "NNW", "35": "N ¼ NW", "36": "N",
            "99": "Variable",
        }

        self.__dd2 = {
            "00":None, "01": 0, "02": 25, "03": 45, "04": 65, "05": 90, "06": 60, "07": 70,
            "08": 80, "09": 90, "10": 100, "11": 110, "12": 120, "13": 130, "14": 140, "15": 150,
            "16": 160, "17": 170, "18": 180, "19": 190, "20": 200, "21": 210, "22": 220, "23": 230,
            "24": 240, "25": 250, "26": 260, "27": 270, "28": 280, "29": 290,"30": 300, "31": 310,
            "32": 320, "33": 330, "34": 340, "35": 350, "36": 360, "99": None
        }

        self.__ww = {
            "00": "Cielo despejado",
            "01": "Cielo parcialmente nublado",
            "02": "Cielo cubierto",
            "03": "Polvo en suspensión, visibilidad reducida",
            "04": "Humo, visibilidad reducida",
            "05": "Calima",
            "06": "Polvo en suspensión, no levantado por el viento",
            "07": "Polvo o arena levantados por el viento",
            "08": "Torbellino de polvo o arena",
            "09": "Tormenta de polvo o arena",
            "10": "Calima",
            "11": "Bancos de niebla",
            "12": "Niebla continua",
            "13": "Relámpagos visibles",
            "14": "Precipitación no llegando al suelo",
            "15": "Precipitación a distancia",
            "16": "Precipitación cerca, pero no en la estación",
            "17": "Truenos, pero sin precipitación en la estación",
            "18": "Ráfagas fuertes",
            "19": "Tromba marina",
            "20": "Llovizna (no helada)",
            "21": "Lluvia (no helada)",
            "22": "Nieve",
            "23": "Lluvia y nieve",
            "24": "Llovizna helada",
            "25": "Chubascos de lluvia",
            "26": "Chubascos de nieve",
            "27": "Chubascos de granizo",
            "28": "Niebla",
            "29": "Tormenta",
            "30": "Tormenta de polvo o arena ligera",
            "31": "Tormenta de polvo o arena moderada",
            "32": "Tormenta de polvo o arena fuerte",
            "33": "Tormenta de polvo o arena violenta",
            "34": "Tormenta de polvo o arena muy fuerte",
            "35": "Lluvia congelada ligera",
            "36": "Lluvia congelada moderada o fuerte",
            "37": "Copos de nieve grandes",
            "38": "Copos de nieve pequeños",
            "39": "Niebla con cristales de hielo",
            "40": "Niebla a distancia",
            "41": "Niebla en bancos",
            "42": "Niebla, cielo visible",
            "43": "Niebla, cielo no visible",
            "44": "Niebla, cielo visible",
            "45": "Niebla, cielo no visible",
            "46": "Niebla, cielo visible",
            "47": "Niebla, cielo no visible",
            "48": "Niebla con escarcha, cielo visible",
            "49": "Niebla con escarcha, cielo no visible",
            "50": "Llovizna ligera discontinua",
            "51": "Llovizna ligera continua",
            "52": "Llovizna moderada discontinua",
            "53": "Llovizna moderada continua",
            "54": "Llovizna fuerte discontinua",
            "55": "Llovizna fuerte continua",
            "56": "Llovizna helada ligera",
            "57": "Llovizna helada moderada o fuerte",
            "58": "Llovizna y lluvia ligera",
            "59": "Llovizna y lluvia moderada o fuerte",
            "60": "Lluvia ligera discontinua",
            "61": "Lluvia ligera continua",
            "62": "Lluvia moderada discontinua",
            "63": "Lluvia moderada continua",
            "64": "Lluvia fuerte discontinua",
            "65": "Lluvia fuerte continua",
            "66": "Lluvia helada ligera",
            "67": "Lluvia helada moderada o fuerte",
            "68": "Lluvia o llovizna con nieve ligera",
            "69": "Lluvia o llovizna con nieve moderada o fuerte",
            "70": "Nieve ligera discontinua",
            "71": "Nieve ligera continua",
            "72": "Nieve moderada discontinua",
            "73": "Nieve moderada continua",
            "74": "Nieve fuerte discontinua",
            "75": "Nieve fuerte continua",
            "76": "Diamantes de hielo (prismas)",
            "77": "Granos de nieve",
            "78": "Copos de nieve aislados",
            "79": "Granizo",
            "80": "Chubascos de lluvia ligeros",
            "81": "Chubascos de lluvia moderados o fuertes",
            "82": "Chubascos de lluvia violentos",
            "83": "Chubascos de lluvia y nieve ligeros",
            "84": "Chubascos de lluvia y nieve moderados o fuertes",
            "85": "Chubascos de nieve ligeros",
            "86": "Chubascos de nieve moderados o fuertes",
            "87": "Chubascos de granizo ligeros",
            "88": "Chubascos de granizo moderados o fuertes",
            "89": "Chubascos de granizo violentos",
            "90": "Tormenta ligera",
            "91": "Tormenta moderada o fuerte",
            "92": "Tormenta violenta",
            "93": "Tormenta con granizo ligera",
            "94": "Tormenta con granizo moderada o fuerte",
            "95": "Tormenta con granizo violenta",
            "96": "Tormenta con granizo y nieve ligera",
            "97": "Tormenta con granizo y nieve moderada o fuerte",
            "98": "Tormenta con polvo o arena",
            "99": "Tormenta violenta con granizo",
        }

        self.__W1 = {
            "0": "Nubes cubriendo la mitad del cielo o menos durante todo el periodo",
            "1": "Nubes cubriendo más de la mitad del cielo durante parte del periodo y cubriendo la mitad del cielo o menos durante parte del periodo",
            "2": "Nubes cubriendo más de la mitad del cielo durante todo el periodo",
            "3": "Tormenta de arena, polvo o nieve",
            "4": "Niebla o humo",
            "5": "Llovizna",
            "6": "Lluvia",
            "7": "Nieve o aguanieve",
            "8": "Chubascos",
            "9": "Tormentas",
        }

        self.__W2 = {
            "0": "Sin nubes en todo el periodo",
            "1": "Nubes cubriendo la mitad del cielo o menos durante todo el periodo",
            "2": "Nubes cubriendo más de la mitad del cielo durante parte del periodo y cubriendo la mitad del cielo o menos durante parte del periodo",
            "3": "Nubes cubriendo más de la mitad del cielo durante todo el periodo",
            "4": "Niebla o humo",
            "5": "Llovizna",
            "6": "Lluvia",
            "7": "Nieve o aguanieve",
            "8": "Chubascos",
            "9": "Tormentas",
        }

    @property
    def dd(self):
        return self.__dd
    
    @property
    def dd2(self):
        return self.__dd2

    @property
    def iW(self):
        return self.__iW

    @property
    def ww(self):
        return self.__ww

    @property
    def W1(self):
        return self.__W1

    @property
    def W2(self):
        return self.__W2

    @property
    def VV(self):
        return self.__VV