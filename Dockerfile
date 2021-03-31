FROM hahaleyile/selenium_chrome_python

COPY main.py keywords.json cronfile /app/

WORKDIR /app

RUN \
    sed -i '/dotenv/d' /app/main.py && \
    sed -i '/binary_location/d' /app/main.py && \
    pip install redis requests WeChatEnterprise-hahaleyile && \
    crontab cronfile

CMD ["/usr/sbin/crond","-f"]