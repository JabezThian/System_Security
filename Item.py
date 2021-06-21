import shelve

# Key Reset
db = shelve.open('storage.db', 'c')
# db['Item_ID'] = 0
db.close()


class Item:
    db = shelve.open('storage.db', 'r')
    id = db['Item_ID']
    db.close()

    def __init__(self, name, price, have, bio, picture):
        Item.id += 1

        db = shelve.open('storage.db', 'c')
        db['Item_ID'] = Item.id
        db.close()

        self.__item_id = Item.id
        self.__item_name = name
        self.__item_price = price
        self.__item_have = have
        self.__item_want = 0
        self.__item_bio = bio
        self.__item_picture = picture
        self.__item_tag = list()

    def get_item_id(self):
        return self.__item_id

    def set_item_id(self, id):
        self.__item_id = id

    def get_item_name(self):
        return self.__item_name

    def set_item_name(self, name):
        self.__item_name = name

    def get_item_price(self):
        return self.__item_price

    def set_item_price(self, price):
        self.__item_price = price

    def get_item_have(self):
        return self.__item_have

    def set_item_have(self, have):
        self.__item_have = have

    def get_item_want(self):
        return self.__item_want

    def set_item_want(self, want):
        self.__item_want = want

    def get_item_bio(self):
        return self.__item_bio

    def set_item_bio(self, bio):
        self.__item_bio = bio

    def get_item_picture(self):
        return self.__item_picture

    def set_item_picture(self, picture):
        self.__item_picture = picture

    def get_item_tag(self):
        return self.__item_tag

    def set_item_tag(self, tag_list):
        self.__item_tag = tag_list

    def add_item_tag(self, tag):
        self.get_item_tag().append(tag)

    def remove_item_tag(self, tag):
        tag_list = []
        for old_tag in self.get_item_tag():
            if old_tag != tag:
                tag_list.append(old_tag)
        self.set_item_tag(tag_list)

    def get_total_price(self):
        return self.get_item_price() * self.get_item_want()


class Prescribed(Item):
    db = shelve.open('storage.db', 'r')
    id = db['Item_ID']
    db.close()

    def __init__(self, name, price, have, bio, picture):
        Prescribed.id += 1

        db = shelve.open('storage.db', 'c')
        db['Item_ID'] = Prescribed.id
        db.close()

        super().__init__(name, price, have, bio, picture)
        self.__item_dosage = ""

    def get_item_dosage(self):
        return self.__item_dosage

    def set_item_dosage(self, dosage):
        self.__item_dosage = dosage
