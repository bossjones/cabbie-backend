# scripts/change_recommend_code.py

from cabbie.apps.account.models import User, _issue_new_recommend_code

def run():
    for user in User.objects.all():
        old = user.recommend_code
        new = _issue_new_recommend_code()
        user.recommend_code = new 

        user.save(update_fields=['recommend_code'])

        print 'User{id} recommend code changed: "{old}"->"{new}"'.format(id=user.id, old=old, new=new)

