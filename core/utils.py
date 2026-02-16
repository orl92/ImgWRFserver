from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static

# Mapa de códigos meteorológicos a nombres base de archivos
TIEMPO_IMG_BASE_MAP = {
    'PN': 'poco_nublado',
    'PARCN': 'parcialmente_nublado',
    'N': 'nublado',
    'AIS CHUB': 'aislados_chubascos',
    'ALG CHUB': 'algunos_chubascos',
    'NUM CHUB': 'numerosos_chubascos',
    'ALG TORM': 'algunas_tormentas',
    'NUM TORM': 'numerosas_tormentas',
}

# Códigos que usan la misma imagen para todos los períodos
CODIGOS_SIN_VARIACION = ['N', 'ALG TORM', 'NUM TORM', 'ALG CHUB', 'NUM CHUB']

# Sufijos para cada período
PERIOD_SUFFIXES = {
    'morning': 'm',
    'afternoon': 'a',
    'night': 'n'
}

def get_img_path(weather_code, period='afternoon'):
    """
    Obtiene la ruta de la imagen según el código meteorológico y el período del día.
    Para códigos sin variación, usa siempre la imagen base.
    Para códigos con variación, usa el sufijo del período.
    """
    if weather_code not in TIEMPO_IMG_BASE_MAP:
        return ''  # O una imagen por defecto si prefieres

    base_name = TIEMPO_IMG_BASE_MAP[weather_code]

    if weather_code in CODIGOS_SIN_VARIACION:
        file_path = f'dist/img/weather_icon/{base_name}.png'
    else:
        suffix = PERIOD_SUFFIXES.get(period, 'a')
        file_path = f'dist/img/weather_icon/{base_name}_{suffix}.png'

    return static(file_path)

# Funciones para la luna
def get_moon_img_path(moon_phase):
    MOON_IMG_MAP = {
        'Luna Nueva': 'dist/img/moon_faces/new_moon.png',
        'Creciente': 'dist/img/moon_faces/waning_crescent_moon.png',
        'Cuarto Creciente': 'dist/img/moon_faces/first_quarter_moon.png',
        'Gibosa Creciente': 'dist/img/moon_faces/waning_gibbous_moon.png',
        'Luna Llena': 'dist/img/moon_faces/full_moon.png',
        'Gibosa Menguante': 'dist/img/moon_faces/waxing_gibbous_moon.png',
        'Cuarto Menguante': 'dist/img/moon_faces/last_quarter_moon.png',
        'Menguante': 'dist/img/moon_faces/waxing_crescent_moon.png',
    }
    file_path = MOON_IMG_MAP.get(moon_phase)
    return static(file_path) if file_path else ''

# Funciones para el sol
def get_sun_img_path(sun_event):
    SUN_IMG_MAP = {
        'sunrise': 'dist/img/sun/sunrise.png',
        'sunset': 'dist/img/sun/sunset.png',
    }
    file_path = SUN_IMG_MAP.get(sun_event)
    return static(file_path) if file_path else ''

def log_action(user, obj, action_flag, message=""):
    """
    Registra una acción en el log de administración de Django.
    """
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message,
    )
