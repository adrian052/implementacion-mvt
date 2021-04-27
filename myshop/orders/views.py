#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------
# Archivo: views.py
#
# Descripción:
#   En este archivo se definen las vistas para la app de órdenes.
#
#   A continuación se describen los métodos que se implementaron en este archivo:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Verifica la infor- |
#           |                        |  - request: datos de     |    mación y crea la   |
#           |    order_create()      |    la solicitud.         |    orden de compra a  |
#           |                        |                          |    partir de los datos|
#           |                        |                          |    del cliente y del  |
#           |                        |                          |    carrito.           |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Crea y envía el    |
#           |        send()          |  - order_id: id del      |    correo electrónico |
#           |                        |    la orden creada.      |    para notificar la  |
#           |                        |                          |    compra.            |
#           +------------------------+--------------------------+-----------------------+
#
# --------------------------------------------------------------------------------------------------

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from .models import OrderItem, Order
from .forms import OrderCreateForm
from django.core.mail import send_mail
from cart.cart import Cart
from datetime import datetime, timedelta


def order_create(request):

    # Se crea el objeto Cart con la información recibida.
    cart = Cart(request)

    # Si la llamada es por método POST, es una creación de órden.
    if request.method == 'POST':

        # Se obtiene la información del formulario de la orden,
        # si la información es válida, se procede a crear la orden.
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])

            # Se limpia el carrito con ayuda del método clear()
            cart.clear()

            # Llamada al método para enviar el email.
            send(order.id, cart)
            return render(request, 'orders/order/created.html', {'cart': cart, 'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart,
                                                        'form': form})


def send(order_id, cart):
    # Se obtiene la información de la orden.
    order = Order.objects.get(id=order_id)

    # Se crea el subject del correo.
    subject = 'Order nr. {}'.format(order.id)

    # Se define el mensaje a enviar.
    message = 'Dear {},\n\nYou have successfully placed an order. Your order id is {}.\n\n\n'.format(
        order.first_name, order.id)
    message_part2 = 'Your order: \n\n'
    mesagges = []
    total = 0

    for item in cart:
        msg = str(item['quantity']) + 'x '+item['product'].get_name() + \
            '  $' + str(item['price']) + '\n'
        total += (item['total_price'])
        mesagges.append(msg)

    message_part3 = ' '.join(mesagges)
    message_part4 = '\n\n\n Total: $'+str(total)
    body = message + message_part2 + message_part3 + message_part4

    # Se envía el correo.
    send_mail(subject, body, 'pruebasjdangoframe@gmail.com',
              [order.email], fail_silently=False)


#Vista para desplegar las ordenes disponibles para cancelar antes de 24
class OrderList(ListView):
    model = Order
    template_name = 'order_list.html'

    def get_queryset(self):
        start_date = datetime.now()-timedelta(days=1)
        end_date = datetime.now()
        return Order.objects.filter(created__range=(start_date, end_date))

##Vista para renderizar el template de cancelar solo ordenes, solo por items
def cancel_order(request, id):
    order = Order.objects.get(id=id)
    order_items = OrderItem.objects.all().filter(order=id)
    context = {
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'orders/order/cancel.html', context=context)

##vista para eliminar una orden con todos sus items.
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    send_cancel(order.id)
    order.delete()
    return redirect('order_list')

##vista para eliminar una item perteneciente a una orden.
def delete_item(request, id):
    item = get_object_or_404(OrderItem, id=id)
    send_cancel_item(item.id)
    item.delete()
    return redirect('order_list')

##manda un email para la cancelacion de una orden
def send_cancel(order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.all().filter(order=order_id)

    subject = 'Order canceled nr. {}'.format(order.id)

    message = 'Dear {} {},\n\nYour order was canceled. Your order id is {}.\n\n\n'.format(
        order.first_name, order.last_name, order.id)
    message_part2 = 'Your order canceled: \n\n'
    messages = []

    for item in order_items:
        msg = str(item.quantity) + 'x '+item.product.name +'  $'+ str(item.price)+ '\n'
        messages.append(msg)

    message_part3 = ' '.join(messages)
    message_part4 = '\n\n\n Total: $'+str(order.get_total_cost())
    body = message + message_part2 + message_part3 + message_part4

    send_mail(subject, body, 'pruebasjdangoframe@gmail.com',
              [order.email], fail_silently=False)

##manda un email para la cancelacion de un item de una orden.
def send_cancel_item(item_id):
    item = OrderItem.objects.get(id=item_id)

    subject = 'Canceled otem nr. {}'.format(item.id)

    message = 'Dear {} {},\n\nYour item was canceled. Your item id is {}.\n\n\n'.format(
        item.order.first_name, item.order.last_name, item.id)
    message_part2 = 'Your item canceled: \n\n'

    message_part3 = item.product.name

    message_part4 = '\n\n\n Total: $' +str(item.get_cost())
    body = message + message_part2 + message_part3 + message_part4

    send_mail(subject, body, 'pruebasjdangoframe@gmail.com',
              [item.order.email], fail_silently=False)
