from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, Product, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    data = request.data

    if 'products' not in data:
        return Response({'products': 'Обязательное поле'}, status=status.HTTP_400_BAD_REQUEST)
    products = data['products']
    if not isinstance(products, list):
        return Response(
            {'products': f'Должен быть type:list, но получено {type(products).__name__}'},
            status=status.HTTP_400_BAD_REQUEST)
    if not products:
        return Response({'products': 'Не пустое поле'}, status=status.HTTP_400_BAD_REQUEST)

    for item in products:
        quantity = item['quantity']
        if type(quantity) is not int:
            return Response(
                {'products': f'Количество должно быть числом(int)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quantity < 1:
            return Response(
                {'products': 'Количетсво товаров должно быть больше 0'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    try:
        order = Order.objects.create(
            firstname=data['firstname'],
            lastname=data['lastname'],
            phonenumber=data['phonenumber'],
            adress=data['address'],
                                )
        for item in products:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
            )

        return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)
    except KeyError as error:
        return Response({
            'error': f'Отсутствует обязательное поле {error.args[0]}'},
            status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)