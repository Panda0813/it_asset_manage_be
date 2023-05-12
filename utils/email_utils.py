from django.core import mail
from django.core.mail import EmailMultiAlternatives
from it_asset_manage_be.settings import EMAIL_FROM

import os
import logging

logger = logging.getLogger('django')


def send_pwd_email(to):
    from_email = '{} <{}>'.format('资产盘点系统', 'itda@unisemicon.com')
    msg = EmailMultiAlternatives(
        subject='密码重置',
        body='testBody',
        from_email=from_email,
        to=to
    )
    h = '''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>资产盘点系统密码重置邮件</title>
            </head>
            <body>
            <p style="font-family: 'Arial Black'">您的新密码为：123456a?，登录后请及时修改密码。</p>
            <p>(<a href="http://%s/login">点击链接跳转至《资产盘点系统》</a>)</p>
            <p>   </p>
            <br>
            <br>
            <br>
            <br>
            <br>
            <br>
            <br>
            <p style="color:red">注意: 该邮件由系统发送，无需回复！</p>
            <p>——————————————————</p>
            <p>信息与设计自动化部(ITDA) </p>
            </body>
        </html>''' % ('172.21.12.111:51680',)
    msg.attach_alternative(content=h, mimetype="text/html")
    msg.send()
