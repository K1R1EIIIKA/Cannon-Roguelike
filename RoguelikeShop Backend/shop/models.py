from django.db import models

from authentication.models import User


class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название', null=False, blank=False)
    hex_code = models.CharField(max_length=9, verbose_name='HEX-код', null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'


class Rarity(models.Model):
    index = models.IntegerField(verbose_name='Индекс', default=0)
    name = models.CharField(max_length=50, verbose_name='Название')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name='Цвет')

    def __str__(self):
        return self.name + ' - ' + str(self.index)

    class Meta:
        verbose_name = 'Редкость'
        verbose_name_plural = 'Редкости'


class BaseItem(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE, verbose_name='Редкость')
    unity_id = models.IntegerField(verbose_name='ID в Unity', unique=True, null=True, blank=True)

    def __str__(self):
        return self.name + ' (' + self.rarity.name + ')' + ' - ' + str(self.price) + ' руб.'

    class Meta:
        abstract = True


class Item(BaseItem):
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Skin(BaseItem):
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name='Цвет')
    only_one = models.BooleanField(verbose_name='Только один', default=False)

    def __str__(self):
        return self.name + ' (' + self.color.name + ')' + ' - ' + str(self.price) + ' руб.'

    class Meta:
        verbose_name = 'Скин'
        verbose_name_plural = 'Скины'


class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Предмет')
    count = models.IntegerField(verbose_name='Количество', default=1)

    @property
    def price(self):
        return self.item.price * self.count

    def __str__(self):
        return str(self.count) + 'x ' + self.item.name

    class Meta:
        verbose_name = 'Предмет в корзине'
        verbose_name_plural = 'Предметы в корзине'


class CartSkin(models.Model):
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, verbose_name='Скин')
    count = models.IntegerField(verbose_name='Количество', default=1)

    @property
    def price(self):
        return self.skin.price * self.count

    def __str__(self):
        return str(self.count) + 'x ' + self.skin.name

    class Meta:
        verbose_name = 'Скин в корзине'
        verbose_name_plural = 'Скины в корзине'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    items = models.ManyToManyField(CartItem, verbose_name='Предметы', blank=True)
    skins = models.ManyToManyField(CartSkin, verbose_name='Скины', blank=True)
    is_active = models.BooleanField(verbose_name='Активна', default=True)

    @property
    def total_price(self):
        return sum([item.price for item in self.items.all()]) + sum([skin.price for skin in self.skins.all()])

    @property
    def items_count(self):
        return sum([item.count for item in self.items.all()]) + sum([skin.count for skin in self.skins.all()])

    def __str__(self):
        return 'Корзина №' + str(self.id) + ' (' + str(self.items_count) + ' товаров - ' + str(self.total_price) + ' руб.)'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    items = models.ManyToManyField(CartItem, verbose_name='Предметы')
    skins = models.ManyToManyField(CartSkin, verbose_name='Скины')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    @property
    def total_price(self):
        return sum([item.price for item in self.items.all()]) + sum([skin.price for skin in self.skins.all()])

    @property
    def items_count(self):
        return sum([item.count for item in self.items.all()]) + sum([skin.count for skin in self.skins.all()])

    def __str__(self):
        return 'Заказ №' + str(self.id) + ' (' + str(self.items.count()) + ' товаров - ' + str(self.total_price) + ' руб.)'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
