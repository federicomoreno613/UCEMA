import pandas as pd
import datetime
import numpy as np


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
    reviews_df['es_una_estrella']= reviews_df['review_score'].apply(es_cinco_estrellas)

    reviews_df['es_una_estrella']= reviews_df['review_score'].apply(es_una_estrella)

    reviews_df = reviews_df[['order_id', 'es_cinco_estrellas', 'es_una_estrella', 'review_score']]

    return reviews_df
#-----------------------------------------------------------------------------------------------------------------------

