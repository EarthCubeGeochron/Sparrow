FROM python:3.8-alpine

COPY ./requirements.txt /install/requirements.txt
RUN pip3 install --no-cache-dir -r /install/requirements.txt

WORKDIR /test

## Copy API testing data (this could maybe go elsewhere)
COPY ./* /test/

CMD echo
