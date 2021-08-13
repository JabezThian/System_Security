import string, random


def new_pass(size=8, chars = string.ascii_letters + string.digits):
    print('For Programmer: INFORMATION --> New Password has been created!')
    return ''.join(random.choice(chars) for _ in range(size))

def new_code(size=6, chars = string.ascii_letters + string.digits):
    print('For Programmer: INFORMATION --> New Password has been created!')
    return ''.join(random.choice(chars) for _ in range(size))
