# encoding: utf8

from datetime import datetime, timedelta
from cabbie.apps.notice.models import Notice

def run():
    TARGET_COUNT = 100
    
    for i in range(TARGET_COUNT): 
        title = u'테스트 공지사항 제목 {0}'.format(i)
        content = u'테스트 공지사항 내용 {0}'.format(i) 
        notice_type = Notice.TYPE_EVENT 
        visible_from = datetime.now()  
        new_until = visible_from + timedelta(days=7)
        notice = Notice(title=title, content=content, notice_type=notice_type, visible_from=visible_from, new_until=new_until)
        notice.save()
