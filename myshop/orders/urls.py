#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: urls.py
#
# Descripción:
#   En este archivo se definen las urls de la app de las órdenes.
#
#   Cada url debe tener la siguiente estructura:
#
#   path( url, vista, nombre_url )
#
#-------------------------------------------------------------------------

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('list/', views.OrderList.as_view(),name='order_list'),
    path('cancel/<int:id>',views.cancel_order, name='cancel_order'),
    path('delete/<int:id>',views.delete_order,name='delete_order'),
    path('delete_item/<int:id>',views.delete_item,name='delete_item'),
]
