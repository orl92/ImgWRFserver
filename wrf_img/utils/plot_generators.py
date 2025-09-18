import numpy as np
import matplotlib
import requests
import io
from datetime import datetime
from django.utils import timezone
import re

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from django.conf import settings
from django.core.files.base import ContentFile
from wrf_img.models import Simulation, MeteoImage
from .plot_config import get_plot_config


import numpy as np
import matplotlib
import requests
import io
import os
from datetime import datetime
from django.utils import timezone
import re

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from django.conf import settings
from django.core.files.base import ContentFile
from wrf_img.models import Simulation, MeteoImage
from .plot_config import get_plot_config


def generate_and_save_meteo_plot(datetime_init, var_name):
    # URL de la API
    api_url = f'https://modelo.cmw.insmet.cu/api/data/?datetime_init={datetime_init}&var_name={var_name}'

    try:
        # Hacer la solicitud a la API
        response = requests.get(api_url, timeout=30, verify=False)
        response.raise_for_status()

        data = response.json()

        # Convertir los datos a arrays de numpy
        lats = np.array(data['lats'])
        longs = np.array(data['longs'])
        times = data['times']
        var_data = np.array(data['var'])

        # Para variables de viento
        u_data = np.array(data['U10']) if 'U10' in data else None
        v_data = np.array(data['V10']) if 'V10' in data else None

        plot_config = get_plot_config(var_name)
        saved_images = []

        # Convertir la cadena a objeto datetime
        datetime_obj = datetime.strptime(datetime_init, '%Y%m%d%H')
        datetime_obj = timezone.make_aware(datetime_obj)

        # Crear o obtener la simulación
        simulation, created = Simulation.objects.get_or_create(
            initial_datetime=datetime_obj,
            defaults={'description': f'Simulación generada automáticamente el {timezone.now()}'}
        )

        for i in range(len(times)):
            fig, ax = setup_figure(lats, longs, var_name)
            contour, barbs, contour_lines = draw_plot(
                ax, var_name, plot_config,
                lats, longs, var_data, times, i,
                u_data, v_data
            )
            cbar = setup_colorbar(fig, ax, contour, plot_config, var_name)

            # Convertir el tiempo válido a formato datetime
            time_str = times[i]
            if 'T' in time_str:
                valid_dt_naive = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
            else:
                valid_dt_naive = datetime.strptime(time_str, '%Y%m%d%H')

            valid_dt = timezone.make_aware(valid_dt_naive)

            # Calcular la hora de pronóstico
            forecast_hour = (valid_dt - simulation.initial_datetime).total_seconds() / 3600

            # Formatear la fecha inicial
            initial_dt_str = simulation.initial_datetime.strftime('%Y-%m-%d %H:%M UTC')

            # Configurar ejes
            setup_axes(ax, plot_config, time_str, initial_dt_str, forecast_hour)

            # Guardar imagen en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            plt.close(fig)

            # Crear nombre de archivo
            safe_time = times[i].replace(':', '-').replace(' ', '_')
            filename = f"{var_name}_{safe_time}.png"

            # Verificar si ya existe una imagen
            existing_image = MeteoImage.objects.filter(
                simulation=simulation,
                valid_datetime=valid_dt,
                variable_name=var_name
            ).first()

            # Calcular estadísticas
            data_min = float(np.min(var_data[i]))
            data_max = float(np.max(var_data[i]))
            data_mean = float(np.mean(var_data[i]))

            if existing_image:
                # Actualizar imagen existente
                meteo_image = existing_image
                meteo_image.data_min = data_min
                meteo_image.data_max = data_max
                meteo_image.data_mean = data_mean
            else:
                # Crear nueva imagen
                meteo_image = MeteoImage(
                    simulation=simulation,
                    valid_datetime=valid_dt,
                    variable_name=var_name,
                    data_min=data_min,
                    data_max=data_max,
                    data_mean=data_mean
                )

            # Guardar imagen
            buffer.seek(0)
            meteo_image.image.save(filename, ContentFile(buffer.getvalue()), save=False)
            meteo_image.save()

            saved_images.append(meteo_image)

        return saved_images

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al acceder a la API: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


def setup_figure(lats, longs, var_name=None):
    fig = plt.figure(figsize=(12, 8), frameon=False)

    # Configurar fondo negro para variables de nubosidad
    if var_name in ['clflo', 'clfmi', 'clfhi']:
        fig.patch.set_facecolor('black')
        plt.rcParams['savefig.facecolor'] = 'black'
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['text.color'] = 'black'  # Texto en negro
        plt.rcParams['axes.labelcolor'] = 'black'  # Etiquetas en negro
        plt.rcParams['xtick.color'] = 'black'  # Ticks en negro
        plt.rcParams['ytick.color'] = 'black'  # Ticks en negro

    ax = plt.axes(projection=ccrs.PlateCarree())

    # Configurar fondo del eje para variables de nubosidad
    if var_name in ['clflo', 'clfmi', 'clfhi']:
        ax.set_facecolor('white')  # Fondo del mapa en blanco para contraste

    # Ajustar extensión del mapa al área de los datos
    ax.set_extent([
        np.min(longs), np.max(longs),
        np.min(lats), np.max(lats)
    ], crs=ccrs.PlateCarree())

    # Configuración del mapa
    resolution = '10m'
    ax.add_feature(cfeature.LAND.with_scale(resolution), facecolor='#f5f5f5')
    ax.add_feature(cfeature.OCEAN.with_scale(resolution), facecolor='#c8e4ff')
    ax.add_feature(cfeature.COASTLINE.with_scale(resolution), linewidth=0.8)
    ax.add_feature(cfeature.BORDERS.with_scale(resolution), linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale(resolution), linewidth=0.3, edgecolor='gray')

    plt.tight_layout(pad=0)
    fig.subplots_adjust(left=0.05, right=0.9, bottom=0.05, top=0.95)

    return fig, ax


def draw_plot(ax, var_name, plot_config, lats, longs, var_data, times, frame_idx, u_data=None, v_data=None):
    levels = plot_config.get('levels', 20)
    current_contour = None
    current_barbs = None
    current_contour_lines = None

    # Caso especial para precipitación (RAINC y RAINC3H)
    if var_name in ['RAINC', 'RAINC3H']:
        from matplotlib.colors import BoundaryNorm, ListedColormap
        cmap_custom = ListedColormap(plot_config['colors'])
        norm = BoundaryNorm(plot_config['levels'], cmap_custom.N)

        current_contour = ax.contourf(
            longs, lats, var_data[frame_idx],
            levels=plot_config['levels'],
            cmap=cmap_custom,
            norm=norm,
            extend=plot_config['extend'],
            transform=ccrs.PlateCarree()
        )

    # Caso especial para dirección del viento (wd10)
    elif var_name == 'wd10':
        current_contour = ax.contourf(
            longs, lats, var_data[frame_idx],
            cmap=plot_config['cmap'],
            levels=plot_config['levels'],
            extend=plot_config.get('extend', 'neither'),
            transform=ccrs.PlateCarree()
        )

        step = 2
        current_barbs = ax.barbs(
            longs[::step, ::step], lats[::step, ::step],
            u_data[frame_idx][::step, ::step],
            v_data[frame_idx][::step, ::step],
            length=6,
            barb_increments={'half': 2, 'full': 4, 'flag': 20},
            color=plot_config.get('barb_color'),
            transform=ccrs.PlateCarree()
        )

    # Caso para nubosidad (convertir a porcentaje)
    elif var_name in ['clflo', 'clfmi', 'clfhi']:
        current_contour = ax.contourf(
            longs, lats, var_data[frame_idx] * 100,
            levels=levels,
            cmap=plot_config['cmap'],
            vmin=plot_config.get('vmin'),
            vmax=plot_config.get('vmax'),
            extend=plot_config.get('extend', 'neither'),
            transform=ccrs.PlateCarree()
        )

    # Para todas las demás variables
    else:
        current_contour = ax.contourf(
            longs, lats, var_data[frame_idx],
            levels=levels,
            cmap=plot_config['cmap'],
            vmin=plot_config.get('vmin'),
            vmax=plot_config.get('vmax'),
            extend=plot_config.get('extend', 'neither'),
            transform=ccrs.PlateCarree()
        )

    # Añadir líneas de contorno para slp y PSFC
    if var_name in ['slp', 'PSFC']:
        current_contour_lines = ax.contour(
            longs, lats, var_data[frame_idx],
            levels=np.arange(950, 1051, 2),
            colors='black',
            linewidths=0.5,
            transform=ccrs.PlateCarree()
        )
        ax.clabel(current_contour_lines, inline=True, fontsize=8, fmt='%1.0f hPa')

    return current_contour, current_barbs, current_contour_lines


def setup_colorbar(fig, ax, contour, plot_config, var_name):
    # Configurar colorbar para nubosidad
    if var_name in ['clflo', 'clfmi', 'clfhi']:
        cbar = fig.colorbar(
            contour, ax=ax,
            orientation='vertical',
            pad=0.02, aspect=25, shrink=0.80
        )
        cbar.ax.yaxis.set_tick_params(color='black')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='black')
        cbar.outline.set_edgecolor('black')
        cbar.set_label(plot_config['units'], rotation=0, labelpad=15,
                       fontsize=9, weight='bold', color='black')
    else:
        cbar = fig.colorbar(
            contour, ax=ax,
            orientation='vertical',
            pad=0.02, aspect=25, shrink=0.80
        )
        cbar.set_label(plot_config['units'], rotation=0, labelpad=15,
                       fontsize=9, weight='bold')

    cbar.set_label(plot_config['units'], rotation=0, labelpad=15, fontsize=9, weight='bold')

    # Configuración especial para RAINC y RAINC3H
    if var_name in ['RAINC', 'RAINC3H']:
        cbar.set_ticks(plot_config['levels'])
        tick_labels = [f"{x:.1f}" if x < 1 else f"{int(x)}" for x in plot_config['levels']]
        cbar.set_ticklabels(tick_labels)
        cbar.ax.axhline(y=0.1, color='gray', linestyle='--', linewidth=0.5)

        # Configuración para nubosidad
    if var_name in ['clflo', 'clfmi', 'clfhi']:
        cbar.set_ticks(plot_config['levels'])
        cbar.set_ticklabels(plot_config['tick_labels'])

    # Configuración especial para dirección del viento (wd10)
    elif var_name == 'wd10':
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        ticks = plot_config['levels']
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(directions)

    # Configuración para otras variables con niveles definidos
    elif isinstance(plot_config.get('levels'), (list, np.ndarray)):
        cbar.set_ticks(plot_config['levels'])
        cbar.set_ticklabels([f"{x:.1f}" if isinstance(x, float) else f"{x}" for x in plot_config['levels']])

    return cbar


def setup_axes(ax, plot_config, time_str, initial_dt_str, forecast_hour):
    ax.set_xlabel('Longitud', fontsize=9, labelpad=8)
    ax.set_ylabel('Latitud', fontsize=9, labelpad=8)

    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}

    # Crear título con información completa
    title = (f"{plot_config['label']} | Inicial: {initial_dt_str} | Hora de simulsción: +{forecast_hour}h | Válido: {time_str}")

    ax.set_title(title, pad=12, fontsize=11)
