import logging
from decimal import Decimal
from django.conf import settings
from main.models import Product


logger = logging.getLogger(__name__)


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price),
                                     }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            logger.debug(f"Price: {item['price']}, Total Price: {item['total_price']}, Product: {item['product']}")
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]

def get_total_price(self):
    total = Decimal('0.00')
    product_ids = self.cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart = self.cart.copy()
    
    # Add product objects to cart items
    for product in products:
        cart[str(product.id)]['product'] = product

    for item in cart.values():
        try:
            price = Decimal(item['price'])
            quantity = item['quantity']
            product = item.get('product')
            
            if product and hasattr(product, 'discount'):
                discount = Decimal(product.discount) / Decimal('100')
                price_after_discount = price - (price * discount)
            else:
                price_after_discount = price
            
            item_total = price_after_discount * quantity
            total += item_total
            
            logger.debug(f"Item: price={price}, quantity={quantity}, total={item_total}, product={product}")
        except KeyError as e:
            logger.error(f"KeyError in cart item: {e}. Item data: {item}")
        except Exception as e:
            logger.error(f"Unexpected error processing cart item: {e}. Item data: {item}")
    
    return format(total, '.2f')