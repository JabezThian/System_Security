import shelve

db = shelve.open('storage.db', 'c')
paid_dict = db['Paid']
# item_dict = db['Items']
# for key in item_dict:
#     item = item_dict[key]
#     item.remove_item_tag('hot')
#     print(item.get_item_tag())
#
#
# db['Items'] = item_dict

for key in db['Cart']:
    print(key)

for key in db['Paid']:
    print(key)

print(db['CartID'])
print(db['PaidID'])
db.close()