"""
Stripe payment service functions
"""
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    """
    Создает продукт в Stripe

    Args:
        name: Название продукта
        description: Описание продукта

    Returns:
        dict: Данные созданного продукта
    """
    # Stripe ограничивает длину полей:
    # name - максимум 250 символов
    # description - максимум 500 символов
    product_name = name[:250] if name else "Курс"
    product_description = None

    if description:
        product_description = description[:500]

    product = stripe.Product.create(
        name=product_name,
        description=product_description
    )
    return product


def create_stripe_price(product_id, amount):
    """
    Создает цену для продукта в Stripe
    
    Args:
        product_id: ID продукта в Stripe
        amount: Сумма в рублях (будет конвертирована в копейки)
    
    Returns:
        dict: Данные созданной цены
    """
    # Конвертируем сумму в копейки (Stripe работает с минимальными единицами валюты)
    amount_in_cents = int(float(amount) * 100)
    
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount_in_cents,
        currency='rub'
    )
    return price


def create_stripe_session(price_id, success_url, cancel_url):
    """
    Создает сессию оплаты в Stripe
    
    Args:
        price_id: ID цены в Stripe
        success_url: URL для перенаправления после успешной оплаты
        cancel_url: URL для перенаправления при отмене оплаты
    
    Returns:
        dict: Данные созданной сессии (включая URL для оплаты)
    """
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def retrieve_stripe_session(session_id):
    """
    Получает информацию о сессии оплаты в Stripe
    
    Args:
        session_id: ID сессии в Stripe
    
    Returns:
        dict: Данные сессии (включая статус оплаты)
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session
