FROM sparrowdata/backend-base:1.1

## This should probably go in backend-base
RUN apk add --no-cache bash && pip3 install --upgrade pip

COPY ./requirements.txt /install/requirements.txt
RUN pip3 install --no-cache-dir -r /install/requirements.txt

WORKDIR /tests

## Copy API testing data (this could maybe go elsewhere)
COPY ./*.py /tests

CMD echo
