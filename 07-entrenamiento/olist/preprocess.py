import pandas as pd
import datetime

def transformar_columnas_datetime(orders_df):
    date_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                    'order_delivered_customer_date', 'order_estimated_delivery_date']
    for i in date_columns:
        orders_df[i] = pd.to_datetime(orders_df[i])
    return orders_df


def tiempo_de_espera(orders_df, is_delivered=True):
    one_day_delta = datetime.timedelta(days=1)  # también se puede hacer de esta manera
    if is_delivered:
        orders_df = orders_df[orders_df['order_status'] == "delivered"]

    orders_df['tiempo_de_espera'] = (orders_df['order_delivered_customer_date'] - orders_df[
            'order_purchase_timestamp']) / one_day_delta
    return orders_df


def real_vs_esperado(orders_df, is_delivered=True):
    one_day_delta = datetime.timedelta(days=1)
    if is_delivered:
        orders_df = orders_df[orders_df['order_status'] == "delivered"]

    orders_df['real_vs_esperado'] = (orders_df['order_delivered_customer_date'] - orders_df['order_estimated_delivery_date'])/ one_day_delta

    for i in orders_df['real_vs_esperado']:
        if i < 0:
            orders_df['real_vs_esperado'] = orders_df['real_vs_esperado'].replace(i, 0.00)

    return orders_df
#-----------------------------------------------------------------------------------------------------------------------
import numpy as np
def es_cinco_estrellas_alt(reviews_df):
    reviews_df['es_cinco_estrellas']= np.where(reviews_df['review_score'] == 5, 1, 0)

def es_cinco_estrellas(x):
    if x == 5:
        return 1
    else:
        return 0

def es_una_estrella(x):
    if x == 1:
        return 1
    else:
        return 0

def puntaje_de_compra(reviews_df):
    #es_cinco_estrellas_alt(reviews_df) si hubiera hehco la otra forma se usaba asi
    reviews_df['es_cinco_estrellas']= reviews_df['review_score'].apply(es_cinco_estrellas)

    reviews_df['es_una_estrella']= reviews_df['review_score'].apply(es_una_estrella)

    reviews_df = reviews_df[['order_id', 'es_cinco_estrellas', 'es_una_estrella', 'review_score']]

    return reviews_df
#-----------------------------------------------------------------------------------------------------------------------
def calcular_numero_productos(items_df):
    items_df = (items_df.groupby('order_id').agg( number_of_products = ('product_id','count'))).reset_index()
    return items_df

#-----------------------------------------------------------------------------------------------------------------------
def vendedores_unicos(items_df):
    items_df = (items_df.groupby('order_id').agg(vendedores_unicos =('product_id', 'count'))).reset_index()
    return items_df
#-----------------------------------------------------------------------------------------------------------------------
def calcular_precio_y_transporte(items_df):
    items_df = items_df.groupby('order_id', as_index = False).agg(precio = ('price', 'mean'), transporte = ('freight_value', 'mean'))
    return items_df

#-----------------------------------------------------------------------------------------------------------------------
def calcular_distancia_vendedor_comprador(data):


from math import radians, sin, cos, asin, sqrt
def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Computa distancia entre dos pares (lat, lng)
    Ver - (https://en.wikipedia.org/wiki/Haversine_formula)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))