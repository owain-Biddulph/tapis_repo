import random as rand
from flask import Flask, render_template
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from tapis_table import Transactions, Base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tapis_create_db.db'

engine = create_engine('sqlite:///tapis_create_db.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


class Magasin:
    """
    carpet and fitted_carpet must be a list of prices
    """

    def __init__(self, name, balance, carpet=None, fitted_carpet=None):
        self.name = name
        self.balance = balance
        if carpet is None:
            self.carpet = []
        else:
            carpet_list = []
            for price in carpet:
                nmbr = Carpet.nmbr_carpet + 1
                name = 'carpet_{}'.format(nmbr)
                carpet_list.append(Carpet(name, price, self))
                self.carpet = carpet_list
        if fitted_carpet is None:
            self.fitted_carpet = []
        else:
            fitted_carpet_list = []
            for price in fitted_carpet:
                quantity = rand.randint(100, 200)
                nmbr = Fitted_carpet.nmbr_fitted_carpet + 1
                name = 'fitted_carpet_{}'.format(nmbr)
                fitted_carpet_list.append(Fitted_carpet(
                    name, price, self, quantity))
                self.fitted_carpet = fitted_carpet_list

    def __repr__(self):
        return self.name


class Product:
    """Available products in the shops"""

    def __init__(self, name, price, owner):
        self.name = name
        self.price = price
        self.owner = owner


class Carpet(Product):

    nmbr_carpet = 0

    def __init__(self, name, price, owner):
        super().__init__(name, price, owner)
        Carpet.nmbr_carpet += 1

    def __repr__(self):
        # return "carpet('{}','{}')".format(self.owner, self.price)
        return '{}'.format(self.name)


class Fitted_carpet(Product):

    nmbr_fitted_carpet = 0

    def __init__(self, name, price, owner, quantity):
        super().__init__(name, price, owner)
        self.quantity = quantity
        Fitted_carpet.nmbr_fitted_carpet += 1

    def __repr__(self):
        return '{}'.format(self.name)


class Client:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def __repr__(self):
        return '{}'.format(self.name)


class Transaction:

    def __init__(self, product, buyer, seller, time, quantity=None):
        self.product = product
        self.buyer = buyer
        self.seller = seller
        self.time = time
        self.quantity = quantity

    def sale(self, quantity=None):
        if quantity is None:
            self.seller.balance += self.product.price
            self.buyer.balance -= self.product.price
        else:
            self.seller.balance += self.product.price * self.product.quantity
            self.buyer.balance -= self.product.price * self.product.quantity
            self.quantity -= quantity

        self.owner = self.buyer


mgs_1 = Magasin(
    'La caverne des tapis', 5000, [
        rand.randint(
            50, 2000) for _ in range(20)], [
                rand.randint(
                    10, 20) for _ in range(10)])
mgs_2 = Magasin(
    'carpet R\'us', 3000, [
        rand.randint(
            50, 2000) for _ in range(20)], [
                rand.randint(
                    10, 20) for _ in range(10)])


client_list = []
for x in range(1, 10001):
    name = 'Client_{}'.format(x)
    client_list.append(Client(name, rand.randint(70, 1500)))

# simulation


def product_determination(client_balance, stock_list, client, quantity=None):
    price_dif = 100000
    if isinstance(stock_list[0], Carpet):
        for el in stock_list:
            if 0 <= client_balance - el.price < price_dif:
                product = el
                price_dif = client_balance - el.price
    else:
        for el in stock_list:
            if 0 <= client_balance - el.price * quantity < price_dif:
                product = el
                price_dif = client_balance - el.price

    try:
        return product
    except UnboundLocalError:
        if stock_list == []:
            print('Il n\'y a plus de tapis à vendre !')
        else:
            print(
                'Le client {} n\'a pas assez d\'argent pour acheter un tapis !'.format(clt))
        return True


transactions_list = []

for clt in client_list:
    buy = rand.randint(0, 730)
    if buy == 0 or buy == 1:
        if buy == 0:
            type_de_produit = 'carpet'
            product = product_determination(
                clt.balance, mgs_1.carpet + mgs_2.carpet, clt)
            if product is True:
                continue
            hour = '{}h{}'.format(rand.randint(10, 18), rand.randint(1, 61))
            transaction = Transaction(product, clt, product.owner, hour)
            transactions_list.append(transaction)
            session.add(
                Transactions(
                    product=product.name,
                    buyer=clt.name,
                    seller=str(
                        product.owner),
                    time=hour))
            transaction.sale()
        if buy == 1:
            type_de_produit = 'fitted_carpet'
            quantity = rand.randint(10, 100)
            product = product_determination(
                clt.balance,
                mgs_1.fitted_carpet +
                mgs_2.fitted_carpet, clt,
                quantity)
            if product is True:
                continue
            hour = '{}h{}'.format(rand.randint(9, 18), rand.randint(1, 61))
            transaction = Transaction(
                product, clt, product.owner, hour, quantity)
            transactions_list.append(transaction)
            session.add(
                Transactions(
                    product=product.name,
                    buyer=clt.name,
                    seller=str(
                        product.owner),
                    time=hour,
                    quantity=quantity))
            transaction.sale(quantity)
print(len(transactions_list))
print(*transactions_list, sep='\n')


@app.route('/')
def index():
    return render_template(
        'show_all.html', Transactions=session.query(Transactions).all())


if __name__ == '__main__':
    app.run()
