#-*- coding: utf-8 -*-
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import healpy as hp
from astropy.io import fits
from astropy import wcs
from reproject import reproject_from_healpix, reproject_to_healpix
from matplotlib.backends.backend_agg import FigureCanvasAgg
import plotly
import plotly.graph_objs as go

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import Context

from my_app.models import Pointing
from .forms import PointingForm

def code(request):
    return redirect("https://github.com/antoinemarchal")


def references(request):
    return redirect("http://adsabs.harvard.edu")


def home(request):
    date = datetime.now()

    return render(request, 'my_app/myhome.html', locals())


def about(request):
    date = datetime.now()

    return render(request, 'my_app/about.html', locals())


def query(request):
    date = datetime.now()

    form = PointingForm(request.POST or None)
    if form.is_valid():
        lon = form.cleaned_data['lon']
        lat = form.cleaned_data['lat']
        size = form.cleaned_data['size']

        map, map_wnm, map_cnm = get_images_url(lon, lat, size)
        spectrum = get_spectrum()
        
    return render(request, 'my_app/query.html', locals())
#______________________________________________________________________________________________________________________________________
def set_wcs(patch_size, projx, projy, cdelt, GLON, GLAT):
    w           = wcs.WCS(naxis=2)
    w.wcs.crpix = [patch_size/2, patch_size/2]
    w.wcs.crval = [GLON, GLAT]
    w.wcs.cdelt = np.array([-cdelt,cdelt])
    w.wcs.ctype = [projx, projy]
    return w

def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])
        
    return pl_colorscale


def get_images_url(lon, lat, size):
    cm = plt.get_cmap('inferno')
    cm.set_bad(color='black')
    imkw = dict(origin='lower', interpolation='none', cmap=cm)

    inferno_cmap = matplotlib.cm.get_cmap('inferno')
    viridis_cmap = matplotlib.cm.get_cmap('viridis')
    
    viridis_rgb = []
    inferno_rgb = []
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)
    
    for i in range(0, 255):
        k = matplotlib.colors.colorConverter.to_rgb(inferno_cmap(norm(i)))
        inferno_rgb.append(k)
        
    for i in range(0, 255):
        k = matplotlib.colors.colorConverter.to_rgb(viridis_cmap(norm(i)))
        viridis_rgb.append(k)
        
    inferno = matplotlib_to_plotly(inferno_cmap, 255)
    viridis = matplotlib_to_plotly(viridis_cmap, 255)

    map = hp.read_map("my_app/static/my_app/data/LFI_SkyMap_030-BPassCorrected-field-IQU_0256_R2.01_full.fits")
    map_cnm = hp.read_map("my_app/static/my_app/data/LFI_SkyMap_044-BPassCorrected-field-IQU_0256_R2.01_full.fits")
    map_wnm = hp.read_map("my_app/static/my_app/data/LFI_SkyMap_070-BPassCorrected-field-IQU_0256_R2.01_full.fits")

    size = int(size)

    target_wcs = set_wcs(size, 'GLON-TAN', 'GLAT-TAN', 0.0833333333, lon, lat)
    target_header = target_wcs.to_header()    

    array, foo = reproject_from_healpix((map,'g'), target_header, shape_out=(size,size))
    array_wnm, foo = reproject_from_healpix((map_wnm,'g'), target_header, shape_out=(size,size))
    array_cnm, foo = reproject_from_healpix((map_cnm,'g'), target_header, shape_out=(size,size))
    
    layout = go.Layout(
        width=540,
        height=540,
        xaxis=dict(
            title='XAXIS',
            titlefont=dict(
                family='Arial, sans-serif',
                size=18,
                color='lightgrey'
                ),
            showticklabels=True,
            tickangle=45,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=14,
                color='black'
                ),
            exponentformat='e',
            showexponent='All'
            ),
        
        yaxis=dict(
            title='YAXIS',
            titlefont=dict(
                family='Arial, sans-serif',
                size=18,
                color='lightgrey'
                ),
            showticklabels=True,
            tickangle=45,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=14,
                color='black'
                ),
            exponentformat='e',
            showexponent='All'
            )
        )
    #__________________________________________
    trace = go.Heatmap(z=array, colorscale=inferno)
    data=[trace]
    fig = {
        'data': data,
        'layout': layout,
        }
    plot = plotly.offline.plot(fig, filename='fig', auto_open=False, output_type="div")
    #__________________________________________
    trace_wnm = go.Heatmap(z=array_wnm, colorscale=inferno)
    data_wnm=[trace_wnm]
    fig_wnm = {
        'data': data_wnm,
        'layout': layout,
        }
    plot_wnm = plotly.offline.plot(fig_wnm, filename='fig_wnm', auto_open=False, output_type="div")
    #__________________________________________
    trace_cnm = go.Heatmap(z=array_cnm, colorscale=inferno)

    data_cnm=[trace_cnm]
    fig_cnm = {
        'data': data_cnm,
        'layout': layout,
        }
    plot_cnm = plotly.offline.plot(fig_cnm, filename='fig_cnm', auto_open=False, output_type="div")

    return plot, plot_wnm, plot_cnm


def get_spectrum():
    trace = []

    trace.append(
        go.Scatter(
            x = np.arange(100),
            y = np.random.randn(100),
            mode = 'lines',
            name = 'TOT', 
            line = dict(
                color = ('rgba(67,67,67,1)'),
                width = 2,
                )
            )
        )

    data = trace
            
    layout = dict(title = "MY PLOT",
                  xaxis = dict(title = 'x label'),
                  yaxis = dict(title = 'y label'),
                  showlegend=False,
                  width=1200,
                  height=650,
                  )
    
    fig = dict(data=data, layout=layout)
    plot = plotly.offline.plot(fig, filename='styled-line', auto_open=False, output_type="div")
    
    return plot
