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
'''def calcular_distancia_vendedor_comprador(data):


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
    return 2 * 6371 * asin(sqrt(a))'''

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

def calcular_distancia_vendedor_comprador(data):
    """ Calcula la distancia entre el vendedor y el comprador
    """
    orders = data['orders']
    order_items = data['order_items']
    sellers = data['sellers']
    customers = data['customers']

    #usar el dataset de geolocalizacion
    # Un zip code puede tener varias lat y lon. groupby puede ser usado con el metodo .first() para quedarte con el primero
    geo = data['geolocation']
    geo = geo.groupby('geolocation_zip_code_prefix',
                      as_index=False).first()

    # Solo usar columnas 'seller_id', 'seller_zip_code_prefix', 'geolocation_lat', 'geolocation_lng'
    sellers_mask_columns = [
        'seller_id', 'seller_zip_code_prefix', 'geolocation_lat', 'geolocation_lng'
    ]

    # mergear vendedores con geolocalizacion
    sellers_geo = sellers.merge(
        geo,
        how='left',
        left_on='seller_zip_code_prefix',
        right_on='geolocation_zip_code_prefix')[sellers_mask_columns]

    # Mergear con compradores
    customers_mask_columns = ['customer_id', 'customer_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']

    customers_geo = customers.merge(
        geo,
        how='left',
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix')[customers_mask_columns]

    # Mergear en otra tabla compradores y vendedores
    customers_sellers = customers.merge(orders, on='customer_id') \
        .merge(order_items, on='order_id') \
        .merge(sellers, on='seller_id') \
        [['order_id', 'customer_id', 'customer_zip_code_prefix', 'seller_id', 'seller_zip_code_prefix']]

    # Mergear con geolocalizacion de compradores
    matching_geo = customers_sellers.merge(sellers_geo,
                                           on='seller_id') \
        .merge(customers_geo,
               on='customer_id',
               suffixes=('_seller',
                         '_customer'))
    # Remover  na()
    matching_geo = matching_geo.dropna()

    matching_geo.loc[:, 'distance_seller_customer'] = \
        matching_geo.apply(lambda row:
                           haversine_distance(row['geolocation_lng_seller'],
                                              row['geolocation_lat_seller'],
                                              row['geolocation_lng_customer'],
                                              row['geolocation_lat_customer']),
                           axis=1)
    # Una orden puede tener muchos compradores retorna el promedio
    order_distance = \
        matching_geo.groupby('order_id',
                             as_index=False).agg({'distance_seller_customer':
                                                      'mean'})

    return order_distance


def obtener_tablon_primario(data,
                            is_delivered=True,
                            with_calcular_distancia_vendedor_comprador=False):
    orders = data['orders']
    reviews = data['order_reviews']
    precio_y_transporte = calcular_precio_y_transporte(data)
    vendedores = vendedores_unicos(data)
    productos = calcular_numero_productos(data)
    reviews = puntaje_de_compra(reviews)
    orders = real_vs_esperado(orders, is_delivered=True)
    #merge all dataframes in tablon_primario
    tablon_primario = orders.merge(reviews, on='order_id') \
        .merge(precio_y_transporte, on='order_id') \
        .merge(vendedores, on='order_id') \
        .merge(productos, on='order_id')


    # calcular_distancia_vendedor_comprador
    if with_calcular_distancia_vendedor_comprador:
        tablon_primario = tablon_primario.merge(
            calcular_distancia_vendedor_comprador(data), on='order_id')

    return tablon_primario.dropna()